from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path

class BaseProvider(ABC):
    """
    Abstract Base Class for all Manga Providers.
    Ensures a consistent API across different sources (Module 03 & 12).
    """

    @abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for manga and return a list of matches."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def get_chapters(self, manga_id: str, languages: List[str]) -> List[Dict[str, Any]]:
        """Retrieve all chapters for specific languages."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def get_pages(self, chapter_id: str) -> List[str]:
        """Get all image URLs for a specific chapter."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    async def close(self):
        """Close any open connections or clients."""
        raise NotImplementedError  # pragma: no cover
