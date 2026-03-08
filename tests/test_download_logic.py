import pytest
from pathlib import Path
from src.modules.download.download_chapter import download_image_async, download_chapter_images
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

@pytest.mark.asyncio
async def test_download_image_async_success(tmp_path):
    mock_client = MagicMock()
    mock_client.client = AsyncMock()
    mock_client.limiter = AsyncMock()

    mock_response = MagicMock()
    mock_response.content = b"fake image data"
    mock_response.status_code = 200
    mock_client.client.get.return_value = mock_response

    target_path = tmp_path / "test.jpg"
    success = await download_image_async("http://example.com/img.jpg", target_path, mock_client)

    assert success is True
    assert target_path.read_bytes() == b"fake image data"

@pytest.mark.asyncio
async def test_download_image_async_failure(tmp_path):
    mock_client = MagicMock()
    mock_client.client = AsyncMock()
    mock_client.limiter = AsyncMock()
    mock_client.client.get.side_effect = Exception("Network error")

    target_path = tmp_path / "fail.jpg"
    success = await download_image_async("http://example.com/img.jpg", target_path, mock_client)

    assert success is False

@pytest.mark.asyncio
async def test_download_chapter_images_orchestration(tmp_path):
    mock_client = AsyncMock()
    mock_client.get.return_value = {
        "baseUrl": "https://base.com",
        "chapter": {
            "hash": "abc",
            "data": ["1.jpg", "2.jpg"]
        }
    }

    with patch("src.modules.download.download_chapter.download_image_async", return_value=True) as mock_dl:
        results = await download_chapter_images("chap1", tmp_path, mock_client)
        assert len(results) == 2
        assert mock_dl.call_count == 2
