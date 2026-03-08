import logging
import httpx
import asyncio
import json
import shutil
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Project Imports
from src.api.provider_registry import ProviderRegistry
from src.modules.download.download_chapter import download_chapter_images
from src.modules.pdf.pdf_generator import create_pdf_from_images
from src.modules.ai.ocr_engine import OCREngine
from src.modules.ai.translator import TranslationEngine
from src.core.config import DOWNLOAD_DIR, CACHE_DIR, SETTINGS_FILE
from src.core.logger import setup_logger
import hashlib
from PIL import Image
import io

# Global Settings State (v3.7.0)
DEFAULT_SETTINGS = {
    "download_dir": str(DOWNLOAD_DIR),
    "use_ai": False,
    "language": "pt",
    "version": "v3.7.2-Singularity",
    "creator": "L0g0rhythm Authority Core",
    "site": "https://www.l0g0rhythm.com.br/",
    "repo": "https://github.com/L0g0rhythm/MDex"
}

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            return {**DEFAULT_SETTINGS, **json.loads(SETTINGS_FILE.read_text())}
        except: return DEFAULT_SETTINGS
    else:
        # Physical creation v3.7.2
        SETTINGS_FILE.write_text(json.dumps(DEFAULT_SETTINGS, indent=4))
        return DEFAULT_SETTINGS

current_settings = load_settings()

app = FastAPI(title="MDex Singularity API", version="1.0.0")

# Setup Logger
logger = logging.getLogger("mdex.api")
# Suppress asyncio socket noise on Windows (Proactor loop reset)
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

# In-memory cache for covers (Absolute Efficiency v3.5.8)
cover_cache: Dict[str, bytes] = {}

# Activity Monitor (M10: Financial & Concurrency Integrity)
active_tasks: Dict[str, asyncio.Task] = {}

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
                logger.debug(f"Failed to send websocket message: {e}")
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
    manga_title: str
    chapter_ids: List[str]
    chapter_titles: List[str] = []
    provider: str = "mangadex"
    target_lang: str = "pt-br"
    use_ai: bool = False
    combine_pdf: bool = False

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
async def get_chapters_route(manga_id: str, lang: str = "pt-br", provider: str = "mangadex"):
    """Retrieves chapters with preferred language (M28)."""
    try:
        p = ProviderRegistry.get_provider(provider)
        # Use provided lang + common fallbacks
        lang_map = {"pt": "pt-br", "en": "en", "es": "es"}
        target = lang_map.get(lang.lower(), lang.lower())
        results = await p.get_chapters(manga_id, [target])
        await p.close()
        return results
    except Exception as e:
        logger.error(f"Failed to fetch chapters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/download/start")
async def start_download_route(request: DownloadRequest):
    """Initiates the download process in background (M10)."""
    task_id = f"{request.manga_id}_{'_'.join(request.chapter_ids[:3])}" # Traceable ID
    
    task = asyncio.create_task(
        process_downloads(
            request.manga_id,
            request.manga_title,
            request.provider, 
            request.chapter_ids, 
            request.chapter_titles,
            request.target_lang, 
            request.use_ai,
            request.combine_pdf
        )
    )
    active_tasks[task_id] = task
    
    return {"status": "success", "message": f"Download iniciado.", "task_id": task_id}

@app.post("/api/v1/download/cancel")
async def cancel_download_route(manga_id: str):
    """Aborts active downloads for a manga (M10)."""
    cancelled_count = 0
    for tid, task in list(active_tasks.items()):
        if tid.startswith(manga_id):
            task.cancel()
            del active_tasks[tid]
            cancelled_count += 1
    
    return {"status": "cancelled", "count": cancelled_count}

@app.websocket("/api/v1/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    """Real-time progress and logging bridge (M22)."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except (WebSocketDisconnect, ConnectionResetError):
        manager.disconnect(websocket)
    except Exception as e:
        logger.debug(f"WebSocket closed softly: {e}")
        manager.disconnect(websocket)

# --- Settings & Metadata Routes (v3.7.0) ---

@app.get("/api/v1/system/select-folder")
async def select_folder():
    """Opens a native directory picker and returns the selected path."""
    if os.name == 'nt': # Windows
        # Script PowerShell Moderno (System.Windows.Forms) v3.9.0
        ps_script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$f = New-Object System.Windows.Forms.FolderBrowserDialog; "
            "$f.Description = 'Selecione a pasta de Downloads MDex'; "
            "$f.ShowNewFolderButton = $true; "
            "if ($f.ShowDialog() -eq 'OK') { $f.SelectedPath }"
        )
        cmd = f'powershell -NoProfile -Command "{ps_script}"'
        
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        path = stdout.decode('latin-1').strip() # Latin-1 covers potential accents in Windows paths
        if path:
            return {"path": path}
    return {"path": None}

@app.get("/api/v1/settings")
async def get_settings():
    global current_settings
    current_settings = load_settings() 
    return current_settings

@app.post("/api/v1/settings")
async def update_settings(new_settings: Dict[str, Any]):
    global current_settings
    current_settings.update(new_settings)
    SETTINGS_FILE.write_text(json.dumps(current_settings, indent=4))
    return current_settings

@app.get("/api/v1/about")
async def get_about():
    global current_settings
    current_settings = load_settings()
    return {
        "app": "MDex Singularity",
        "version": current_settings["version"],
        "creator": current_settings["creator"],
        "site": current_settings["site"],
        "repo": current_settings["repo"],
        "description": "Premium Manga Acquisition & Translation Engine"
    }

# --- Background Processor ---

async def process_downloads(manga_id: str, manga_title: str, provider_name: str, chapter_ids: List[str], chapter_titles: List[str], target_lang: str, use_ai: bool, combine_pdf: bool):
    try:
        provider = ProviderRegistry.get_provider(provider_name)
        
        # Use Dynamic Download Dir (v3.9.5)
        base_download_path = Path(current_settings["download_dir"])
        
        # Sanitize Manga Title for Folder Naming
        safe_manga_title = "".join([c for c in manga_title if c.isalnum() or c in (' ', '-', '_')]).strip()
        manga_path = base_download_path / safe_manga_title
        manga_path.mkdir(parents=True, exist_ok=True)

        ocr_cache_engine = {} # Cache engine pairs by source lang
        translator_cache = {}
        
        # Pre-fetch all chapter metadata once for the whole manga (M23: Stewardship)
        chapter_metadata_list = await provider.get_chapters(manga_id, [])
        chapter_metadata_map = {c["id"]: c for c in chapter_metadata_list}

        all_downloaded_images = []

        for idx, cid in enumerate(chapter_ids):
            # 1. Find original language from cache
            this_chapter = chapter_metadata_map.get(cid)
            source_lang = "en" # Default
            if this_chapter:
                source_lang = this_chapter["lang"][:2] # Convert pt-br -> pt, etc.
                if source_lang == "pt": source_lang = "pt" # Stay safe

            # 2. Dynamic AI Initialization (only if needed)
            chapter_ocr = None
            chapter_translator = None
            if use_ai:
                if source_lang not in ocr_cache_engine:
                    # Map common codes to OCR/Translator supported codes
                    ocr_lang = 'en' if source_lang in ['en', 'pt'] else source_lang
                    ocr_cache_engine[source_lang] = OCREngine(languages=[ocr_lang])
                    translator_cache[source_lang] = TranslationEngine(from_code=source_lang, to_code=target_lang.split('-')[0])
                
                chapter_ocr = ocr_cache_engine[source_lang]
                chapter_translator = translator_cache[source_lang]
            # Resolve Chapter Label (Title or Number)
            label = chapter_titles[idx] if idx < len(chapter_titles) else f"Chapter {cid}"
            safe_label = "".join([c for c in label if c.isalnum() or c in (' ', '-', '_')]).strip()

            await manager.broadcast({
                "type": "progress",
                "chapter_id": cid,
                "percentage": 10,
                "status": f"Iniciando {label}..."
            })

            chap_dir = manga_path / f"temp_{cid}"
            chap_dir.mkdir(exist_ok=True)

            async def progress_cb(pct):
                await manager.broadcast({
                    "type": "progress",
                    "chapter_id": cid,
                    "percentage": max(10, pct),
                    "status": "Capturando..." if pct < 100 else "Consolidando..."
                })

            images = await download_chapter_images(cid, chap_dir, provider.client, progress_callback=progress_cb)

            if images:
                if combine_pdf:
                    all_downloaded_images.extend(images)
                else:
                    pdf_path = manga_path / f"{safe_label}.pdf"
                    create_pdf_from_images(images, pdf_path, chapter_ocr, chapter_translator)
                    try:
                        shutil.rmtree(chap_dir)
                    except: pass
                
                await manager.broadcast({
                    "type": "progress",
                    "chapter_id": cid,
                    "percentage": 100,
                    "status": "Completo"
                })
            else:
                logger.error(f"Failed to download chapter {cid}")

        if combine_pdf and all_downloaded_images:
            combined_pdf_path = manga_path / f"{safe_manga_title}_Consolidado.pdf"
            create_pdf_from_images(all_downloaded_images, combined_pdf_path, chapter_ocr, chapter_translator)
            # Cleanup all temp dirs
            for cid in chapter_ids:
                try: shutil.rmtree(manga_path / f"temp_{cid}")
                except: pass

        await manager.broadcast({"type": "complete", "message": "Arquivos organizados com sucesso!"})
        await provider.close()
    except asyncio.CancelledError:
        logger.info(f"Download for manga {manga_id} cancelled by user.")
        await manager.broadcast({"type": "info", "message": "Operação Cancelada."})
    except Exception as e:
        logger.error(f"Background process failure: {e}")
        await manager.broadcast({"type": "error", "message": str(e)})

@app.get("/api/v1/manga/proxy/cover")
async def proxy_cover_route(url: str):
    if not url: return Response(status_code=400)
    
    # Generate unique hash for the URL
    url_hash = hashlib.md5(url.encode()).hexdigest()
    cache_path = CACHE_DIR / f"{url_hash}.webp"

    # 1. Memory Cache Check (Instant)
    if url in cover_cache:
        return Response(content=cover_cache[url], media_type="image/webp")
    
    # 2. Disk Cache Check (Persistent)
    if cache_path.exists():
        content = cache_path.read_bytes()
        cover_cache[url] = content # Populate memory cache
        return Response(content=content, media_type="image/webp")
    
    # 3. Network Fetch & Compression (Extreme Practicality v3.6.0)
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=15.0)
            if resp.status_code == 200:
                # Compress to WebP (Quality 60 for extreme space saving vs speed)
                img = Image.open(io.BytesIO(resp.content))
                img = img.convert("RGB")
                
                output = io.BytesIO()
                img.save(output, format="WEBP", quality=60, optimize=True)
                webp_content = output.getvalue()

                # Persist
                cache_path.write_bytes(webp_content)
                cover_cache[url] = webp_content
                
                return Response(content=webp_content, media_type="image/webp")
        except Exception as e:
            logger.error(f"Cover proxy failure: {e}")
            return Response(status_code=502)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
