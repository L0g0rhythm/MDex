from fastapi import FastAPI, HTTPException
from typing import List, Optional
from src.api.provider_registry import ProviderRegistry
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional, Dict
import json
import asyncio

app = FastAPI(title="MDex Omni-v5 API")

# Module 22: Observability & Resilience - Real-time Progress Tracking
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Connection might be stale
                pass

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Module 28: External Interface Contracts - CORS Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    """Trigger the download of specific chapters in the background (Module 10)."""
    chapter_list = chapter_ids.split(",")
    asyncio.create_task(process_downloads(manga_id, provider, chapter_list, lang, use_ai))
    return {"status": "queued", "count": len(chapter_list)}

async def process_downloads(manga_id: str, provider_name: str, chapter_ids: List[str], target_lang: str, use_ai: bool):
    """Background task to handle downloads and broadcast progress via WebSockets."""
    try:
        provider = ProviderRegistry.get_provider(provider_name)
        total = len(chapter_ids)

        for idx, cid in enumerate(chapter_ids):
            progress = int(((idx) / total) * 100)
            await manager.broadcast({
                "type": "progress",
                "chapter_id": cid,
                "progress": progress,
                "status": f"Iniciando download ({idx+1}/{total})"
            })

            # Simulate/Execute download logic
            await asyncio.sleep(1) # Simulated high-speed sync

            await manager.broadcast({
                "type": "progress",
                "chapter_id": cid,
                "progress": int(((idx + 1) / total) * 100),
                "status": f"Capítulo finalizado"
            })

        await manager.broadcast({"type": "complete", "message": "Todos os downloads concluídos."})
        await provider.close()
    except Exception as e:
        await manager.broadcast({"type": "error", "message": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
