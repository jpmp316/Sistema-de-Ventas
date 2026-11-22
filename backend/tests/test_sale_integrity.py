import pytest
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError
from models.sales import Sale, SaleDetail, InventoryMovement


def test_multi_product_sale_preserves_prices_and_history(authenticated_client, product_factory):
    client = authenticated_client
    first = product_factory(price_cents=125, stock=5)
    second = product_factory(price_cents=299, stock=2)
    response = client.post("/sales/", json={"items": [
        {"product_id": first["id"], "quantity": 2},
        {"product_id": second["id"], "quantity": 2},
    ]})
    assert response.status_code == 201, response.text
    sale = response.json()
    assert sale["subtotal"] == sale["total"] == "8.48"
    assert len(sale["details"]) == 2
    assert client.get(f"/products/{second['id']}").json()["stock"] == 0
    client.put(f"/products/{first['id']}", json={"price_cents": 999})
    saved = client.get(f"/sales/{sale['id']}").json()
    assert saved["total"] == "8.48"
    assert saved["details"][0]["unit_price"] == "1.25"
    movements = client.get("/inventory/movements?type=sale").json()["items"]
    assert len(movements) == 2
    assert all(row["sale_id"] == sale["id"] for row in movements)


@pytest.mark.parametrize("failure", ["missing", "inactive", "insufficient"])
def test_invalid_second_line_leaves_no_partial_sale(authenticated_client, product_factory, failure):
    client = authenticated_client
    first = product_factory()
    second = product_factory(stock=1)
    product_id = second["id"]
    expected = 409 if failure == "insufficient" else 404
    if failure == "missing":
        product_id = 99999
    elif failure == "inactive":
        client.put(f"/products/{product_id}", json={"is_active": False})
    before = client.get("/inventory/movements").json()["total"]
    response = client.post("/sales/", json={"items": [
        {"product_id": first["id"], "quantity": 2},
        {"product_id": product_id, "quantity": 2},
    ]})
    assert response.status_code == expected
    assert client.get(f"/products/{first['id']}").json()["stock"] == 10
    assert client.get("/sales/").json()["total"] == 0
    assert client.get("/inventory/movements").json()["total"] == before


@pytest.mark.parametrize("model", [SaleDetail, InventoryMovement])
def test_write_failure_rolls_back_sale_details_stock_and_movements(
    authenticated_client, product_factory, test_session_factory, model,
):
    client = authenticated_client
    product = product_factory()
    before = client.get("/inventory/movements").json()["total"]

    def fail_insert(*args):
        raise SQLAlchemyError("simulated sale failure")

    event.listen(model, "before_insert", fail_insert)
    try:
        with pytest.raises(SQLAlchemyError, match="simulated sale failure"):
            client.post("/sales/", json={"items": [{"product_id": product["id"], "quantity": 2}]})
    finally:
        event.remove(model, "before_insert", fail_insert)
    with test_session_factory() as db:
        assert db.query(Sale).count() == db.query(SaleDetail).count() == 0
        assert db.query(InventoryMovement).count() == before
    assert client.get(f"/products/{product['id']}").json()["stock"] == 10
    # A fresh request remains usable after rollback.
    assert client.post("/sales/", json={"items": [{"product_id": product["id"], "quantity": 1}]}).status_code == 201


@pytest.mark.parametrize("items", [
    [], [{"product_id": 1, "quantity": 0}],
    [{"product_id": 1, "quantity": -1}],
    [{"product_id": 1, "quantity": 1.5}],
    [{"product_id": 0, "quantity": 1}],
])
def test_invalid_sale_lines_are_rejected(authenticated_client, items):
    assert authenticated_client.post("/sales/", json={"items": items}).status_code == 422
    assert authenticated_client.get("/sales/").json()["total"] == 0


def test_missing_sale_returns_404(authenticated_client):
    assert authenticated_client.get("/sales/99999").status_code == 404
