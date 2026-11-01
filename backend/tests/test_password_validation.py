import pytest
from pydantic import ValidationError

from schemas.user_schemas import UserCreate, UserUpdate


@pytest.mark.parametrize("password", [
    "Abc123!", "lowercase123!", "UPPERCASE123!", "NoDigitsHere!",
    "NoSymbols1234", "Ab1!" + "x" * 125,
])
def test_password_policy_applies_to_creation_and_update(password):
    with pytest.raises(ValidationError):
        UserCreate(username="usuario", password=password)
    with pytest.raises(ValidationError):
        UserUpdate(password=password)


@pytest.mark.parametrize("method,path", [
    ("post", "/users/"), ("post", "/auth/bootstrap-admin"), ("put", "/users/1"),
])
def test_api_rejects_weak_password_without_creating_or_modifying_user(authenticated_client, method, path):
    before = authenticated_client.get("/users/").json()
    response = authenticated_client.request(method, path, json={"username": "otro_usuario", "password": "weak"})
    assert response.status_code == 422
    assert authenticated_client.get("/users/").json() == before


def test_secure_password_update_preserves_spaces_and_hashes_password(authenticated_client):
    password = "  StrongPass123!  "
    created = authenticated_client.post("/users/", json={"username": "secure_seller", "password": password})
    assert created.status_code == 201
    assert "password" not in created.json()
    assert "hashed_password" not in created.json()
    assert authenticated_client.post("/auth/login", data={"username": "secure_seller", "password": password}).status_code == 200
    assert authenticated_client.post("/auth/login", data={"username": "secure_seller", "password": password.strip()}).status_code == 401
    updated = authenticated_client.put(f"/users/{created.json()['id']}", json={"password": "AnotherStrong123!"})
    assert updated.status_code == 200
    assert authenticated_client.post("/auth/login", data={"username": "secure_seller", "password": password}).status_code == 401
    assert authenticated_client.post("/auth/login", data={"username": "secure_seller", "password": "AnotherStrong123!"}).status_code == 200
