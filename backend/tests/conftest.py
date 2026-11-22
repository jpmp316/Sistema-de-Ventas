import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite+pysqlite:///:memory:",
)
test_database_url = make_url(TEST_DATABASE_URL)

if (
    not test_database_url.drivername.startswith("sqlite")
    or test_database_url.database not in (None, "", ":memory:")
):
    raise RuntimeError(
        "Las pruebas solo pueden usar SQLite en memoria. "
        "Configura TEST_DATABASE_URL=sqlite+pysqlite:///:memory:."
    )

# Make any un-overridden SessionLocal safe too, before importing the app.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["SECRET_KEY"] = "test-only-secret-key-never-use-outside-tests"

from core.database import Base, get_db  # noqa: E402
from main import app  # noqa: E402
from models.role import Role  # noqa: E402


@pytest.fixture
def test_session_factory():
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    @event.listens_for(test_engine, "connect")
    def enable_foreign_keys(connection, _record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=test_engine)
    test_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )
    with test_session_local() as db:
        db.add_all([Role(name="admin"), Role(name="vendedor")])
        db.commit()

    try:
        yield test_session_local
    finally:
        test_engine.dispose()


@pytest.fixture
def client(test_session_factory):
    def override_get_db():
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def user_data():
    unique_value = uuid.uuid4().hex[:10]
    return {
        "username": f"user_{unique_value}",
        "password": "Password123!",
    }


@pytest.fixture
def authenticated_client(client, user_data):
    create_response = client.post("/auth/bootstrap-admin", json=user_data)

    assert create_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    category_response = client.post("/categories/", json={"name": "Pruebas"})
    assert category_response.status_code == 201
    return client

@pytest.fixture
def product_factory(authenticated_client):
    """Create through the public API and fail at setup if creation fails."""
    def create(**overrides):
        code = overrides.get("code", f"TEST-{uuid.uuid4().hex[:8]}")
        payload = {
            "name": f"Producto {code}", "code": code, "category_id": 1,
            "price_cents": 1250, "stock": 10, "min_stock": 1,
            **overrides,
        }
        response = authenticated_client.post("/products/", json=payload)
        assert response.status_code == 201, response.text
        return response.json()
    return create
