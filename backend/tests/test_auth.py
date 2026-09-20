import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-that-is-not-used-in-production")

from collections.abc import Generator

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.api.auth import router as auth_router
from app.core.database import Base
from app.core.dependencies import (
    get_current_user,
    get_db_session,
    require_administrator,
    require_customer,
    require_photographer,
)
from app.core.security import decode_access_token, hash_password, verify_password
from app.models.user import User, UserRole


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


app = FastAPI()
app.include_router(auth_router)


@app.get("/customer-only")
def customer_only(_: User = Depends(require_customer)) -> dict[str, str]:
    return {"message": "customer access granted"}


@app.get("/photographer-only")
def photographer_only(_: User = Depends(require_photographer)) -> dict[str, str]:
    return {"message": "photographer access granted"}


@app.get("/administrator-only")
def administrator_only(_: User = Depends(require_administrator)) -> dict[str, str]:
    return {"message": "administrator access granted"}


app.dependency_overrides[get_db_session] = override_get_db
app.dependency_overrides[get_current_user] = get_current_user
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database() -> Generator[None, None, None]:
    Base.metadata.create_all(engine)
    with TestingSessionLocal() as db:
        db.query(User).delete()
        db.commit()
    yield
    Base.metadata.drop_all(engine)


def register(email: str = "customer@example.com", role: str = "CUSTOMER"):
    return client.post(
        "/auth/register",
        json={"email": email, "password": "strong-password", "role": role},
    )


def test_registration_hashes_password() -> None:
    response = register()

    assert response.status_code == 201
    with TestingSessionLocal() as db:
        user = db.query(User).one()
        assert user.hashed_password != "strong-password"
        assert verify_password("strong-password", user.hashed_password)


def test_duplicate_email_is_rejected() -> None:
    register()

    response = register()

    assert response.status_code == 409


def test_login_returns_and_validates_jwt() -> None:
    register()

    response = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "strong-password"},
    )

    assert response.status_code == 200
    token = response.json()["access_token"]
    claims = decode_access_token(token)
    assert claims["sub"] == "1"
    assert claims["role"] == UserRole.CUSTOMER.value


def test_invalid_password_is_rejected() -> None:
    register()

    response = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_protected_profile_requires_valid_token() -> None:
    register()
    unauthenticated = client.get("/auth/me")
    login = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "strong-password"},
    )
    authenticated = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert unauthenticated.status_code == 401
    assert authenticated.status_code == 200
    assert authenticated.json()["email"] == "customer@example.com"
    assert "hashed_password" not in authenticated.json()


def test_role_authorization_allows_only_matching_roles() -> None:
    register(role="CUSTOMER")
    customer_login = client.post(
        "/auth/login",
        json={"email": "customer@example.com", "password": "strong-password"},
    )
    customer_headers = {"Authorization": f"Bearer {customer_login.json()['access_token']}"}

    assert client.get("/customer-only", headers=customer_headers).status_code == 200
    assert client.get("/photographer-only", headers=customer_headers).status_code == 403
    assert client.get("/administrator-only", headers=customer_headers).status_code == 403


def test_photographer_registration_gets_photographer_role() -> None:
    response = register(role="PHOTOGRAPHER")

    assert response.status_code == 201
    assert response.json()["role"] == UserRole.PHOTOGRAPHER.value


def test_administrator_role_can_authorize_provisioned_user() -> None:
    with TestingSessionLocal() as db:
        admin = User(
            email="admin@example.com",
            hashed_password=hash_password("admin-password"),
            role=UserRole.ADMINISTRATOR,
        )
        db.add(admin)
        db.commit()

    response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "admin-password"},
    )
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    assert response.status_code == 200
    assert client.get("/administrator-only", headers=headers).status_code == 200
    assert client.get("/customer-only", headers=headers).status_code == 403