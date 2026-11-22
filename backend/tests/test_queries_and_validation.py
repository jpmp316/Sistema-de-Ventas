from datetime import datetime, timezone

import pytest
from models.sales import InventoryMovement
from models.user import User


@pytest.mark.parametrize("path", ["/sales/", "/inventory/movements"])
@pytest.mark.parametrize("query", ["page=0", "page_size=0", "page_size=101"])
def test_strict_pagination_limits(authenticated_client, path, query):
    assert authenticated_client.get(f"{path}?{query}").status_code == 422


@pytest.mark.parametrize("days", [0, -1, 366, "invalid"])
def test_report_period_validation(authenticated_client, days):
    assert authenticated_client.get(f"/reports/summary?days={days}").status_code == 422


@pytest.mark.parametrize("path", ["/products/", "/products/paginated", "/users/paginated"])
def test_legacy_pagination_normalizes_limits(authenticated_client, path):
    result = authenticated_client.get(f"{path}?page=0&page_size=101")
    assert result.status_code == 200
    assert result.json()["page"] == 1
    assert result.json()["page_size"] == 100


def test_product_pages_have_consistent_metadata_and_no_duplicates(authenticated_client, product_factory):
    ids = [product_factory()["id"] for _ in range(3)]
    first = authenticated_client.get("/products/?page=1&page_size=2").json()
    second = authenticated_client.get("/products/?page=2&page_size=2").json()
    assert first["total"] == second["total"] == 3
    assert first["total_pages"] == second["total_pages"] == 2
    assert [row["id"] for row in first["items"] + second["items"]] == ids
    assert authenticated_client.get("/products/?page=3&page_size=2").json()["items"] == []


def test_inventory_dates_are_inclusive_utc_and_type_filter_combines(
    authenticated_client, product_factory, test_session_factory,
):
    product = product_factory(stock=0)
    with test_session_factory() as db:
        user_id = db.query(User).first().id
        for date, kind in [
            (datetime(2026, 1, 1, 23, 59, 59), "adjustment"),
            (datetime(2026, 1, 2), "adjustment"),
            (datetime(2026, 1, 2, 23, 59, 59), "adjustment"),
            (datetime(2026, 1, 2, 12), "entry"),
            (datetime(2026, 1, 3), "adjustment"),
        ]:
            db.add(InventoryMovement(
                product_id=product["id"], user_id=user_id, date=date.replace(tzinfo=timezone.utc),
                type=kind, quantity=1, previous_stock=0, resulting_stock=1,
            ))
        db.commit()
    response = authenticated_client.get(
        "/inventory/movements?date_from=2026-01-02&date_to=2026-01-02&type=adjustment&page_size=1"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == data["total_pages"] == 2
    assert data["items"][0]["date"].startswith("2026-01-02T23:59:59")
    assert data["items"][0]["product_name"] == product["name"]
    second = authenticated_client.get(
        "/inventory/movements?date_from=2026-01-02&date_to=2026-01-02&type=adjustment&page_size=1&page=2"
    ).json()
    assert second["items"][0]["id"] != data["items"][0]["id"]


@pytest.mark.parametrize("field,value", [
    ("price_cents", 0), ("price_cents", -1), ("stock", -1),
    ("stock", 1.5), ("min_stock", -1), ("category_id", 99999),
])
def test_invalid_update_preserves_product(authenticated_client, product_factory, field, value):
    product = product_factory()
    response = authenticated_client.put(f"/products/{product['id']}", json={field: value})
    assert response.status_code == 422
    assert authenticated_client.get(f"/products/{product['id']}").json() == product


@pytest.mark.parametrize("method", ["put", "delete"])
def test_missing_category_returns_404(authenticated_client, method):
    response = authenticated_client.request(method, "/categories/99999",
                                            **({"json": {"name": "Valid name"}} if method == "put" else {}))
    assert response.status_code == 404


def test_category_conflict_preserves_original_name(authenticated_client):
    created = authenticated_client.post("/categories/", json={"name": "Bebidas"}).json()
    response = authenticated_client.put(f"/categories/{created['id']}", json={"name": " pRuEbAs "})
    assert response.status_code == 409
    assert any(row["name"] == "Bebidas" for row in authenticated_client.get("/categories/").json())
