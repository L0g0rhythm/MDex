import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.api.provider_registry import ProviderRegistry

@pytest.mark.asyncio
async def test_search_all_parallel_logic():
    # Mocking providers in the registry
    mock_p1 = AsyncMock()
    mock_p1.search.return_value = [{"id": "p1", "title": "Manga 1", "provider": "p1"}]

    with patch.dict(ProviderRegistry._providers, {"p1": lambda: mock_p1}, clear=True):
        results = await ProviderRegistry.search_all("query")
        assert len(results) == 1
        assert results[0]["title"] == "Manga 1"

def test_list_providers_registry():
    with patch.dict(ProviderRegistry._providers, {"p1": None, "p2": None}, clear=True):
        assert ProviderRegistry.list_providers() == ["p1", "p2"]
