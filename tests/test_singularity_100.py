import pytest
import asyncio
import httpx
import logging
from unittest.mock import AsyncMock, MagicMock, patch
from src.core.config import MANGADEX_API_URL, RETRY_BACKOFF_FACTOR
from src.core.rate_limiter import RateLimiter
from src.api.mangadex_client import MangaDexClient
from src.api.provider_registry import ProviderRegistry
from src.modules.search.chapter_selection import parse_chapter_selection
from src.modules.search.search_manga import search_manga
from src.modules.ai.ocr_engine import OCREngine
from src.modules.ai.translator import TranslationEngine
from src.modules.download.download_chapter import download_image_async
from pathlib import Path

@pytest.mark.asyncio
async def test_client_raise_status_error():
    # Covers mangadex_client.py:33 (raise on status error < 500)
    client = MangaDexClient()
    with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
        request = httpx.Request("GET", f"{MANGADEX_API_URL}/manga")
        real_resp = httpx.Response(403, json={"error": "forbidden"}, request=request)
        mock_get.return_value = real_resp
        with pytest.raises(httpx.HTTPStatusError):
            await client.get("/manga")
    await client.close()

@pytest.mark.asyncio
async def test_registry_search_all_exception():
    with patch("src.api.providers.mangadex.MangaDexProvider.search", side_effect=Exception("Fatal")):
        results = await ProviderRegistry.search_all("query")
        assert results == []

def test_chapter_selection_range_value_error():
    chapters = [{"number": "1"}]
    res = parse_chapter_selection(chapters, "10-abc")
    assert res == []

@pytest.mark.asyncio
async def test_search_manga_no_match():
    mock_client = AsyncMock()
    mock_client.get.return_value = {"data": []}
    res = await search_manga("Ghost Manga", mock_client)
    assert res is None

@pytest.mark.asyncio
async def test_download_image_generic_exception():
    mock_client = MagicMock()
    mock_client.client.get = AsyncMock(side_effect=RuntimeError("IO Crash"))
    res = await download_image_async("http://err", Path("tmp.jpg"), mock_client)
    assert res is False

@pytest.mark.asyncio
async def test_translator_init_failure():
    with patch("argostranslate.translate.get_installed_languages", side_effect=Exception("Pkg Corrupt")):
        engine = TranslationEngine("en", "pt")
        assert engine.is_active is False

@pytest.mark.asyncio
async def test_translator_translate_failure():
    engine = TranslationEngine("en", "pt")
    engine.is_active = True
    engine.translation = MagicMock()
    engine.translation.translate.side_effect = Exception("Model Failure")
    assert engine.translate("Hello") == "Hello"

def test_logger_setup_failure():
    with patch("logging.getLogger") as mock_get:
        mock_root = MagicMock()
        mock_root.handlers = []
        mock_get.return_value = mock_root
        from src.core.logger import setup_logger
        setup_logger("Singularity")

@pytest.mark.asyncio
async def test_provider_search_failure():
    from src.api.providers.mangadex import MangaDexProvider
    p = MangaDexProvider()
    with patch.object(p.client, "get", side_effect=Exception("API Down")):
        res = await p.search("q")
        assert res == []
    await p.close()

@pytest.mark.asyncio
async def test_provider_chapters_failure():
    from src.api.providers.mangadex import MangaDexProvider
    p = MangaDexProvider()
    with patch.object(p.client, "get", side_effect=Exception("API Down")):
        res = await p.get_chapters("id", ["en"])
        assert res == []
    await p.close()

@pytest.mark.asyncio
async def test_main_absolute_singularity():
    from src.main import async_main
    mock_provider = AsyncMock()
    # CRITICAL: ensure close is awaitable and does nothing
    mock_provider.close = AsyncMock()
    
    # Case: Empty manga title -> Coverage 43-44
    with patch("inquirer.list_input", return_value="English"), \
         patch("src.ui.terminal.console.input", side_effect=["", "Solo", "1", "n", "n"]), \
         patch("src.api.provider_registry.ProviderRegistry.get_provider", return_value=mock_provider):
        await async_main()

    # Case: No chapters -> Coverage 61-62
    with patch("inquirer.list_input", return_value="English"), \
         patch("src.ui.terminal.console.input", side_effect=["Solo", "0", "n"]), \
         patch("src.modules.search.search_manga", new_callable=AsyncMock, return_value={"id": "1", "title": "S"}), \
         patch("src.main.get_manga_chapters", new_callable=AsyncMock, return_value=[]), \
         patch("src.api.provider_registry.ProviderRegistry.get_provider", return_value=mock_provider):
        await async_main()

    # Case: No selection -> Coverage 83-84
    with patch("inquirer.list_input", return_value="English"), \
         patch("src.ui.terminal.console.input", side_effect=["Solo", "0", "n"]), \
         patch("src.modules.search.search_manga", new_callable=AsyncMock, return_value={"id": "1", "title": "S"}), \
         patch("src.main.get_manga_chapters", new_callable=AsyncMock, return_value=[{"number": "1", "lang": "en"}]), \
         patch("src.modules.search.chapter_selection.parse_chapter_selection", return_value=[]), \
         patch("src.api.provider_registry.ProviderRegistry.get_provider", return_value=mock_provider):
        await async_main()

    # Case: Needs Translation -> Coverage 90-91
    # We use Portuquês to trigger lang="pt-br". Then provide a chapter in "en".
    with patch("inquirer.list_input", return_value="Português (Brasil)"), \
         patch("src.ui.terminal.console.input", side_effect=["Solo", "1", "n", "n"]), \
         patch("src.modules.search.search_manga", new_callable=AsyncMock, return_value={"id": "1", "title": "S"}), \
         patch("src.main.get_manga_chapters", new_callable=AsyncMock, return_value=[{"number": "1", "lang": "en"}]), \
         patch("src.modules.search.chapter_selection.parse_chapter_selection", return_value=[{"id": "c1", "display": "1", "lang": "en", "number": "1"}]), \
         patch("src.api.provider_registry.ProviderRegistry.get_provider", return_value=mock_provider):
        await async_main()

@pytest.mark.asyncio
async def test_download_image_hash_verification():
    mock_client = MagicMock()
    mock_client.client.get = AsyncMock()
    content = b"fake content"
    resp = MagicMock(content=content, status_code=200)
    resp.raise_for_status = MagicMock()
    mock_client.client.get.return_value = resp
    import hashlib
    expected_hash = hashlib.sha256(content).hexdigest()
    res = await download_image_async("http://img", Path("test_h.jpg"), mock_client, expected_hash=expected_hash)
    assert res is True
    if Path("test_h.jpg").exists(): Path("test_h.jpg").unlink()

@pytest.mark.asyncio
async def test_mangadex_provider_pagination_coverage():
    from src.api.providers.mangadex import MangaDexProvider
    p = MangaDexProvider()
    with patch.object(p.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [
            {"data": [{"id": str(i), "attributes": {"chapter": str(i), "title": "T", "translatedLanguage": "en"}} for i in range(100)], "total": 150},
            {"data": [{"id": str(i), "attributes": {"chapter": str(i), "title": "T", "translatedLanguage": "en"}} for i in range(100, 150)], "total": 150}
        ]
        res = await p.get_chapters("m1", ["en"])
        assert len(res) == 150
    await p.close()
