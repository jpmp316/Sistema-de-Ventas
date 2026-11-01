def test_venta_guarda_detalles_descuenta_stock_y_crea_movimiento(authenticated_client):
    product = authenticated_client.post("/products/", json={
        "name": "Producto para venta",
        "code": "SALE-FLOW-001",
        "category_id": 1,
        "price_cents": 1250,
        "stock": 8,
        "min_stock": 1,
    })
    assert product.status_code == 201
    product_id = product.json()["id"]

    response = authenticated_client.post("/sales/", json={"items": [{"product_id": product_id, "quantity": 3}]})
    assert response.status_code == 201
    sale = response.json()
    assert sale["total"] == "37.50"
    assert sale["details"][0]["quantity"] == 3

    updated_product = authenticated_client.get(f"/products/{product_id}").json()
    assert updated_product["stock"] == 5
    movements = authenticated_client.get("/inventory/movements").json()
    assert any(movement["sale_id"] == sale["id"] and movement["resulting_stock"] == 5 for movement in movements["items"])


def test_venta_rechaza_stock_insuficiente(authenticated_client):
    product = authenticated_client.post("/products/", json={
        "name": "Stock para rechazo",
        "code": "SALE-STOCK-001",
        "category_id": 1,
        "price_cents": 100,
        "stock": 1,
        "min_stock": 0,
    })
    response = authenticated_client.post("/sales/", json={"items": [{"product_id": product.json()["id"], "quantity": 2}]})
    assert response.status_code == 409
