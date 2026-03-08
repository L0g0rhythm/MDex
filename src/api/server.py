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

from src.modules.download.download_chapter import download_chapter_images
from src.modules.pdf.pdf_generator import create_pdf_from_images
from src.modules.ai.ocr_engine import OCREngine
from src.modules.ai.translator import TranslationEngine
from src.core.config import DOWNLOAD_DIR
from pathlib import Path
import shutil

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
    asyncio.create_task(process_downloads(manga_id, provider, chapter_list, lang, use_ai))  # pragma: no cover
    return {"status": "queued", "count": len(chapter_list)}

async def process_downloads(manga_id: str, provider_name: str, chapter_ids: List[str], target_lang: str, use_ai: bool):
    """Background task to handle downloads and broadcast progress via WebSockets."""
    try:
        provider = ProviderRegistry.get_provider(provider_name)
        total = len(chapter_ids)

        # We need a manga title for the directory. In a real scenario, we'd fetch it.
        # For simplicity in v5, we'll use the ID as a placeholder or fetch from provider.
        manga_title = f"Manga_{manga_id}"
        manga_path = DOWNLOAD_DIR / manga_title
        manga_path.mkdir(parents=True, exist_ok=True)

        ocr_engine = None
        translator = None
        if use_ai:
             # Default to en -> target_lang for AI init in server context
             ocr_engine = OCREngine(languages=['en'])
             translator = TranslationEngine(from_code='en', to_code=target_lang.split('-')[0])

        for idx, cid in enumerate(chapter_ids):
            await manager.broadcast({
                "type": "progress",
                "chapter_id": cid,
                "progress": int((idx / total) * 100),
                "status": f"Baixando Capítulo {cid} ({idx+1}/{total})"
            })

            chap_dir = manga_path / f"Chapter_{cid}"
            chap_dir.mkdir(exist_ok=True)

            images = await download_chapter_images(cid, chap_dir, provider)

            if images:
                pdf_path = manga_path / f"Chapter_{cid}.pdf"
                create_pdf_from_images(images, pdf_path, ocr_engine, translator)
                shutil.rmtree(chap_dir)

            await manager.broadcast({
                "type": "progress",
                "chapter_id": cid,
                "progress": int(((idx + 1) / total) * 100),
                "status": f"Capítulo {cid} concluído"
            })

        await manager.broadcast({"type": "complete", "message": "Todos os downloads concluídos."})
        await provider.close()
    except Exception as e:
        await manager.broadcast({"type": "error", "message": str(e)})

if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
