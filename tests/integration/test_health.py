import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_retorna_200(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_health_retorna_status_ok(client: AsyncClient):
    resp = await client.get("/health")
    data = resp.json()
    assert data["status"] == "ok"
    assert "versao" in data
