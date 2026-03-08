from fastapi import FastAPI, HTTPException
from typing import List, Optional
from src.api.provider_registry import ProviderRegistry
from pydantic import BaseModel

app = FastAPI(title="MDex Omni-v5 API")

class MangaResult(BaseModel):
    id: str
    title: str
    provider: str

@app.get("/search/all", response_model=List[MangaResult])
async def search_all(q: str):
    try:
        return await ProviderRegistry.search_all(q)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search", response_model=List[MangaResult])
async def search(q: str, provider: Optional[str] = "mangadex"):
    try:
        p = ProviderRegistry.get_provider(provider)
        results = await p.search(q)
        await p.close()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/providers")
def list_providers():
    return ProviderRegistry.list_providers()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
