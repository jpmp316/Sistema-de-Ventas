import pytest


@pytest.fixture
def seller(authenticated_client):
    data = {"username": "vendedor_prueba", "password": "Password123!"}
    created = authenticated_client.post("/users/", json=data)
    assert created.status_code == 201
    login = authenticated_client.post("/auth/login", data=data)
    assert login.status_code == 200
    assert login.json()["role"] == "vendedor"
    return authenticated_client, {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.parametrize("method,path,body", [
    ("post", "/products/", {"name": "No permitido", "code": "DENIED", "category_id": 1, "price_cents": 100, "stock": 1}),
    ("put", "/products/1", {"stock": 100, "is_active": False}),
    ("delete", "/products/1", None),
    ("post", "/categories/", {"name": "No permitida"}),
    ("put", "/categories/1", {"name": "No permitida"}),
    ("delete", "/categories/1", None),
    ("get", "/users/", None),
    ("get", "/users/paginated", None),
    ("get", "/users/1", None),
    ("post", "/users/", {"username": "intruso", "password": "Password123!"}),
    ("put", "/users/1", {"password": "NewPassword123!"}),
    ("delete", "/users/1", None),
    ("post", "/auth/bootstrap-admin", {"username": "intruso", "password": "Password123!"}),
    ("get", "/reports/summary", None),
])
def test_seller_cannot_access_admin_operations(seller, method, path, body):
    client, headers = seller
    response = client.request(method, path, headers=headers, **({"json": body} if body else {}))
    assert response.status_code == 403, response.text


def test_seller_can_sell_view_details_movements_and_logout(seller):
    client, headers = seller
    product = client.post("/products/", json={
        "name": "Producto del vendedor", "code": "SELLER-001", "category_id": 1,
        "price_cents": 15000, "stock": 10, "min_stock": 1,
    }).json()
    for path in ("/products/", "/products/paginated", f"/products/{product['id']}", "/categories/"):
        assert client.get(path, headers=headers).status_code == 200
    response = client.post("/sales/", headers=headers, json={"items": [{"product_id": product["id"], "quantity": 2}]})
    assert response.status_code == 201, response.text
    sale = response.json()
    assert sale["total"] == "300.00"
    assert sale["username"] == "vendedor_prueba"
    assert sale["details"][0]["product_name"] == product["name"]
    assert sale["details"][0]["product_code"] == product["code"]
    assert client.get(f"/sales/{sale['id']}", headers=headers).json() == sale
    assert client.get("/sales/", headers=headers).json()["total"] == 1
    movements = client.get("/inventory/movements?type=sale", headers=headers).json()["items"]
    assert len(movements) == 1
    assert movements[0]["username"] == "vendedor_prueba"
    assert movements[0]["previous_stock"] == 10
    assert movements[0]["resulting_stock"] == 8
    assert client.post("/auth/logout", headers=headers).status_code == 204
    assert client.get("/inventory/movements", headers=headers).status_code == 401


def test_repeated_product_cannot_bypass_stock_check(authenticated_client):
    product = authenticated_client.post("/products/", json={
        "name": "Stock protegido", "code": "STOCK-SAFE", "category_id": 1,
        "price_cents": 100, "stock": 3, "min_stock": 0,
    }).json()
    line = {"product_id": product["id"], "quantity": 2}
    response = authenticated_client.post("/sales/", json={"items": [line, line]})
    assert response.status_code == 422
    assert authenticated_client.get(f"/products/{product['id']}").json()["stock"] == 3
    assert authenticated_client.get("/sales/").json()["total"] == 0
