from typing import Dict, Type
from src.api.base_provider import BaseProvider
from src.api.providers.mangadex import MangaDexProvider

class ProviderRegistry:
    """Registry for manga providers to allow dynamic discovery (Module 03)."""

    _providers: Dict[str, Type[BaseProvider]] = {
        "mangadex": MangaDexProvider
    }

    @classmethod
    def get_provider(cls, name: str) -> BaseProvider:
        provider_class = cls._providers.get(name.lower())
        if not provider_class:
            raise ValueError(f"Provider {name} not found.")
        return provider_class()

    @classmethod
    async def search_all(cls, query: str) -> List[Dict[str, Any]]:
        """Search across all registered providers in parallel."""
        tasks = []
        for name, provider_class in cls._providers.items():
            instance = provider_class()
            tasks.append(instance.search(query))
            # Note: For production, we should handle provider closing better
            # but for this aggregation, we return the results first.

        results = await asyncio.gather(*tasks, return_exceptions=True)

        flat_results = []
        for res in results:
            if isinstance(res, list):
                flat_results.extend(res)
            elif isinstance(res, Exception):
                logging.error(f"Provider search error: {res}")

        return flat_results

    @classmethod
    def list_providers(cls) -> List[str]:
        return list(cls._providers.keys())
