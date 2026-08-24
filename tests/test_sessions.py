import pytest


async def test_create_session(client):
    response = await client.post("/api/v1/sessions", json={"source_page": "test-page"})
    assert response.status_code in (200, 201)

    data = response.json()
    assert "session_id" in data
    assert isinstance(data["session_id"], str)
    assert len(data["session_id"]) > 0


async def test_create_session_returns_unique_tokens(client):
    response1 = await client.post("/api/v1/sessions", json={"source_page": "test-page"})
    response2 = await client.post("/api/v1/sessions", json={"source_page": "test-page"})

    session_id_1 = response1.json()["session_id"]
    session_id_2 = response2.json()["session_id"]

    assert session_id_1 != session_id_2
