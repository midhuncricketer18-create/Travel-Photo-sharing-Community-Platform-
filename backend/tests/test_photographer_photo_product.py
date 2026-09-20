from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.core.database import Base
from app.core.dependencies import get_db_session
from app.main import app


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


def create_account(email: str, role: str) -> dict[str, str]:
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "strong-password", "role": role},
    )
    assert response.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "strong-password"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def create_photographer(email: str = "photographer@example.com") -> dict[str, str]:
    headers = create_account(email, "PHOTOGRAPHER")
    response = client.post(
        "/photographers/profile",
        json={"display_name": "Nature Photographer", "bio": "Outdoor photography"},
        headers=headers,
    )
    assert response.status_code == 201
    return headers


def create_photo(headers: dict[str, str], status: str = "PUBLISHED") -> int:
    response = client.post(
        "/photos",
        json={
            "title": "Mountain Sunrise",
            "description": "A sunrise over the mountains",
            "image_url": "https://example.com/mountain.jpg",
            "category": "Landscape",
            "status": status,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_product(headers: dict[str, str], photo_id: int) -> int:
    response = client.post(
        "/products",
        json={
            "photo_id": photo_id,
            "name": "Medium Print",
            "size": "12x18",
            "material": "Matte paper",
            "price": "25.00",
            "stock": 10,
            "status": "AVAILABLE",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_photographer_profile_create_retrieve_and_update() -> None:
    headers = create_account("profile@example.com", "PHOTOGRAPHER")

    created = client.post(
        "/photographers/profile",
        json={"display_name": "Original Name", "bio": "Original bio"},
        headers=headers,
    )
    retrieved = client.get("/photographers/profile", headers=headers)
    updated = client.put(
        "/photographers/profile",
        json={"display_name": "Updated Name"},
        headers=headers,
    )

    assert created.status_code == 201
    assert retrieved.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Updated Name"


def test_profile_is_photographer_only() -> None:
    customer_headers = create_account("customer@example.com", "CUSTOMER")

    response = client.post(
        "/photographers/profile",
        json={"display_name": "Not Allowed"},
        headers=customer_headers,
    )

    assert response.status_code == 403


def test_photo_crud_and_ownership_protection() -> None:
    owner_headers = create_photographer("owner@example.com")
    other_headers = create_photographer("other@example.com")
    customer_headers = create_account("photo-viewer@example.com", "CUSTOMER")
    photo_id = create_photo(owner_headers, "DRAFT")

    mine = client.get("/photos/mine", headers=owner_headers)
    updated = client.put(
        f"/photos/{photo_id}",
        json={"title": "Updated Sunrise", "status": "PUBLISHED"},
        headers=owner_headers,
    )
    forbidden_update = client.put(
        f"/photos/{photo_id}",
        json={"title": "Stolen Update"},
        headers=other_headers,
    )
    deleted = client.delete(f"/photos/{photo_id}", headers=owner_headers)
    missing = client.get(f"/photos/{photo_id}", headers=customer_headers)

    assert mine.status_code == 200
    assert len(mine.json()) == 1
    assert updated.status_code == 200
    assert forbidden_update.status_code == 403
    assert deleted.status_code == 204
    assert missing.status_code == 404


def test_anyone_browses_published_photos_only() -> None:
    photographer_headers = create_photographer()
    published_id = create_photo(photographer_headers, "PUBLISHED")
    draft_id = create_photo(photographer_headers, "DRAFT")

    listing = client.get("/photos")
    published_detail = client.get(f"/photos/{published_id}")
    draft_detail = client.get(f"/photos/{draft_id}")

    assert listing.status_code == 200
    assert [photo["id"] for photo in listing.json()] == [published_id]
    assert published_detail.status_code == 200
    assert draft_detail.status_code == 404


def test_product_crud_and_ownership_protection() -> None:
    owner_headers = create_photographer("product-owner@example.com")
    other_headers = create_photographer("product-other@example.com")
    photo_id = create_photo(owner_headers, "PUBLISHED")
    product_id = create_product(owner_headers, photo_id)

    mine = client.get("/products/mine", headers=owner_headers)
    updated = client.put(
        f"/products/{product_id}",
        json={"price": "30.00", "stock": 8},
        headers=owner_headers,
    )
    forbidden_update = client.put(
        f"/products/{product_id}",
        json={"price": "1.00"},
        headers=other_headers,
    )
    deleted = client.delete(f"/products/{product_id}", headers=owner_headers)

    assert mine.status_code == 200
    assert len(mine.json()) == 1
    assert updated.status_code == 200
    assert updated.json()["price"] == "30.00"
    assert forbidden_update.status_code == 403
    assert deleted.status_code == 204


def test_anyone_browses_available_products_only() -> None:
    photographer_headers = create_photographer("available@example.com")
    photo_id = create_photo(photographer_headers, "PUBLISHED")
    product_id = create_product(photographer_headers, photo_id)

    listing = client.get("/products")
    detail = client.get(f"/products/{product_id}")

    assert listing.status_code == 200
    assert listing.json()[0]["id"] == product_id
    assert detail.status_code == 200


def test_product_validation_and_invalid_photo() -> None:
    headers = create_photographer("validation@example.com")
    invalid_photo = client.post(
        "/products",
        json={
            "photo_id": 999,
            "name": "Print",
            "size": "Small",
            "material": "Paper",
            "price": "10.00",
            "stock": 1,
        },
        headers=headers,
    )
    invalid_price = client.post(
        "/products",
        json={
            "photo_id": 999,
            "name": "Print",
            "size": "Small",
            "material": "Paper",
            "price": "0",
            "stock": 1,
        },
        headers=headers,
    )
    invalid_stock = client.post(
        "/products",
        json={
            "photo_id": 999,
            "name": "Print",
            "size": "Small",
            "material": "Paper",
            "price": "10.00",
            "stock": -1,
        },
        headers=headers,
    )

    assert invalid_photo.status_code == 404
    assert invalid_price.status_code == 422
    assert invalid_stock.status_code == 422


def test_public_photo_and_product_reads_preserve_protected_writes() -> None:
    assert client.get("/photos").status_code == 200
    assert client.get("/products").status_code == 200
    assert client.post("/photos", json={}).status_code == 401
    assert client.post("/products", json={}).status_code == 401