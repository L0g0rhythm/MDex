import os
from pathlib import Path

# --- Directory Structures ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Soberania de Caminhos v3.8.2: Forçar pasta de sistema
# Soberania de Caminhos v3.8.4: Forçar pasta de sistema absoluta
DOWNLOAD_DIR = Path(os.path.expanduser("~/Downloads/MDex")).absolute()
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR = (BASE_DIR / ".cache").absolute()
CACHE_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = (BASE_DIR / "settings.json").absolute()

# --- MangaDex API ---
MANGADEX_API_URL = "https://api.mangadex.org"
AUTH_API_URL = "https://auth.mangadex.org"

# --- Performance & Safety ---
MAX_CONCURRENT_DOWNLOADS = 10  # Hardware Efficiency Limit
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
