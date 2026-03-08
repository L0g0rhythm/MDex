from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
from pydantic import BaseModel
import json
import asyncio
import logging
import shutil
from pathlib import Path

# Project Imports
from src.api.provider_registry import ProviderRegistry
from src.modules.download.download_chapter import download_chapter_images
from src.modules.pdf.pdf_generator import create_pdf_from_images
from src.modules.ai.ocr_engine import OCREngine
from src.modules.ai.translator import TranslationEngine
from src.core.config import DOWNLOAD_DIR
from src.core.logger import setup_logger

app = FastAPI(title="MDex Singularity API", version="1.0.0")

# Setup Logger
logger = logging.getLogger("mdex.api")

# Module 22: Observability & Resilience - Real-time Progress Tracking
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.warning(f"Failed to send websocket message: {e}")
                pass

manager = ConnectionManager()

# Module 13: Frontend Client Security - Zero Trust CORS (M13)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class DownloadRequest(BaseModel):
    manga_id: str
    chapter_ids: List[str]
    provider: str = "mangadex"
    target_lang: str = "pt-br"
    use_ai: bool = False

# --- RESTful API v1 Routes ---

@app.get("/api/v1/manga/search")
async def search_manga_route(title: str):
    """Searches for manga across all providers (M28)."""
    try:
        results = await ProviderRegistry.search_all(title)
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/manga/{manga_id}/chapters")
async def get_chapters_route(manga_id: str, provider: str = "mangadex"):
    """Retrieves chapters for a specific manga (M28)."""
    try:
        p = ProviderRegistry.get_provider(provider)
        # Default languages for v1
        results = await p.get_chapters(manga_id, ["pt-br", "en"])
        await p.close()
        return results
    except Exception as e:
        logger.error(f"Failed to fetch chapters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/download/start")
async def start_download_route(request: DownloadRequest):
    """Initiates the download process in background (M10)."""
    try:
        asyncio.create_task(
            process_downloads(
                request.manga_id, 
                request.provider, 
                request.chapter_ids, 
                request.target_lang, 
                request.use_ai
            )
        )
        return {"status": "success", "message": f"Download initiated for {len(request.chapter_ids)} chapters."}
    except Exception as e:  # pragma: no cover
        logger.error(f"Download initiation failed: {e}")  # pragma: no cover
        raise HTTPException(status_code=500, detail=str(e))  # pragma: no cover

@app.websocket("/api/v1/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time progress and logging bridge (M22)."""
    await manager.connect(websocket)  # pragma: no cover
    try:  # pragma: no cover
        while True:  # pragma: no cover
            await websocket.receive_text()  # pragma: no cover
    except WebSocketDisconnect:  # pragma: no cover
        manager.disconnect(websocket)  # pragma: no cover

# --- Background Processor ---

async def process_downloads(manga_id: str, provider_name: str, chapter_ids: List[str], target_lang: str, use_ai: bool):
    """Background engine for secure acquisition and processing (M10)."""
    try:
        provider = ProviderRegistry.get_provider(provider_name)
        total = len(chapter_ids)
        manga_title = f"Manga_{manga_id}"
        manga_path = DOWNLOAD_DIR / manga_title
        manga_path.mkdir(parents=True, exist_ok=True)

        ocr_engine = None
        translator = None
        if use_ai:
             ocr_engine = OCREngine(languages=['en'])
             translator = TranslationEngine(from_code='en', to_code=target_lang.split('-')[0])

        for idx, cid in enumerate(chapter_ids):
            await manager.broadcast({
                "type": "progress",
                "chapter_id": cid,
                "percentage": int((idx / total) * 100),
                "status": f"Downloading Chapter {cid}..."
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
                "percentage": int(((idx + 1) / total) * 100),
                "status": "Completed"
            })

        await manager.broadcast({"type": "complete", "message": "All downloads finished successfully."})
        await provider.close()
    except Exception as e:
        logger.error(f"Background task failure: {e}")
        await manager.broadcast({"type": "log", "message": f"Error: {str(e)}"})

if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
