import pytest
from src.api.provider_registry import ProviderRegistry
from src.api.providers.mangadex import MangaDexProvider
from src.core.localization import STRINGS, get_string

def test_list_providers():
    providers = ProviderRegistry.list_providers()
    assert "mangadex" in providers

def test_get_provider_success():
    provider = ProviderRegistry.get_provider("mangadex")
    assert isinstance(provider, MangaDexProvider)

def test_get_provider_fail():
    with pytest.raises(ValueError, match="Provider unknown not found."):
        ProviderRegistry.get_provider("unknown")

def test_get_provider_case_insensitivity():
    provider = ProviderRegistry.get_provider("MangaDex")
    assert isinstance(provider, MangaDexProvider)
