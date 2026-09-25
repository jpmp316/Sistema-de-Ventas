def test_crear_usuario(client, user_data):
    response = client.post("/users/", json=user_data)

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "hashed_password" not in data

    client.delete(f"/users/{data['id']}")


def test_login_usuario(client, user_data):
    create_response = client.post("/users/", json=user_data)

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == 200

    token_data = login_response.json()

    assert token_data["token_type"] == "bearer"
    assert token_data["expires_in"] == 30 * 60
    assert token_data["access_token"]

    client.delete(f"/users/{user_id}")


def test_login_con_password_incorrecta(client, user_data):
    create_response = client.post("/users/", json=user_data)

    assert create_response.status_code == 201

    user_id = create_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        data={
            "username": user_data["username"],
            "password": "password_incorrecta",
        },
    )

    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Credenciales inválidas"

    client.delete(f"/users/{user_id}")


def test_listar_usuarios_requiere_autenticacion(client):
    response = client.get("/users/")

    assert response.status_code in (401, 403)


def test_listar_usuarios_autenticado(authenticated_client):
    response = authenticated_client.get("/users/")

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
