import pytest
from src.modules.search.search_manga import search_manga
from src.modules.search.get_chapters import get_manga_chapters
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_search_manga_success():
    mock_client = AsyncMock()
    mock_client.get.return_value = {
        "data": [{
            "id": "m1",
            "attributes": {
                "title": {"en": "Solo Leveling"}
            }
        }]
    }

    result = await search_manga("Solo Leveling", mock_client)
    assert result["id"] == "m1"
    assert result["title"] == "Solo Leveling"

@pytest.mark.asyncio
async def test_search_manga_no_results():
    mock_client = AsyncMock()
    mock_client.get.return_value = {"data": []}

    result = await search_manga("Unknown", mock_client)
    assert result is None

@pytest.mark.asyncio
async def test_search_manga_fuzz_match():
    mock_client = AsyncMock()
    # Mocking title to satisfy 75 threshold (EXACT match to be safe for coverage)
    mock_client.get.return_value = {
        "data": [{
            "id": "m2",
            "attributes": {
                "title": {"en": "One Piece"}
            }
        }]
    }

    result = await search_manga("One Piece", mock_client)
    assert result is not None
    assert result["id"] == "m2"

@pytest.mark.asyncio
async def test_get_manga_chapters_pagination():
    mock_client = AsyncMock()
    mock_client.get.side_effect = [
        {
            "data": [{"id": "c1", "attributes": {"chapter": "1", "title": "Start"}}],
            "total": 2
        },
        {
            "data": [{"id": "c2", "attributes": {"chapter": "2", "title": "Next"}}],
            "total": 2
        }
    ]

    # get_manga_chapters(manga_id, lang, client)
    chapters = await get_manga_chapters("m1", "en", mock_client)
    assert len(chapters) == 2
    assert chapters[0]["number"] == "1"

@pytest.mark.asyncio
async def test_get_manga_chapters_empty():
    mock_client = AsyncMock()
    mock_client.get.return_value = {"data": [], "total": 0}

    chapters = await get_manga_chapters("m1", "en", mock_client)
    assert chapters == []
