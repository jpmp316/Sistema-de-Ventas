from datetime import datetime, timezone
from decimal import Decimal

import pytest

from models.sales import Sale, InventoryMovement


def test_admin_can_list_edit_reset_and_delete_seller(authenticated_client):
    client = authenticated_client
    created = client.post("/users/", json={"username": "managed_seller", "password": "Password123!"})
    assert created.status_code == 201
    user = created.json()
    result = client.get("/users/paginated?page=1&page_size=10").json()
    assert any(row["id"] == user["id"] and row["role"] == "vendedor" for row in result["items"])
    edited = client.put(f"/users/{user['id']}", json={"username": "renamed_seller", "password": "ChangedPass123!"})
    assert edited.status_code == 200
    assert edited.json()["role"] == "vendedor"
    assert "hashed_password" not in edited.json()
    assert client.post("/auth/login", data={"username": "renamed_seller", "password": "ChangedPass123!"}).status_code == 200
    assert client.delete(f"/users/{user['id']}").status_code == 204
    assert client.get(f"/users/{user['id']}").status_code == 404


def test_admin_cannot_delete_current_account(authenticated_client):
    user = authenticated_client.get("/users/").json()["items"][0]
    assert authenticated_client.delete(f"/users/{user['id']}").status_code == 403
    assert authenticated_client.get(f"/users/{user['id']}").status_code == 200


@pytest.mark.parametrize("history", ["sale", "movement"])
def test_user_with_history_cannot_be_deleted(authenticated_client, test_session_factory, history):
    client = authenticated_client
    user = client.post("/users/", json={"username": "seller_history", "password": "Password123!"}).json()
    product = client.post("/products/", json={"name": "Producto historial", "code": "USER-HISTORY", "category_id": 1, "price_cents": 100, "stock": 0, "min_stock": 0}).json()
    with test_session_factory() as db:
        if history == "sale":
            db.add(Sale(user_id=user["id"], subtotal=Decimal("1.00"), total=Decimal("1.00"), date=datetime.now(timezone.utc), status="completed"))
        else:
            db.add(InventoryMovement(user_id=user["id"], product_id=product["id"], type="adjustment", quantity=1, previous_stock=0, resulting_stock=1))
        db.commit()
    assert client.delete(f"/users/{user['id']}").status_code == 409
    assert client.get(f"/users/{user['id']}").json()["username"] == "seller_history"
