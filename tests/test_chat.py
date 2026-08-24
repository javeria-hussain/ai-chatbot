import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
async def session_id(client):
    response = await client.post("/api/v1/sessions", json={"source_page": "test-page"})
    return response.json()["session_id"]


@patch("app.api.v1.chat.orchestrator.get_response", new_callable=AsyncMock)
async def test_chat_message_basic_flow(mock_get_response, client, session_id):
    
    mock_get_response.return_value = {
        "answer": "We build custom software, SaaS products, and AI solutions.",
        "sources_used": 3,
        "grounded": True,
    }

    response = await client.post(
        "/api/v1/chat/messages",
        json={
            "session_id": session_id,
            "message": "What services do you offer?",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert (
        data["answer"] == "We build custom software, SaaS products, and AI solutions."
    )
    assert data["grounded"] is True
    assert data["sources_used"] == 3
    assert data["session_id"] == session_id

    mock_get_response.assert_awaited_once()


@patch("app.api.v1.chat.orchestrator.get_response", new_callable=AsyncMock)
async def test_chat_message_pricing_triggers_lead_capture(
    mock_get_response, client, session_id
):
    mock_get_response.return_value = {
        "answer": "Our pricing depends on project scope.",
        "sources_used": 2,
        "grounded": True,
    }

    response = await client.post(
        "/api/v1/chat/messages",
        json={
            "session_id": session_id,
            "message": "What is your pricing for a quote?",
        },
    )

    data = response.json()
    assert data["lead_capture_required"] is True
    assert "name" in data["missing_lead_fields"]
