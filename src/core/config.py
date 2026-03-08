import os
from pathlib import Path

# --- Directory Structures ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOWNLOAD_DIR = BASE_DIR / "Downloads"

# --- MangaDex API ---
MANGADEX_API_URL = "https://api.mangadex.org"
AUTH_API_URL = "https://auth.mangadex.org"

# --- Performance & Safety ---
MAX_CONCURRENT_DOWNLOADS = 5  # Semaphore limit
MAX_RETRIES = 5
RETRY_BACKOFF_FACTOR = 1.5
CHAPTER_DOWNLOAD_DELAY = 0.3  # Seconds between chapter metadata calls
CHAPTERS_PER_BATCH = 100 # Standard batch for pagination

# --- PDF Configuration ---
ASSUMED_DPI = 72
PDF_UNIT = "pt"

# --- UI Configuration ---
THEME_COLOR = "cyan"
ERROR_COLOR = "red"
SUCCESS_COLOR = "green"
