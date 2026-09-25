def test_crear_producto(authenticated_client):
    product_data = {
        "name": "Producto de prueba",
        "description": "Producto creado durante pytest",
        "price_cents": 1999,
        "stock": 10,
    }

    response = authenticated_client.post(
        "/products/",
        json=product_data,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == product_data["name"]
    assert data["description"] == product_data["description"]
    assert data["price_cents"] == 1999
    assert data["stock"] == 10

    authenticated_client.delete(f"/products/{data['id']}")


def test_listar_productos_requiere_autenticacion(client):
    response = client.get("/products/")

    assert response.status_code in (401, 403)


def test_listar_productos(authenticated_client):
    product_data = {
        "name": "Producto para listar",
        "price_cents": 2500,
        "stock": 5,
    }

    create_response = authenticated_client.post(
        "/products/",
        json=product_data,
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    list_response = authenticated_client.get("/products/")

    assert list_response.status_code == 200

    data = list_response.json()

    assert "items" in data
    assert "total" in data
    assert any(item["id"] == product_id for item in data["items"])

    authenticated_client.delete(f"/products/{product_id}")


def test_actualizar_producto(authenticated_client):
    create_response = authenticated_client.post(
        "/products/",
        json={
            "name": "Producto original",
            "price_cents": 1000,
            "stock": 3,
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    update_response = authenticated_client.put(
        f"/products/{product_id}",
        json={
            "name": "Producto actualizado",
            "price_cents": 1500,
            "stock": 8,
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["name"] == "Producto actualizado"
    assert data["price_cents"] == 1500
    assert data["stock"] == 8

    authenticated_client.delete(f"/products/{product_id}")


def test_obtener_producto_inexistente(authenticated_client):
    response = authenticated_client.get("/products/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Producto no encontrado"


def test_eliminar_producto(authenticated_client):
    create_response = authenticated_client.post(
        "/products/",
        json={
            "name": "Producto para eliminar",
            "price_cents": 500,
            "stock": 1,
        },
    )

    assert create_response.status_code == 201

    product_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(
        f"/products/{product_id}",
    )

    assert delete_response.status_code == 204

    get_response = authenticated_client.get(
        f"/products/{product_id}",
    )

    assert get_response.status_code == 404