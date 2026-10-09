import uuid

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def user_data():
    unique_value = uuid.uuid4().hex[:10]
    return {
        "username": f"user_{unique_value}",
        "password": "Password123",
    }


@pytest.fixture
def authenticated_client(client, user_data):
    create_response = client.post("/users/", json=user_data)

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
    yield client

    created_user = create_response.json()
    user_id = created_user["id"]
    client.delete(f"/users/{user_id}")