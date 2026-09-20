from collections.abc import Generator

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
from app.models.user import User, UserRole

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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


def make_headers(role: UserRole) -> dict[str, str]:
    with TestingSessionLocal() as db:
        user = User(email=f"{role.value.lower()}@example.com", hashed_password=hash_password("password"), role=role)
        db.add(user)
        db.commit()
        user_id = user.id
    return {"Authorization": f"Bearer {create_access_token(str(user_id), role.value)}"}


def test_administrator_can_list_users_and_customer_cannot() -> None:
    admin_headers = make_headers(UserRole.ADMINISTRATOR)
    customer_headers = make_headers(UserRole.CUSTOMER)

    assert client.get("/admin/users", headers=admin_headers).status_code == 200
    assert client.get("/admin/users", headers=customer_headers).status_code == 403
    assert len(client.get("/admin/users", headers=admin_headers).json()) == 2
