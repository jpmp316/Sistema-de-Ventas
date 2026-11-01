from datetime import datetime, timezone
from decimal import Decimal

from models.sales import Sale
from models.user import User
from routes import reports_routes


def test_seller_changes_only_own_password(authenticated_client):
    data = {"username": "seller_password", "password": "Password123!"}
    created = authenticated_client.post("/users/", json=data)
    assert created.status_code == 201
    login = authenticated_client.post("/auth/login", data=data)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    new = "NewPassword456!"
    path = "/auth/change-password"
    assert authenticated_client.post(path, headers=headers, json={"current_password": "incorrecta", "new_password": new}).status_code == 400
    assert authenticated_client.post(path, headers=headers, json={"current_password": data["password"], "new_password": "weak"}).status_code == 422
    assert authenticated_client.post(path, headers=headers, json={"current_password": data["password"], "new_password": data["password"]}).status_code == 422
    assert authenticated_client.post(path, headers=headers, json={"current_password": data["password"], "new_password": new, "user_id": 1}).status_code == 422
    assert authenticated_client.post(path, headers=headers, json={"current_password": data["password"], "new_password": new}).status_code == 204
    assert authenticated_client.post("/auth/login", data=data).status_code == 401
    assert authenticated_client.post("/auth/login", data={**data, "password": new}).status_code == 200
    assert authenticated_client.get("/users/", headers=headers).status_code == 403


def test_password_change_requires_authentication(client):
    assert client.post("/auth/change-password", json={"current_password": "Password123!", "new_password": "NewPassword456!"}).status_code in (401, 403)


def test_today_uses_colombian_midnight(authenticated_client, test_session_factory, monkeypatch):
    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 11, 1, 18, tzinfo=timezone.utc).astimezone(tz)

    monkeypatch.setattr(reports_routes, "datetime", FixedDateTime)
    with test_session_factory() as db:
        user_id = db.query(User).first().id
        for hour, amount in ((4, "10.00"), (5, "20.00"), (17, "30.00"), (19, "40.00")):
            db.add(Sale(user_id=user_id, date=datetime(2026, 11, 1, hour, tzinfo=timezone.utc), subtotal=Decimal(amount), total=Decimal(amount), status="completed"))
        db.commit()
    response = authenticated_client.get("/reports/summary?days=1")
    assert response.status_code == 200
    report = response.json()
    assert report["operations"] == 2
    assert report["revenue"] == 50
    assert report["sales_by_day"] == [{"day": "2026-11-01", "revenue": 50, "operations": 2}]
    assert report["previous_revenue"] == 10
