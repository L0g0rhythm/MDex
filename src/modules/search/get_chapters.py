from src.api.mangadex_client import MangaDexClient
from src.core.config import CHAPTERS_PER_BATCH

async def get_manga_chapters(manga_id: str, lang: str, client: MangaDexClient):
    """Fetches all available chapters for a manga in a specific language."""
    chapters = []
    offset = 0
    limit = 100 # Standard API limit

    while True:
        params = {
            "manga": manga_id,
            "translatedLanguage[]": [lang],
            "includes[]": ["scanlation_group"],
            "order[chapter]": "asc",
            "limit": limit,
            "offset": offset,
            "contentRating[]": ["safe", "suggestive", "erotica", "pornographic"]
        }

        data = await client.get("/chapter", params=params)

        current_batch = data.get("data", [])
        if not current_batch:  # pragma: no cover
            break  # pragma: no cover

        for item in current_batch:
            attrs = item["attributes"]
            chapters.append({
                "id": item["id"],
                "number": attrs.get("chapter"),
                "title": attrs.get("title"),
                "display": attrs.get("chapter") or attrs.get("title") or "N/A"
            })

        offset += len(current_batch)
        if offset >= data.get("total", 0):
            break

    return chapters
