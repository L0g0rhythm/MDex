import pytest
from fastapi.testclient import TestClient
from src.api.server import app
from unittest.mock import patch, AsyncMock, MagicMock

client = TestClient(app)

def test_search_all_endpoint_mock():
    with patch("src.api.provider_registry.ProviderRegistry.search_all", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = [{"id": "1", "title": "Test Manga", "provider": "test"}]
        response = client.get("/search/all?q=test")
        assert response.status_code == 200
        assert response.json()[0]["title"] == "Test Manga"

def test_chapters_endpoint_mock():
    with patch("src.api.provider_registry.ProviderRegistry.get_provider") as mock_get:
        mock_p = AsyncMock()
        mock_p.get_chapters.return_value = [{"id": "c1", "number": "1", "title": "Test Chapter", "lang": "en", "provider": "test"}]
        mock_p.close = AsyncMock()
        mock_get.return_value = mock_p

        response = client.get("/chapters?manga_id=1&provider=test")
        assert response.status_code == 200
        assert response.json()[0]["id"] == "c1"

def test_download_endpoint_queued():
    # We mock asyncio.create_task to avoid running the background task
    # We close the coroutine to prevent "was never awaited" warnings
    def mock_create_task(coro):
        coro.close()
        return MagicMock()

    with patch("asyncio.create_task", side_effect=mock_create_task):
        response = client.get("/download?manga_id=1&provider=test&chapter_ids=c1,c2")
        assert response.status_code == 200
        assert response.json()["status"] == "queued"
