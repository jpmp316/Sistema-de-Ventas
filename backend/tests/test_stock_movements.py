import pytest
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError

from models.sales import InventoryMovement


def create_product(client, stock=10, code="MOVEMENT-001"):
    response = client.post("/products/", json={
        "name": f"Producto {code}", "code": code, "category_id": 1,
        "price_cents": 1000, "stock": stock, "min_stock": 0,
    })
    assert response.status_code == 201, response.text
    return response.json()


def test_initial_stock_creates_entry_with_responsible(authenticated_client, user_data):
    product = create_product(authenticated_client)
    response = authenticated_client.get("/inventory/movements?type=entry")
    assert response.status_code == 200
    movement, = response.json()["items"]
    assert movement["product_id"] == product["id"]
    assert movement["username"] == user_data["username"]
    assert movement["previous_stock"] == 0
    assert movement["resulting_stock"] == movement["quantity"] == 10
    assert movement["sale_id"] is None
    assert movement["date"]


def test_zero_initial_stock_does_not_create_movement(authenticated_client):
    create_product(authenticated_client, stock=0)
    assert authenticated_client.get("/inventory/movements").json()["total"] == 0


@pytest.mark.parametrize("new_stock", [15, 4, 0])
def test_manual_change_is_an_adjustment_and_updates_reports(authenticated_client, user_data, new_stock):
    product = create_product(authenticated_client)
    response = authenticated_client.put(f"/products/{product['id']}", json={"stock": new_stock})
    assert response.status_code == 200
    assert response.json()["stock"] == new_stock
    assert authenticated_client.get(f"/products/{product['id']}").json()["stock"] == new_stock
    movement, = authenticated_client.get("/inventory/movements?type=adjustment").json()["items"]
    assert movement["product_id"] == product["id"]
    assert movement["username"] == user_data["username"]
    assert movement["previous_stock"] == 10
    assert movement["resulting_stock"] == new_stock
    assert movement["quantity"] == abs(new_stock - 10)
    assert movement["sale_id"] is None
    summary = authenticated_client.get("/reports/summary?days=1").json()
    assert summary["inventory_movements"] == 2
    assert summary["inventory_by_day"][0]["entries"] == 10
    assert summary["inventory_by_day"][0]["adjustments"] == abs(new_stock - 10)


def test_unchanged_stock_other_fields_and_activation_create_no_adjustments(authenticated_client):
    product = create_product(authenticated_client)
    for changes in ({"stock": 10}, {"price_cents": 2000}, {"is_active": False}, {"is_active": True}):
        assert authenticated_client.put(f"/products/{product['id']}", json=changes).status_code == 200
    assert authenticated_client.get("/inventory/movements").json()["total"] == 1


def test_invalid_change_does_not_modify_stock_or_history(authenticated_client):
    product = create_product(authenticated_client)
    other = create_product(authenticated_client, code="OTHER")
    for changes, status in (({"stock": -1}, 422), ({"stock": 20, "code": other["code"]}, 409)):
        assert authenticated_client.put(f"/products/{product['id']}", json=changes).status_code == status
    assert authenticated_client.get(f"/products/{product['id']}").json()["stock"] == 10
    assert authenticated_client.get("/inventory/movements?type=adjustment").json()["total"] == 0


def test_movement_failure_rolls_back_stock_change(authenticated_client):
    product = create_product(authenticated_client)

    def fail_movement(*args):
        raise SQLAlchemyError("Fallo de escritura simulado")

    event.listen(InventoryMovement, "before_insert", fail_movement)
    try:
        with pytest.raises(SQLAlchemyError, match="Fallo de escritura simulado"):
            authenticated_client.put(f"/products/{product['id']}", json={"stock": 20})
    finally:
        event.remove(InventoryMovement, "before_insert", fail_movement)
    assert authenticated_client.get(f"/products/{product['id']}").json()["stock"] == 10
    assert authenticated_client.get("/inventory/movements").json()["total"] == 1
