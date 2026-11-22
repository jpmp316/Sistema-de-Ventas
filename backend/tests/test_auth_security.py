from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from auth.auth_handler import SECRET_KEY, ALGORITHM
from auth.auth_service import verificar_password
from models.user import User


@pytest.mark.parametrize("claims", [
    {"sub": "missing-user", "jti": "test"},
    {"jti": "test"},
    {"sub": "missing-user"},
    {"sub": "missing-user", "jti": "test", "exp": 1},
])
def test_invalid_claims_cannot_access_protected_routes(client, claims):
    payload = {"exp": datetime.now(timezone.utc) + timedelta(minutes=5), **claims}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get("/products/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("token", ["not-a-jwt", jwt.encode({"sub": "admin"}, "another-key", algorithm="HS256")])
def test_malformed_or_wrong_signature_is_rejected(client, token):
    assert client.get("/products/", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_logout_revokes_only_current_token(authenticated_client, user_data):
    client = authenticated_client
    first = client.headers["Authorization"]
    other = client.post("/auth/login", data=user_data).json()["access_token"]
    assert client.post("/auth/logout").status_code == 204
    assert client.get("/products/", headers={"Authorization": first}).status_code == 401
    assert client.get("/products/", headers={"Authorization": f"Bearer {other}"}).status_code == 200
    assert client.post("/auth/logout").status_code == 401


def test_password_is_hashed_and_not_exposed(authenticated_client, test_session_factory, user_data):
    with test_session_factory() as db:
        user = db.query(User).filter_by(username=user_data["username"]).one()
        assert user.hashed_password != user_data["password"]
        assert verificar_password(user_data["password"], user.hashed_password)
    for row in authenticated_client.get("/users/").json()["items"]:
        assert "hashed_password" not in row
        assert "password" not in row


def test_bootstrap_requires_admin_after_first_account(client, user_data):
    assert client.post("/auth/bootstrap-admin", json=user_data).status_code == 201
    assert client.post("/auth/bootstrap-admin", json={**user_data, "username": "other_admin"}).status_code == 403
