from thefuzz import fuzz
from src.api.mangadex_client import MangaDexClient

async def search_manga(title: str, client: MangaDexClient):
    """Searches for a manga by title via MangaDex API."""
    params = {"title": title, "limit": 10, "order[relevance]": "desc"}
    data = await client.get("/manga", params=params)

    if not data or not data.get("data"):
        return None

    # Logic for finding best match using thefuzz
    best_match = None
    best_score = 0
    title_lower = title.lower()

    for manga in data["data"]:
        manga_titles = manga["attributes"]["title"].values()
        for t in manga_titles:
            score = fuzz.ratio(title_lower, t.lower())
            if score > best_score:
                best_score = score
                best_match = manga
            if score == 100:
                break

    if best_match and best_score >= 75:
        display_title = best_match["attributes"]["title"].get("en") or \
                        next(iter(best_match["attributes"]["title"].values()))
        return {"id": best_match["id"], "title": display_title}

    return None
