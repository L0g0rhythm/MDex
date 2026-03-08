import pytest
import asyncio
import hashlib
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
from src.modules.download.download_chapter import download_image_async, download_chapter_images
from src.modules.pdf.pdf_generator import create_pdf_from_images
from src.modules.search.search_manga import search_manga
from src.modules.search.get_chapters import get_manga_chapters
from src.modules.search.chapter_selection import parse_chapter_selection

# --- Acquisition & Image Handling ---
@pytest.mark.asyncio
async def test_download_image_success():
    client = MagicMock()
    resp = MagicMock(status_code=200, content=b"data")
    client.client.get = AsyncMock(return_value=resp)
    
    path = Path("tmp_success.jpg")
    res = await download_image_async("http://url", path, client)
    assert res is True
    assert path.exists()
    path.unlink()

@pytest.mark.asyncio
async def test_download_image_hash_verification():
    client = MagicMock()
    content = b"hashed_data"
    resp = MagicMock(status_code=200, content=content)
    client.client.get = AsyncMock(return_value=resp)
    
    valid_hash = hashlib.md5(content).hexdigest()
    path = Path("tmp_hash.jpg")
    res = await download_image_async("http://url", path, client, expected_hash=valid_hash)
    assert res is True
    
    res_fail = await download_image_async("http://url", path, client, expected_hash="wrong")
    assert res_fail is False
    if path.exists(): path.unlink()

@pytest.mark.asyncio
async def test_download_image_error():
    client = MagicMock()
    client.client.get = AsyncMock(side_effect=Exception("Net Error"))
    res = await download_image_async("http://url", Path("err.jpg"), client)
    assert res is False

@pytest.mark.asyncio
async def test_download_chapter_images_flow():
    provider = AsyncMock()
    # Correct structure for MangaDex at-home server data
    provider.get.return_value = {
        "baseUrl": "https://test.com",
        "chapter": {
            "hash": "h1",
            "data": ["1.jpg"]
        }
    }
    
    with patch("src.modules.download.download_chapter.download_image_async", new_callable=AsyncMock) as m:
        m.return_value = True
        res = await download_chapter_images("c1", Path("."), provider)
        assert len(res) == 1

# --- PDF Generation ---
def test_pdf_generation_full():
    from PIL import Image
    test_img = Path("test_pdf_gen.jpg")
    Image.new('RGB', (10, 10)).save(test_img)
    pdf_out = Path("test_pdf_gen.pdf")
    
    # With mocks for engines
    ocr = MagicMock()
    # Box must be [[x,y],[x,y],[x,y],[x,y]]
    ocr.extract_text.return_value = [{"text": "Hello", "box": [[0,0], [10,0], [10,10], [0,10]]}]
    trans = MagicMock()
    trans.translate.return_value = "Olá"
    
    create_pdf_from_images([test_img], pdf_out, ocr, trans)
    assert pdf_out.exists()
    
    if test_img.exists(): test_img.unlink()
    if pdf_out.exists(): pdf_out.unlink()

# --- Search & Intelligence ---
@pytest.mark.asyncio
async def test_search_manga_logic():
    client = AsyncMock()
    client.get.return_value = {"data": [{"id": "m1", "attributes": {"title": {"en": "Solo"}}}]}
    res = await search_manga("Solo", client)
    assert res["title"] == "Solo"
    
    client.get.return_value = {"data": []}
    assert await search_manga("None", client) is None

@pytest.mark.asyncio
async def test_get_chapters_pagination():
    client = AsyncMock()
    client.get.side_effect = [
        {"data": [{"id": "c1", "attributes": {"chapter": "1"}}], "total": 2},
        {"data": [{"id": "c2", "attributes": {"chapter": "2"}}], "total": 2}
    ]
    res = await get_manga_chapters("m1", "en", client)
    assert len(res) == 2

# --- Selection Logic ---
def test_chapter_selection_parsing():
    chaps = [{"number": "1", "display": "1"}, {"number": "2", "display": "2"}]
    assert len(parse_chapter_selection(chaps, "1")) == 1
    assert len(parse_chapter_selection(chaps, "1-2")) == 2
    assert len(parse_chapter_selection(chaps, "99")) == 0
    # Extra selection branches
    assert len(parse_chapter_selection(chaps, "all")) == 2
    assert len(parse_chapter_selection(chaps, "last")) == 1

# --- Coverage Edge Cases ---
@pytest.mark.asyncio
async def test_base_provider_abstracts():
    from src.api.base_provider import BaseProvider
    class DummyProvider(BaseProvider):
        async def search(self, q): pass
        async def get_chapters(self, m, l): pass
        async def get_pages(self, c): pass
        async def close(self): pass
    p = DummyProvider()
    await p.search("t")
    await p.get_chapters("m", [])
    await p.get_pages("c")
    await p.close()

@pytest.mark.asyncio
async def test_mangadex_client_full_coverage():
    from src.api.mangadex_client import MangaDexClient
    client = MangaDexClient()
    # Mock health and client.client.get
    with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"result": "ok"})
        await client.get("/test")
        assert await client.check_health() is True
    await client.close()

@pytest.mark.asyncio
async def test_provider_registry_edge_cases():
    from src.api.provider_registry import ProviderRegistry
    assert "mangadex" in ProviderRegistry.list_providers()
    with pytest.raises(ValueError):
        ProviderRegistry.get_provider("invalid")
    # Coverage for search_all with one failing
    mock_success = AsyncMock()
    mock_success.search.return_value = [{"id": "1"}]
    # ProviderRegistry expects a CLASS that returns an instance
    mock_class = MagicMock(return_value=mock_success)
    with patch.dict(ProviderRegistry._providers, {"m": mock_class}):
         await ProviderRegistry.search_all("q")

@pytest.mark.asyncio
async def test_mangadex_provider_full_coverage():
    from src.api.providers.mangadex import MangaDexProvider
    p = MangaDexProvider()
    with patch.object(p.client, "get", new_callable=AsyncMock) as mock_get:
        # P1: More than limit, P2: Remaining
        mock_get.side_effect = [
            {"data": [{"id": "m1", "attributes": {"title": "M"}}]}, # search
            {"data": [{"id": "c1", "attributes": {"chapter": "1", "title": "T", "translatedLanguage": "en"}}], "total": 105}, # get_chapters P1
            {"data": [{"id": "c2", "attributes": {"chapter": "2", "title": "T", "translatedLanguage": "en"}}], "total": 105}, # get_chapters P2
            {"baseUrl": "https://test.com", "chapter": {"hash": "h1", "data": ["1.jpg"]}} # get_pages
        ]
        await p.search("test")
        await p.get_chapters("m1", ["en"])
        await p.get_pages("c1")
    await p.close()

@pytest.mark.asyncio
async def test_mangadex_client_retries_and_errors():
    from src.api.mangadex_client import MangaDexClient
    import httpx
    client = MangaDexClient()
    
    # Test 429 Retry-After
    mock_resp_429 = MagicMock(status_code=429, headers={"Retry-After": "0"})
    mock_resp_200 = MagicMock(status_code=200)
    mock_resp_200.json.return_value = {"result": "ok"}
    
    # Use AsyncMock for client.client.get since it's awaited
    with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [mock_resp_429, mock_resp_200]
        with patch("asyncio.sleep", new_callable=AsyncMock):
            res = await client.get("/test")
            assert res == {"result": "ok"}

    # Test 500 Retry
    import httpx
    mock_resp_500 = MagicMock(status_code=500)
    mock_resp_500.raise_for_status.side_effect = httpx.HTTPStatusError("500", request=MagicMock(), response=mock_resp_500)
    
    mock_resp_200_again = MagicMock(status_code=200)
    mock_resp_200_again.json.return_value = {"result": "ok"}
    
    with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [mock_resp_500, mock_resp_200_again]
        with patch("asyncio.sleep", new_callable=AsyncMock):
            res = await client.get("/test")
            assert res == {"result": "ok"}

    # Test TimeoutError
    with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [asyncio.TimeoutError(), mock_resp_200_again]
        with patch("asyncio.sleep", new_callable=AsyncMock):
            res = await client.get("/test")
            assert res == {"result": "ok"}
    
    # Test Max Retries
    with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [mock_resp_500] * 5
        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(Exception, match="Max retries exceeded"):
                await client.get("/test")
    
    # Test 429 without Retry-After (fallback to 5s)
    mock_resp_429_no_header = MagicMock(status_code=429, headers={})
    mock_resp_200_final = MagicMock(status_code=200)
    mock_resp_200_final.json.return_value = {"result": "ok"}
    with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [mock_resp_429_no_header, mock_resp_200_final]
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            res = await client.get("/test")
            assert res == {"result": "ok"}
            mock_sleep.assert_called_with(5)

    # Test check_health Exception
    with patch.object(client.client, "get", side_effect=Exception("Dead")):
        assert await client.check_health() is False

    await client.close()

@pytest.mark.asyncio
async def test_mangadex_provider_errors():
    from src.api.providers.mangadex import MangaDexProvider
    p = MangaDexProvider()
    with patch.object(p.client, "get", side_effect=Exception("Failed")):
        assert await p.search("q") == []
        assert await p.get_chapters("m1", ["en"]) == []
    await p.close()

@pytest.mark.asyncio
async def test_provider_registry_coverage():
    from src.api.provider_registry import ProviderRegistry
    # Test get_provider with invalid
    with pytest.raises(ValueError):
        ProviderRegistry.get_provider("invalid")
    # Test search_all
    with patch("src.api.providers.mangadex.MangaDexProvider.search", new_callable=AsyncMock) as m:
        m.return_value = [{"id": "1"}]
        res = await ProviderRegistry.search_all("query")
        assert len(res) > 0
