import pytest
from unittest.mock import AsyncMock, patch

from app.email.base import EmailResult


@pytest.fixture
async def session_id(client):
    response = await client.post("/api/v1/sessions", json={"source_page": "test-page"})
    return response.json()["session_id"]


async def test_lead_capture_invalid_email(client, session_id):
    response = await client.post(
        "/api/v1/lead-capture",
        json={
            "session_id": session_id,
            "name": "Javeria",
            "email": "not-an-email",
            "phone": "03001234567",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["status"] == "invalid"
    assert "email" in data["errors"]


async def test_lead_capture_invalid_short_phone(client, session_id):
    response = await client.post(
        "/api/v1/lead-capture",
        json={
            "session_id": session_id,
            "name": "Javeria",
            "email": "javeria@example.com",
            "phone": "123",
        },
    )
    data = response.json()
    assert data["success"] is False
    assert "phone" in data["errors"]


@patch("app.api.v1.leads.send_lead_notification", new_callable=AsyncMock)
async def test_lead_capture_success(mock_send_notification, client, session_id):
    
    mock_send_notification.return_value = EmailResult(
        success=True, provider_message_id="fake-id", error=None
    )

    response = await client.post(
        "/api/v1/lead-capture",
        json={
            "session_id": session_id,
            "name": "Javeria",
            "email": "javeria@example.com",
            "phone": "03001234567",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "complete"

    mock_send_notification.assert_awaited_once()
