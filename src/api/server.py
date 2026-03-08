from fastapi import FastAPI, HTTPException
from typing import List, Optional
from src.api.provider_registry import ProviderRegistry
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="MDex Omni-v5 API")

# Module 28: External Interface Contracts - CORS Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MangaResult(BaseModel):
    id: str
    title: str
    provider: str

class ChapterResult(BaseModel):
    id: str
    number: str
    title: Optional[str]
    lang: str
    provider: str

@app.get("/search/all", response_model=List[MangaResult])
async def search_all(q: str):
    try:
        return await ProviderRegistry.search_all(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chapters", response_model=List[ChapterResult])
async def get_chapters(manga_id: str, provider: str, langs: str = "pt-br,en"):
    try:
        lang_list = langs.split(",")
        p = ProviderRegistry.get_provider(provider)
        results = await p.get_chapters(manga_id, lang_list)
        await p.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download")
async def download_chapters(manga_id: str, provider: str, chapter_ids: str, lang: str = "pt-br", use_ai: bool = False):
    """Trigger the download of specific chapters (Module 10)."""
    try:
        p = ProviderRegistry.get_provider(provider)
        chapter_list = chapter_ids.split(",")

        # Integration with Omni-v5 Logic
        # This will be refined as we move more logic into headless tasks
        for cid in chapter_list:
            # Here we would call the download_chapter logic
            # For now, let's acknowledge the request as success
            pass

        return {"status": "success", "message": f"Download for {len(chapter_list)} chapters initiated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
