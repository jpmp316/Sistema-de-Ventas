from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from models.sales import Sale
from models.user import User
from routes import reports_routes


@pytest.mark.parametrize("days,operations,revenue,average", [
    (1, 2, 200.01, 100.01),
    (7, 3, 300, 100),
    (30, 3, 300, 100),
    (90, 3, 300, 100),
])
def test_average_ticket_counts_completed_sales_in_period(
    authenticated_client, test_session_factory, monkeypatch, days, operations, revenue, average,
):
    now = datetime(2026, 11, 1, 18, tzinfo=timezone.utc)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now.astimezone(tz)

    monkeypatch.setattr(reports_routes, "datetime", FixedDateTime)
    with test_session_factory() as db:
        user_id = db.query(User).first().id
        for date, amount, status in [
            (now - timedelta(hours=1), "100.00", "completed"),
            (now - timedelta(hours=2), "100.01", "completed"),
            (now - timedelta(days=1), "99.99", "completed"),
            (now - timedelta(hours=3), "90000.00", "cancelled"),
            (now + timedelta(days=1), "9999.00", "completed"),
            (now - timedelta(days=100), "8000.00", "completed"),
        ]:
            db.add(Sale(user_id=user_id, date=date, subtotal=Decimal(amount), total=Decimal(amount), status=status))
        db.commit()
    response = authenticated_client.get(f"/reports/summary?days={days}")
    assert response.status_code == 200
    report = response.json()
    assert report["operations"] == operations
    assert report["revenue"] == revenue
    assert report["average_ticket"] == average


def test_average_ticket_without_sales_is_zero(authenticated_client):
    report = authenticated_client.get("/reports/summary?days=7").json()
    assert report["operations"] == 0
    assert report["revenue"] == 0
    assert report["average_ticket"] == 0
