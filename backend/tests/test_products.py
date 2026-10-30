def test_crear_producto(authenticated_client):
    product_data = {
        "name": "Producto de prueba",
        "code": "TEST-CREATE-001",
        "category_id": 1,
        "description": "Producto creado durante pytest",
        "price_cents": 1999,
        "stock": 10,
        "min_stock": 2,
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
        "code": "TEST-LIST-001",
        "category_id": 1,
        "price_cents": 2500,
        "stock": 5,
        "min_stock": 1,
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
            "code": "TEST-UPDATE-001",
            "category_id": 1,
            "price_cents": 1000,
            "stock": 3,
            "min_stock": 1,
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


def test_vaciar_descripcion_producto(authenticated_client):
    create_response = authenticated_client.post(
        "/products/",
        json={
            "name": "Producto con descripción",
            "code": "TEST-DESC-001",
            "category_id": 1,
            "description": "Descripción que se debe vaciar",
            "price_cents": 1000,
            "stock": 1,
            "min_stock": 0,
        },
    )

    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    update_response = authenticated_client.put(
        f"/products/{product_id}",
        json={"description": None},
    )

    assert update_response.status_code == 200
    assert update_response.json()["description"] is None


def test_obtener_producto_inexistente(authenticated_client):
    response = authenticated_client.get("/products/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Producto no encontrado"


def test_eliminar_producto(authenticated_client):
    create_response = authenticated_client.post(
        "/products/",
        json={
            "name": "Producto para eliminar",
            "code": "TEST-DELETE-001",
            "category_id": 1,
            "price_cents": 500,
            "stock": 1,
            "min_stock": 0,
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

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_codigo_duplicado_sin_distinguir_mayusculas(authenticated_client):
    product_data = {
        "name": "Producto con código",
        "code": "UNICO-001",
        "category_id": 1,
        "price_cents": 1000,
        "stock": 2,
        "min_stock": 1,
    }
    first = authenticated_client.post("/products/", json=product_data)
    assert first.status_code == 201

    duplicate = authenticated_client.post(
        "/products/",
        json={**product_data, "name": "Otro producto", "code": "unico-001"},
    )
    assert duplicate.status_code == 409


def test_editar_conservando_codigo_y_cambiar_estado(authenticated_client):
    created = authenticated_client.post(
        "/products/",
        json={
            "name": "Producto editable",
            "code": "EDIT-001",
            "category_id": 1,
            "price_cents": 2300,
            "stock": 7,
            "min_stock": 2,
        },
    )
    assert created.status_code == 201
    product_id = created.json()["id"]

    unchanged_code = authenticated_client.put(
        f"/products/{product_id}",
        json={"name": "Producto editado", "code": " edit-001 "},
    )
    assert unchanged_code.status_code == 200
    assert unchanged_code.json()["code"] == "edit-001"

    deactivated = authenticated_client.put(
        f"/products/{product_id}",
        json={"is_active": False},
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False
    assert deactivated.json()["stock"] == 7

    reactivated = authenticated_client.put(
        f"/products/{product_id}",
        json={"is_active": True},
    )
    assert reactivated.status_code == 200
    assert reactivated.json()["is_active"] is True

    reloaded = authenticated_client.get(f"/products/{product_id}")
    assert reloaded.status_code == 200
    assert reloaded.json()["is_active"] is True
    assert reloaded.json()["code"] == "edit-001"


def test_editar_no_permite_codigo_de_otro_producto(authenticated_client):
    first = authenticated_client.post(
        "/products/",
        json={
            "name": "Primer producto",
            "code": "CODE-FIRST",
            "category_id": 1,
            "price_cents": 100,
            "stock": 1,
            "min_stock": 0,
        },
    )
    second = authenticated_client.post(
        "/products/",
        json={
            "name": "Segundo producto",
            "code": "CODE-SECOND",
            "category_id": 1,
            "price_cents": 200,
            "stock": 2,
            "min_stock": 0,
        },
    )
    assert first.status_code == second.status_code == 201

    response = authenticated_client.put(
        f"/products/{second.json()['id']}",
        json={"code": "code-first"},
    )
    assert response.status_code == 409


def test_categoria_no_se_puede_eliminar_si_tiene_productos(authenticated_client):
    product_response = authenticated_client.post(
        "/products/",
        json={
            "name": "Producto asociado a categoría",
            "code": "CATEGORY-DELETE-001",
            "category_id": 1,
            "price_cents": 100,
            "stock": 1,
            "min_stock": 0,
        },
    )
    assert product_response.status_code == 201
    response = authenticated_client.delete("/categories/1")
    assert response.status_code == 409


def test_categoria_rechaza_nombre_duplicado_sin_distinguir_mayusculas(authenticated_client):
    response = authenticated_client.post("/categories/", json={"name": "pRuEbAs"})
    assert response.status_code == 409


def test_categoria_se_puede_crear_listar_editar_y_eliminar(authenticated_client):
    created = authenticated_client.post("/categories/", json={"name": "Bebidas"})
    assert created.status_code == 201
    category_id = created.json()["id"]
    assert created.json()["name"] == "Bebidas"

    listed = authenticated_client.get("/categories/")
    assert listed.status_code == 200
    assert any(category["id"] == category_id for category in listed.json())

    updated = authenticated_client.put(
        f"/categories/{category_id}",
        json={"name": "Bebidas frías"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Bebidas frías"

    deleted = authenticated_client.delete(f"/categories/{category_id}")
    assert deleted.status_code == 204
