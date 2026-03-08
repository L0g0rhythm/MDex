import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.api.server import manager, ConnectionManager, search_all, get_chapters, process_downloads
from src.api.mangadex_client import MangaDexClient
from src.api.providers.mangadex import MangaDexProvider
from src.core.config import MANGADEX_API_URL
import respx
from fastapi import HTTPException
import httpx

@pytest.mark.asyncio
async def test_manager_broadcast_error():
    # Test broadcast exception handling
    mock_conn = AsyncMock()
    mock_conn.send_text.side_effect = Exception("Fail")
    
    mgr = ConnectionManager()
    await mgr.connect(mock_conn)
    # Should not raise exception
    await mgr.broadcast({"test": "data"})
    assert len(mgr.active_connections) == 1

@pytest.mark.asyncio
async def test_client_request_error():
    client = MangaDexClient()
    from httpx import RequestError
    async with respx.mock(base_url=MANGADEX_API_URL) as respx_mock:
        respx_mock.get("/err").mock(side_effect=RequestError("Conn Failed"))
        
        with pytest.MonkeyPatch().context() as m:
            async def mock_sleep(x): pass
            m.setattr(asyncio, "sleep", mock_sleep)
            with pytest.raises(Exception, match="Max retries exceeded"):
                await client.get("/err")
    await client.close()

@pytest.mark.asyncio
async def test_provider_get_pages_success():
    provider = MangaDexProvider()
    async with respx.mock(base_url="https://api.mangadex.org") as respx_mock:
        respx_mock.get("/at-home/server/chap1").mock(return_value=httpx.Response(200, json={
            "baseUrl": "https://base",
            "chapter": {"hash": "h1", "data": ["p1.jpg"]}
        }))
        pages = await provider.get_pages("chap1")
        assert pages == ["https://base/data/h1/p1.jpg"]
    await provider.close()

@pytest.mark.asyncio
async def test_provider_get_pages_error():
    provider = MangaDexProvider()
    with patch.object(provider.client, "get", side_effect=Exception("API Error")):
        with pytest.raises(Exception):
            await provider.get_pages("chap1")
    await provider.close()

@pytest.mark.asyncio
async def test_search_all_error():
    with patch("src.api.provider_registry.ProviderRegistry.search_all", side_effect=Exception("API Down")):
        with pytest.raises(HTTPException) as exc:
            await search_all("query")
        assert exc.value.status_code == 500

@pytest.mark.asyncio
async def test_get_chapters_error():
    with patch("src.api.provider_registry.ProviderRegistry.get_provider", side_effect=Exception("No Provider")):
        with pytest.raises(HTTPException) as exc:
            await get_chapters("m1", "p1")
        assert exc.value.status_code == 500

@pytest.mark.asyncio
async def test_process_downloads_exception():
    # Trigger the except block in process_downloads
    with patch("src.api.provider_registry.ProviderRegistry.get_provider", side_effect=Exception("Crash")):
        with patch.object(manager, "broadcast", new_callable=AsyncMock) as mock_b:
            # We don't await because process_downloads is async, we call it directly here
            await process_downloads("m1", "p1", ["c1"], "pt", False)
            assert mock_b.called
            # Verify error message broadcast
            args, kwargs = mock_b.call_args
            assert args[0]["type"] == "error"

def test_base_provider_abstract_raises():
    from src.api.base_provider import BaseProvider
    class Concrete(BaseProvider):
        async def search(self, q): return await super().search(q)
        async def get_chapters(self, m, l): return await super().get_chapters(m, l)
        async def get_pages(self, c): return await super().get_pages(c)
        async def close(self): return await super().close()
    
    c = Concrete()
    # Call each method to trigger super().method() -> BaseProvider.method() -> NotImplementedError
    with pytest.raises(NotImplementedError):
        asyncio.get_event_loop().run_until_complete(c.search("q"))
    with pytest.raises(NotImplementedError):
        asyncio.get_event_loop().run_until_complete(c.get_chapters("id", []))
    with pytest.raises(NotImplementedError):
        asyncio.get_event_loop().run_until_complete(c.get_pages("id"))
    with pytest.raises(NotImplementedError):
        asyncio.get_event_loop().run_until_complete(c.close())
