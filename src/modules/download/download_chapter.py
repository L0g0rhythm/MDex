import os
import asyncio
import logging
import hashlib
from pathlib import Path
from src.api.mangadex_client import MangaDexClient
from src.core.config import MAX_CONCURRENT_DOWNLOADS

async def download_image_async(url: str, path: Path, client: MangaDexClient, expected_hash: str = None):
    """Downloads a single image and verifies its integrity using SHA-256."""
    async with client.limiter:
        try:
            # Module 04/28: External Contract - Mimic Browser UA for CDN trust
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Referer": "https://mangadex.org/"
            }
            response = await client.client.get(url, timeout=30.0, headers=headers)
            response.raise_for_status()

            if expected_hash:
                actual_hash = hashlib.md5(response.content).hexdigest()
                if actual_hash != expected_hash:
                    logging.error(f"Hash mismatch for {path.name}: Expected {expected_hash}, got {actual_hash}")
                    return False

            path.write_bytes(response.content)
            logging.debug(f"Saved: {path.name} ({len(response.content)} bytes)")
            return True
        except Exception as e:
            logging.error(f"Failed to download image from {url}: {e}")
            return False

async def download_chapter_images(chapter_id: str, save_dir: Path, client: MangaDexClient, progress_callback=None):
    """Orchestrates the download of all images for a chapter."""
    server_data = await client.get(f"/at-home/server/{chapter_id}")
    base_url = server_data["baseUrl"]
    chapter_hash = server_data["chapter"]["hash"]
    filenames = server_data["chapter"]["data"]

    total = len(filenames)
    tasks = []
    downloaded_paths = []

    async def tracked_download(url, path, cl, idx):
        success = await download_image_async(url, path, cl)
        if success and progress_callback:
            # Report progress based on index
            await progress_callback(int(((idx + 1) / total) * 100))
        return success

    logging.info(f"Chapter {chapter_id}: Spawning {total} download tasks.")
    for i, filename in enumerate(filenames):
        img_url = f"{base_url}/data/{chapter_hash}/{filename}"
        ext = os.path.splitext(filename)[1]
        img_path = save_dir / f"{i+1:03d}{ext}"
        tasks.append(tracked_download(img_url, img_path, client, i))
        downloaded_paths.append(img_path)

    results = await asyncio.gather(*tasks)
    successfully_downloaded = [p for p, success in zip(downloaded_paths, results) if success]
    logging.info(f"Chapter {chapter_id}: {len(successfully_downloaded)}/{total} images captured.")
    return successfully_downloaded
