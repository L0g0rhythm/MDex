import pytest
import respx
import httpx
from src.api.mangadex_client import MangaDexClient

@pytest.mark.asyncio
async def test_client_initialization():
    client = MangaDexClient(concurrent_limit=2)
    assert client.limiter.semaphore._value == 2
    await client.close()

@respx.mock
@pytest.mark.asyncio
async def test_get_success():
    # Mocking MangaDex API
    respx.get("https://api.mangadex.org/manga").mock(return_value=httpx.Response(200, json={"data": []}))

    client = MangaDexClient()
    result = await client.get("/manga")
    assert result == {"data": []}
    await client.close()
