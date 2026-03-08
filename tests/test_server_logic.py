import pytest
from fastapi.testclient import TestClient
from src.api.server import app, manager, process_downloads
from unittest.mock import AsyncMock, patch, MagicMock

client = TestClient(app)

@pytest.mark.asyncio
async def test_websocket_connection():
    # Test WebSocket connection
    with client.websocket_connect("/ws") as websocket:
        assert len(manager.active_connections) == 1
    assert len(manager.active_connections) == 0

@pytest.mark.asyncio
async def test_process_downloads_logic():
    # Directly test the background task logic in server.py
    with patch("src.api.provider_registry.ProviderRegistry.get_provider") as mock_get, \
         patch("src.api.server.manager.broadcast", new_callable=AsyncMock) as mock_broadcast, \
         patch("src.api.server.download_chapter_images", new_callable=AsyncMock) as mock_dl, \
         patch("src.api.server.create_pdf_from_images") as mock_pdf, \
         patch("src.api.server.shutil.rmtree"), \
         patch("src.modules.ai.ocr_engine.OCREngine", new_callable=MagicMock), \
         patch("src.modules.ai.translator.TranslationEngine", new_callable=MagicMock):

        mock_p = AsyncMock()
        mock_get.return_value = mock_p
        mock_dl.return_value = ["path/to/img1.jpg"]

        # Execute the background task
        await process_downloads("m1", "mangadex", ["c1"], "pt-br", True)

        # Verify broadcasts were called
        assert mock_broadcast.called
        # Verify orchestration
        assert mock_dl.called
        assert mock_pdf.called
