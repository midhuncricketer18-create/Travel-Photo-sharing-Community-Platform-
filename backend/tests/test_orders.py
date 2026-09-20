from collections.abc import Generator
from decimal import Decimal
from itertools import count

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.core.database import Base
from app.core.dependencies import get_db_session
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
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
email_counter = count()


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


def make_user(role: UserRole) -> tuple[User, dict[str, str]]:
    email = f"user-{next(email_counter)}@example.com"
    with TestingSessionLocal() as db:
        user = User(email=email, hashed_password=hash_password("password"), role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id
    token = create_access_token(str(user_id), role.value)
    return user, {"Authorization": f"Bearer {token}"}


def make_photographer() -> tuple[User, dict[str, str], Photographer]:
    user, headers = make_user(UserRole.PHOTOGRAPHER)
    with TestingSessionLocal() as db:
        profile = Photographer(user_id=user.id, display_name=f"Photographer {user.id}")
        db.add(profile)
        db.commit()
        db.refresh(profile)
        profile_id = profile.id
    return user, headers, Photographer(id=profile_id, user_id=user.id, display_name="")


def make_product(
    photographer: User,
    *,
    price: str = "12.50",
    stock: int = 5,
    photo_status: PhotoStatus = PhotoStatus.PUBLISHED,
    product_status: ProductStatus = ProductStatus.AVAILABLE,
) -> int:
    with TestingSessionLocal() as db:
        profile = db.scalar(select(Photographer).where(Photographer.user_id == photographer.id))
        photo = Photo(
            photographer_id=profile.id,
            title=f"Photo {photographer.id}",
            image_url="https://example.com/photo.jpg",
            status=photo_status,
        )
        db.add(photo)
        db.flush()
        product = Product(
            photo_id=photo.id,
            name="Print",
            size="12x18",
            material="Paper",
            price=Decimal(price),
            stock=stock,
            status=product_status,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product.id


def add_to_cart(headers: dict[str, str], product_id: int, quantity: int = 1) -> None:
    response = client.post(
        "/cart/items",
        json={"product_id": product_id, "quantity": quantity},
        headers=headers,
    )
    assert response.status_code == 201


def product_state(product_id: int) -> tuple[Decimal, int]:
    with TestingSessionLocal() as db:
        product = db.get(Product, product_id)
        return product.price, product.stock


def test_successful_order_calculates_total_snapshots_prices_reduces_stock_and_clears_cart() -> None:
    customer, customer_headers = make_user(UserRole.CUSTOMER)
    photographer, _, _ = make_photographer()
    first_product = make_product(photographer, price="12.50", stock=5)
    second_product = make_product(photographer, price="20.00", stock=5)
    add_to_cart(customer_headers, first_product, 2)
    add_to_cart(customer_headers, second_product, 1)

    response = client.post("/orders", headers=customer_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["customer_id"] == customer.id
    assert body["status"] == "PENDING"
    assert body["total_amount"] == "45.00"
    assert {item["quantity"] for item in body["items"]} == {1, 2}
    assert {item["unit_price"] for item in body["items"]} == {"12.50", "20.00"}
    assert product_state(first_product)[1] == 3
    assert product_state(second_product)[1] == 4
    assert client.get("/cart", headers=customer_headers).json()["items"] == []


def test_order_item_keeps_purchase_price_snapshot() -> None:
    _, customer_headers = make_user(UserRole.CUSTOMER)
    photographer, _, _ = make_photographer()
    product_id = make_product(photographer, price="15.00")
    add_to_cart(customer_headers, product_id)

    order = client.post("/orders", headers=customer_headers).json()
    with TestingSessionLocal() as db:
        db.get(Product, product_id).price = Decimal("99.00")
        db.commit()
        item = db.scalar(select(OrderItem).where(OrderItem.order_id == order["id"]))

    assert item.unit_price == Decimal("15.00")


def test_empty_cart_is_rejected() -> None:
    _, headers = make_user(UserRole.CUSTOMER)
    assert client.get("/cart", headers=headers).status_code == 200

    response = client.post("/orders", headers=headers)

    assert response.status_code == 400


def test_insufficient_stock_and_unavailable_product_leave_cart_unchanged() -> None:
    customer, customer_headers = make_user(UserRole.CUSTOMER)
    photographer, _, _ = make_photographer()
    product_id = make_product(photographer, stock=1)
    add_to_cart(customer_headers, product_id)
    with TestingSessionLocal() as db:
        db.get(Product, product_id).stock = 0
        db.commit()

    insufficient = client.post("/orders", headers=customer_headers)

    assert insufficient.status_code == 400
    with TestingSessionLocal() as db:
        assert db.scalar(select(Order).where(Order.customer_id == customer.id)) is None
        assert db.scalar(select(CartItem).join(Cart).where(Cart.user_id == customer.id)) is not None

    unavailable_id = make_product(photographer, product_status=ProductStatus.UNAVAILABLE)
    with TestingSessionLocal() as db:
        cart = db.scalar(select(Cart).where(Cart.user_id == customer.id))
        db.add(CartItem(cart_id=cart.id, product_id=unavailable_id, quantity=1))
        db.commit()

    unavailable = client.post("/orders", headers=customer_headers)

    assert unavailable.status_code == 400


def test_unpublished_product_rolls_back_entire_order() -> None:
    customer, customer_headers = make_user(UserRole.CUSTOMER)
    photographer, _, _ = make_photographer()
    valid_id = make_product(photographer, stock=3)
    draft_id = make_product(photographer, photo_status=PhotoStatus.DRAFT, stock=3)
    with TestingSessionLocal() as db:
        cart = Cart(user_id=customer.id)
        db.add(cart)
        db.flush()
        db.add_all(
            [
                CartItem(cart_id=cart.id, product_id=valid_id, quantity=1),
                CartItem(cart_id=cart.id, product_id=draft_id, quantity=1),
            ]
        )
        db.commit()

    response = client.post("/orders", headers=customer_headers)

    assert response.status_code == 400
    assert product_state(valid_id)[1] == 3
    with TestingSessionLocal() as db:
        assert db.scalar(select(Order).where(Order.customer_id == customer.id)) is None
        assert len(db.scalars(select(CartItem).join(Cart).where(Cart.user_id == customer.id)).all()) == 2


def test_customer_can_view_only_own_orders() -> None:
    first_customer, first_headers = make_user(UserRole.CUSTOMER)
    second_customer, second_headers = make_user(UserRole.CUSTOMER)
    photographer, _, _ = make_photographer()
    product_id = make_product(photographer)
    add_to_cart(first_headers, product_id)
    order = client.post("/orders", headers=first_headers).json()

    own = client.get(f"/orders/{order['id']}", headers=first_headers)
    other = client.get(f"/orders/{order['id']}", headers=second_headers)
    listing = client.get("/orders", headers=first_headers)

    assert own.status_code == 200
    assert other.status_code == 404
    assert [item["id"] for item in listing.json()] == [order["id"]]
    assert first_customer.id != second_customer.id


def test_photographer_sees_only_orders_containing_own_products() -> None:
    customer, customer_headers = make_user(UserRole.CUSTOMER)
    _, first_headers, first_profile = make_photographer()
    _, second_headers, second_profile = make_photographer()
    first_product = make_product(User(id=first_profile.user_id), price="10.00")
    second_product = make_product(User(id=second_profile.user_id), price="20.00")
    add_to_cart(customer_headers, first_product)
    add_to_cart(customer_headers, second_product)
    order = client.post("/orders", headers=customer_headers)

    first_view = client.get("/orders/photographer", headers=first_headers)
    second_view = client.get("/orders/photographer", headers=second_headers)

    assert order.status_code == 201
    assert first_view.status_code == 200
    assert second_view.status_code == 200
    assert len(first_view.json()[0]["items"]) == 1
    assert len(second_view.json()[0]["items"]) == 1
    assert first_view.json()[0]["related_total"] == "10.00"
    assert second_view.json()[0]["related_total"] == "20.00"
    assert customer.id > 0


def test_customer_can_cancel_once_and_stock_is_restored() -> None:
    _, customer_headers = make_user(UserRole.CUSTOMER)
    photographer, _, _ = make_photographer()
    product_id = make_product(photographer, stock=5)
    add_to_cart(customer_headers, product_id, 2)
    order = client.post("/orders", headers=customer_headers).json()
    assert product_state(product_id)[1] == 3

    cancelled = client.post(f"/orders/{order['id']}/cancel", headers=customer_headers)
    repeated = client.post(f"/orders/{order['id']}/cancel", headers=customer_headers)

    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "CANCELLED"
    assert product_state(product_id)[1] == 5
    assert repeated.status_code == 400


def test_administrator_status_transition_and_invalid_transition() -> None:
    _, customer_headers = make_user(UserRole.CUSTOMER)
    _, admin_headers = make_user(UserRole.ADMINISTRATOR)
    photographer, _, _ = make_photographer()
    product_id = make_product(photographer)
    add_to_cart(customer_headers, product_id)
    order = client.post("/orders", headers=customer_headers).json()

    confirmed = client.patch(
        f"/orders/{order['id']}/status", json={"status": "CONFIRMED"}, headers=admin_headers
    )
    invalid = client.patch(
        f"/orders/{order['id']}/status", json={"status": "COMPLETED"}, headers=admin_headers
    )

    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "CONFIRMED"
    assert invalid.status_code == 400


def test_order_routes_reject_wrong_roles_and_unauthenticated_requests() -> None:
    _, photographer_headers, _ = make_photographer()
    _, admin_headers = make_user(UserRole.ADMINISTRATOR)

    assert client.post("/orders").status_code == 401
    assert client.get("/orders").status_code == 401
    assert client.post("/orders", headers=photographer_headers).status_code == 403
    assert client.get("/orders", headers=admin_headers).status_code == 403
    assert client.get("/orders/999", headers=photographer_headers).status_code == 403
    assert client.get("/orders/999", headers=admin_headers).status_code == 403