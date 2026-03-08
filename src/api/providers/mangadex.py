import httpx
import asyncio
import logging
from typing import List, Dict, Any
from src.api.base_provider import BaseProvider
from src.core.rate_limiter import RateLimiter
from src.core.config import MANGADEX_API_URL, MAX_CONCURRENT_DOWNLOADS

class MangaDexProvider(BaseProvider):
    """MangaDex implementation of the BaseProvider."""

    def __init__(self, concurrent_limit: int = MAX_CONCURRENT_DOWNLOADS):
        self.client = httpx.AsyncClient(base_url=MANGADEX_API_URL, timeout=30.0)
        self.limiter = RateLimiter(concurrent_limit)

    async def search(self, query: str) -> List[Dict[str, Any]]:
        params = {"title": query, "limit": 10}
        response = await self.client.get("/manga", params=params)
        response.raise_for_status()
        data = response.json()["data"]
        return [
            {"id": m["id"], "title": m["attributes"]["title"].get("en") or m["attributes"]["title"].get("ja-ro"), "provider": "mangadex"}
            for m in data
        ]

    async def get_chapters(self, manga_id: str, languages: List[str]) -> List[Dict[str, Any]]:
        """Retrieve chapters for multiple languages to support intelligent translation (Module 12)."""
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
            response = await self.client.get(f"/manga/{manga_id}/feed", params=params)
            response.raise_for_status()
            data = response.json()

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

    async def get_pages(self, chapter_id: str) -> List[str]:
        response = await self.client.get(f"/at-home/server/{chapter_id}")
        response.raise_for_status()
        data = response.json()
        base_url = data["baseUrl"]
        chapter_hash = data["chapter"]["hash"]
        filenames = data["chapter"]["data"]
        return [f"{base_url}/data/{chapter_hash}/{f}" for f in filenames]

    async def close(self):
        await self.client.aclose()
