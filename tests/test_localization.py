import pytest
import asyncio
from src.core.localization import STRINGS, get_string

def test_localization_keys_consistency():
    """Ensure all languages have the same keys."""
    keys_pt = set(STRINGS["pt-br"].keys())
    keys_en = set(STRINGS["en"].keys())
    keys_es = set(STRINGS["es"].keys())

    assert keys_pt == keys_en
    assert keys_pt == keys_es

def test_get_string_fallback():
    """Test localization fallback logic."""
    # Test valid key
    assert get_string("select_language_prompt", "pt-br") == STRINGS["pt-br"]["select_language_prompt"]
    # Test invalid language fallback to English
    assert get_string("select_language_prompt", "fr") == STRINGS["en"]["select_language_prompt"]
    # Test invalid key
    assert get_string("non_existent_key", "en") == "non_existent_key"
