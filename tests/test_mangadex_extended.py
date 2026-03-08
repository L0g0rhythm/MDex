import pytest
import respx
from httpx import Response, HTTPStatusError, RequestError
from src.api.providers.mangadex import MangaDexProvider
from src.api.mangadex_client import MangaDexClient
from src.core.config import MANGADEX_API_URL
import asyncio

@pytest.mark.asyncio
async def test_client_retry_on_500():
    client = MangaDexClient()
    async with respx.mock(base_url=MANGADEX_API_URL) as respx_mock:
        # First attempt 500, second 200
        respx_mock.get("/test").mock(side_effect=[
            Response(500),
            Response(200, json={"ok": True})
        ])
        
        # We need to mock asyncio.sleep to avoid waiting during tests
        with pytest.MonkeyPatch().context() as m:
            async def mock_sleep(x): pass
            m.setattr(asyncio, "sleep", mock_sleep)
            result = await client.get("/test")
            assert result == {"ok": True}
    await client.close()

@pytest.mark.asyncio
async def test_client_429_retry():
    client = MangaDexClient()
    async with respx.mock(base_url=MANGADEX_API_URL) as respx_mock:
        respx_mock.get("/test").mock(side_effect=[
            Response(429, headers={"Retry-After": "1"}),
            Response(200, json={"ok": True})
        ])
        
        with pytest.MonkeyPatch().context() as m:
            async def mock_sleep(x): pass
            m.setattr(asyncio, "sleep", mock_sleep)
            result = await client.get("/test")
            assert result == {"ok": True}
    await client.close()

@pytest.mark.asyncio
async def test_client_max_retries():
    client = MangaDexClient()
    async with respx.mock(base_url=MANGADEX_API_URL) as respx_mock:
        respx_mock.get("/test").mock(return_value=Response(500))
        
        with pytest.MonkeyPatch().context() as m:
            async def mock_sleep(x): pass
            m.setattr(asyncio, "sleep", mock_sleep)
            with pytest.raises(Exception, match="Max retries exceeded"):
                await client.get("/test")
    await client.close()

@pytest.mark.asyncio
async def test_provider_error_handling():
    provider = MangaDexProvider()
    with pytest.MonkeyPatch().context() as m:
        # Mock search method of client inside provider to fail
        async def fail(*args, **kwargs):
            raise Exception("Generic Failure")
        m.setattr(provider.client, "get", fail)
        
        results = await provider.search("Solo")
        assert results == []
    await provider.close()
