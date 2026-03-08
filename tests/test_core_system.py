import pytest
import logging
from unittest.mock import patch, MagicMock
from src.core.logger import setup_logger
from src.core.config import DOWNLOAD_DIR
from src.core.localization import get_string, STRINGS
from src.core.rate_limiter import RateLimiter

# --- Logger Tests ---
def test_logger_setup_rotation():
    with patch("logging.basicConfig") as mock_bc:
        with patch("logging.getLogger") as mock_get:
            mock_root = MagicMock()
            mock_root.handlers = []
            mock_get.return_value = mock_root
            setup_logger()
            # If no handlers, basicConfig should be called
            assert mock_bc.called

def test_logger_setup_existing_handlers():
    l1 = setup_logger("SharedLogger")
    l2 = setup_logger("SharedLogger")
    assert l1 == l2

# --- Config & Assets ---
def test_config_paths():
    assert DOWNLOAD_DIR.name == "Downloads"

# --- Localization ---
def test_localization_strings():
    assert get_string("manga_title_prompt", "en") == STRINGS["en"]["manga_title_prompt"]
    # Fallback check
    assert get_string("non_existent", "en") == "non_existent"

# --- Rate Limiter ---
@pytest.mark.asyncio
async def test_rate_limiter_logic():
    limiter = RateLimiter(concurrent_limit=10)
    # Just verify it doesn't crash e.g. on __aenter__
    async with limiter:
        assert True
