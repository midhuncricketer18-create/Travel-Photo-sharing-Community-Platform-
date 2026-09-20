from collections.abc import Generator
from decimal import Decimal
from itertools import count

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.core.database import Base
from app.core.dependencies import get_db_session
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.photo import Photo, PhotoStatus
from app.models.photographer import Photographer
from app.models.product import Product, ProductStatus
from app.models.user import User, UserRole


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
owner_counter = count()


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    app.dependency_overrides[get_db_session] = override_get_db
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    app.dependency_overrides.pop(get_db_session, None)


def make_user(email: str, role: UserRole) -> tuple[User, dict[str, str]]:
    with TestingSessionLocal() as db:
        user = User(email=email, hashed_password=hash_password("password"), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
    token = create_access_token(str(user_id), role.value)
    return user, {"Authorization": f"Bearer {token}"}


def make_product(
    *,
    photo_status: PhotoStatus = PhotoStatus.PUBLISHED,
    product_status: ProductStatus = ProductStatus.AVAILABLE,
    stock: int = 5,
) -> Product:
    with TestingSessionLocal() as db:
        owner_email = f"owner-{next(owner_counter)}@example.com"
        owner = User(
            email=owner_email,
            hashed_password=hash_password("password"),
            role=UserRole.PHOTOGRAPHER,
        )
        db.add(owner)
        db.flush()
        profile = Photographer(user_id=owner.id, display_name="Owner")
        db.add(profile)
        db.flush()
        photo = Photo(
            photographer_id=profile.id,
            title="Sunset",
            image_url="https://example.com/sunset.jpg",
            status=photo_status,
        )
        db.add(photo)
        db.flush()
        product = Product(
            photo_id=photo.id,
            name="Small Print",
            size="8x10",
            material="Paper",
            price=Decimal("12.50"),
            stock=stock,
            status=product_status,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product


def test_cart_is_created_and_retrieved_for_customer() -> None:
    _, headers = make_user("customer@example.com", UserRole.CUSTOMER)

    first = client.get("/cart", headers=headers)
    second = client.get("/cart", headers=headers)

    assert first.status_code == 200
    assert first.json()["items"] == []
    assert first.json()["total_amount"] == "0.00"
    assert first.json()["id"] == second.json()["id"]


def test_add_same_product_updates_quantity_and_totals() -> None:
    product = make_product(stock=5)
    _, headers = make_user("customer@example.com", UserRole.CUSTOMER)

    first = client.post(
        "/cart/items", json={"product_id": product.id, "quantity": 2}, headers=headers
    )
    second = client.post(
        "/cart/items", json={"product_id": product.id, "quantity": 1}, headers=headers
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert len(second.json()["items"]) == 1
    assert second.json()["items"][0]["quantity"] == 3
    assert second.json()["items"][0]["subtotal"] == "37.50"
    assert second.json()["total_amount"] == "37.50"


def test_update_and_remove_cart_item() -> None:
    product = make_product()
    _, headers = make_user("customer@example.com", UserRole.CUSTOMER)
    added = client.post(
        "/cart/items", json={"product_id": product.id, "quantity": 2}, headers=headers
    )
    item_id = added.json()["items"][0]["id"]

    updated = client.put(
        f"/cart/items/{item_id}", json={"quantity": 4}, headers=headers
    )
    removed = client.delete(f"/cart/items/{item_id}", headers=headers)
    cart = client.get("/cart", headers=headers)

    assert updated.status_code == 200
    assert updated.json()["items"][0]["quantity"] == 4
    assert removed.status_code == 204
    assert cart.json()["items"] == []


def test_cart_rejects_invalid_or_excess_quantity() -> None:
    product = make_product(stock=3)
    _, headers = make_user("customer@example.com", UserRole.CUSTOMER)

    invalid = client.post(
        "/cart/items", json={"product_id": product.id, "quantity": 0}, headers=headers
    )
    excessive = client.post(
        "/cart/items", json={"product_id": product.id, "quantity": 4}, headers=headers
    )

    assert invalid.status_code == 422
    assert excessive.status_code == 400


def test_cart_rejects_unavailable_and_unpublished_products() -> None:
    unavailable = make_product(product_status=ProductStatus.UNAVAILABLE)
    unpublished = make_product(photo_status=PhotoStatus.DRAFT)
    _, headers = make_user("customer@example.com", UserRole.CUSTOMER)

    unavailable_response = client.post(
        "/cart/items", json={"product_id": unavailable.id, "quantity": 1}, headers=headers
    )
    unpublished_response = client.post(
        "/cart/items", json={"product_id": unpublished.id, "quantity": 1}, headers=headers
    )

    assert unavailable_response.status_code == 400
    assert unpublished_response.status_code == 400


def test_customer_cart_data_is_isolated() -> None:
    product = make_product()
    _, first_headers = make_user("first@example.com", UserRole.CUSTOMER)
    _, second_headers = make_user("second@example.com", UserRole.CUSTOMER)
    added = client.post(
        "/cart/items", json={"product_id": product.id, "quantity": 1}, headers=first_headers
    )
    item_id = added.json()["items"][0]["id"]

    second_cart = client.get("/cart", headers=second_headers)
    second_update = client.put(
        f"/cart/items/{item_id}", json={"quantity": 2}, headers=second_headers
    )

    assert second_cart.status_code == 200
    assert second_cart.json()["items"] == []
    assert second_update.status_code == 404


def test_cart_requires_customer_role() -> None:
    _, photographer_headers = make_user("photographer@example.com", UserRole.PHOTOGRAPHER)
    _, admin_headers = make_user("admin@example.com", UserRole.ADMINISTRATOR)

    assert client.get("/cart", headers=photographer_headers).status_code == 403
    assert client.get("/cart", headers=admin_headers).status_code == 403


def test_cart_requires_authentication() -> None:
    assert client.get("/cart").status_code == 401
    assert client.get("/cart/items").status_code == 401
    assert client.post("/cart/items", json={"product_id": 1, "quantity": 1}).status_code == 401