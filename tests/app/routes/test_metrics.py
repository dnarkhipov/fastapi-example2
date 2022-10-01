import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio


async def test_metrics(client: AsyncClient):
    response = await client.get("/metrics")
    assert response.status_code == status.HTTP_200_OK
