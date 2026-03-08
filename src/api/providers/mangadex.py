import httpx
import asyncio
import logging
from typing import List, Dict, Any
from src.api.base_provider import BaseProvider
from src.core.rate_limiter import RateLimiter
from src.core.config import MANGADEX_API_URL, MAX_CONCURRENT_DOWNLOADS

from src.api.mangadex_client import MangaDexClient

class MangaDexProvider(BaseProvider):
    """MangaDex implementation of the BaseProvider."""

    def __init__(self, concurrent_limit: int = MAX_CONCURRENT_DOWNLOADS):
        self.client = MangaDexClient(concurrent_limit=concurrent_limit)

    async def search(self, query: str) -> List[Dict[str, Any]]:
        try:
            params = {"title": query, "limit": 10}
            response_data = await self.client.get("/manga", params=params)
            data = response_data["data"]
            return [
                {"id": m["id"], "title": m["attributes"]["title"].get("en") or m["attributes"]["title"].get("ja-ro"), "provider": "mangadex"}
                for m in data
            ]
        except Exception as e:
            logging.error(f"MangaDex Search Failure: {e}")
            return []

    async def get_chapters(self, manga_id: str, languages: List[str]) -> List[Dict[str, Any]]:
        """Retrieve chapters for multiple languages to support intelligent translation (Module 12)."""
        try:
            chapters = []
            offset = 0
            limit = 100

            while True:
                params = {
                    "limit": limit,
                    "offset": offset,
                    "translatedLanguage[]": languages,
                    "order[chapter]": "asc"
                }
                data = await self.client.get(f"/manga/{manga_id}/feed", params=params)

                chapters.extend([
                    {
                        "id": c["id"],
                        "number": c["attributes"]["chapter"],
                        "title": c["attributes"]["title"],
                        "lang": c["attributes"]["translatedLanguage"],
                        "provider": "mangadex"
                    }
                    for c in data["data"]
                ])

                if offset + limit >= data["total"]:
                    break
                offset += limit

            return chapters
        except Exception as e:
            logging.error(f"MangaDex Chapters Failure: {e}")
            return []

    async def get_pages(self, chapter_id: str) -> List[str]:
        data = await self.client.get(f"/at-home/server/{chapter_id}")
        base_url = data["baseUrl"]
        chapter_hash = data["chapter"]["hash"]
        filenames = data["chapter"]["data"]
        return [f"{base_url}/data/{chapter_hash}/{f}" for f in filenames]

    async def close(self):
        await self.client.close()
