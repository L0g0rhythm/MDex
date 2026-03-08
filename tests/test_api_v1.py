import pytest
import asyncio
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from src.api.server import app, manager, ConnectionManager

client = TestClient(app)

# --- ConnectionManager Unit Tests ---
@pytest.mark.asyncio
async def test_websocket_manager_logic():
    mock_ws = AsyncMock()
    # Specifically ensure accept is awaitable
    mock_ws.accept = AsyncMock()
    mock_ws.send_text = AsyncMock()
    
    # Singleton check/instantiation for unit test scope
    local_manager = ConnectionManager()
    await local_manager.connect(mock_ws)
    assert mock_ws in local_manager.active_connections
    
    await local_manager.broadcast({"type": "test"})
    mock_ws.send_text.assert_called()
    
    # Test stale connection handling
    mock_ws.send_text.side_effect = Exception("Closed")
    await local_manager.broadcast({"type": "test"}) # Should pass
    
    local_manager.disconnect(mock_ws)
    assert mock_ws not in local_manager.active_connections

# --- API v1 Integration Tests ---
def test_api_v1_manga_search():
    with patch("src.api.provider_registry.ProviderRegistry.search_all", new_callable=AsyncMock) as mock:
        mock.return_value = [{"id": "m1", "title": "S", "provider": "mangadex"}]
        resp = client.get("/api/v1/manga/search?title=test")
        assert resp.status_code == 200
        assert resp.json()[0]["id"] == "m1"

def test_api_v1_manga_search_error():
    with patch("src.api.provider_registry.ProviderRegistry.search_all", side_effect=Exception("API Down")):
        resp = client.get("/api/v1/manga/search?title=test")
        assert resp.status_code == 500

def test_api_v1_manga_chapters():
    mock_p = AsyncMock()
    mock_p.get_chapters.return_value = [{"id": "c1", "number": "1", "lang": "en"}]
    mock_p.close = AsyncMock()
    with patch("src.api.provider_registry.ProviderRegistry.get_provider", return_value=mock_p):
        resp = client.get("/api/v1/manga/m1/chapters")
        assert resp.status_code == 200
        assert resp.json()[0]["id"] == "c1"

def test_api_v1_manga_chapters_error():
    with patch("src.api.provider_registry.ProviderRegistry.get_provider", side_effect=Exception("Provider Fail")):
        resp = client.get("/api/v1/manga/m1/chapters")
        assert resp.status_code == 500

def test_api_v1_download_start():
    with patch("src.api.server.process_downloads", new_callable=AsyncMock):
        payload = {"manga_id": "m1", "chapter_ids": ["c1"], "use_ai": True}
        resp = client.post("/api/v1/download/start", json=payload)
        assert resp.status_code == 200
        assert "initiated" in resp.json()["message"]

def test_api_v1_download_start_validation_error():
    resp = client.post("/api/v1/download/start", json={"invalid": "payload"})
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_api_search_failure():
    from src.api.server import app
    from httpx import AsyncClient, ASGITransport
    mock_registry = AsyncMock()
    mock_registry.search_all.return_value = []
    with patch("src.api.server.ProviderRegistry", mock_registry):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.get("/api/v1/search?q=test")
            assert resp.status_code == 404

@pytest.mark.asyncio
async def test_api_download_failure():
    from src.api.server import app
    from httpx import AsyncClient, ASGITransport
    # Accessing the queue from the module if available, or patching the module variable
    import src.api.server as server_mod
    # Module has 'process_downloads', we should patch it correctly
    with patch("src.api.server.process_downloads", side_effect=Exception("Fail")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            data = {"manga_id": "1", "chapter_ids": ["c1"], "use_ai": False}
            resp = await ac.post("/api/v1/download/start", json=data)
            # The failure is inside a create_task, so it returns 200 but task fails (covered by pragma in server.py)
            assert resp.status_code == 200
@pytest.mark.asyncio
async def test_process_downloads_background_task():
    from src.api.server import process_downloads
    mock_p = AsyncMock()
    mock_p.close = AsyncMock()
    
    with patch("src.api.provider_registry.ProviderRegistry.get_provider", return_value=mock_p), \
         patch("src.api.server.download_chapter_images", new_callable=AsyncMock) as mock_dl, \
         patch("src.api.server.create_pdf_from_images") as mock_pdf, \
         patch("src.api.server.DOWNLOAD_DIR", Path(".")), \
         patch("shutil.rmtree"), \
         patch.object(manager, "broadcast", new_callable=AsyncMock):
        
        mock_dl.return_value = [Path("img.jpg")]
        # Case with AI
        await process_downloads("m1", "mangadex", ["c1"], "pt", True)
        mock_pdf.assert_called()
        
        # Case without AI
        mock_pdf.reset_mock()
        await process_downloads("m1", "mangadex", ["c2"], "en", False)
        mock_pdf.assert_called()

@pytest.mark.asyncio
async def test_server_v1_error_routes():
    with patch("src.api.provider_registry.ProviderRegistry.search_all", side_effect=Exception("Failed")):
        response = client.get("/api/v1/manga/search?title=test")
        assert response.status_code == 500

    with patch("src.api.provider_registry.ProviderRegistry.get_provider") as mock_gp:
        mock_p = AsyncMock()
        mock_p.get_chapters.side_effect = Exception("Failed")
        mock_gp.return_value = mock_p
        response = client.get("/api/v1/manga/m1/chapters")
        assert response.status_code == 500

@pytest.mark.asyncio
async def test_download_start_error():
    # Test invalid json or other post error
    response = client.post("/api/v1/download/start", json={"manga_id": "m1"})
    # Pydantic will fail if chapter_ids is missing
    assert response.status_code == 422 
        
@pytest.mark.asyncio
async def test_process_downloads_fatal_error():
    from src.api.server import process_downloads
    with patch("src.api.provider_registry.ProviderRegistry.get_provider", side_effect=Exception("Fatal")):
        await process_downloads("m1", "mangadex", ["c1"], "pt", False)
        # Should reach logger and broadcast without crashing
