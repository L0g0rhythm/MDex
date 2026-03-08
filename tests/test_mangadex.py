import pytest
import respx
from httpx import Response
from src.api.providers.mangadex import MangaDexProvider
from src.core.config import MANGADEX_API_URL

@pytest.mark.asyncio
async def test_mangadex_search_mock():
    async with respx.mock(base_url=MANGADEX_API_URL) as respx_mock:
        respx_mock.get("/manga").mock(return_value=Response(200, json={
            "data": [
                {
                    "id": "123",
                    "attributes": {
                        "title": {"en": "Solo Leveling", "ja-ro": "Ore dake Level Up na Ken"}
                    }
                }
            ]
        }))

        provider = MangaDexProvider()
        results = await provider.search("Solo")
        assert len(results) == 1
        assert results[0]["id"] == "123"
        await provider.close()

@pytest.mark.asyncio
async def test_mangadex_get_chapters_mock():
    async with respx.mock(base_url="https://api.mangadex.org") as respx_mock:
        respx_mock.get("/manga/123/feed").mock(return_value=Response(200, json={
            "data": [
                {
                    "id": "chap1",
                    "attributes": {
                        "chapter": "1",
                        "title": "Begin",
                        "translatedLanguage": "pt-br"
                    }
                }
            ],
            "total": 1
        }))

        provider = MangaDexProvider()
        chapters = await provider.get_chapters("123", ["pt-br"])
        assert len(chapters) == 1
        assert chapters[0]["number"] == "1"
        await provider.close()
