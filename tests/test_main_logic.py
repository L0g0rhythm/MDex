import pytest
import sys
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

# Mock dependencies used in main.py BEFORE import
sys.modules["inquirer"] = MagicMock()

from src.main import async_main

@pytest.mark.asyncio
async def test_async_main_flow():
    # Mock everything to avoid real I/O and reach 100% coverage
    with patch("inquirer.list_input", return_value="Português (Brasil)"), \
         patch("src.main.console.input") as mock_input, \
         patch("src.main.search_manga", new_callable=AsyncMock) as mock_search, \
         patch("src.main.get_manga_chapters", new_callable=AsyncMock) as mock_get_chaps, \
         patch("src.main.parse_chapter_selection") as mock_select, \
         patch("src.main.download_chapter_images", new_callable=AsyncMock) as mock_dl, \
         patch("src.main.create_pdf_from_images") as mock_pdf, \
         patch("src.main.shutil.rmtree"), \
         patch("src.main.console.status"):

        # Inputs for: manga title, selection, use_ai toggle
        mock_input.side_effect = ["Solo Leveling", "1", "n"]

        mock_search.return_value = {"id": "m1", "title": "Solo Leveling"}
        mock_get_chaps.return_value = [{"id": "c1", "number": "1", "display": "1", "lang": "pt-br"}]
        mock_select.return_value = [{"id": "c1", "number": "1", "display": "1", "lang": "pt-br"}]
        mock_dl.return_value = [Path("img1.jpg")]

        # Run the main async entry point
        await async_main()

        assert mock_search.called
        assert mock_dl.called
        assert mock_pdf.called

@pytest.mark.asyncio
async def test_async_main_no_results():
    with patch("inquirer.list_input", return_value="English"), \
         patch("src.main.console.input", return_value="Unknown"), \
         patch("src.main.search_manga", new_callable=AsyncMock) as mock_search, \
         patch("src.main.console.status"):

        mock_search.return_value = None
        await async_main()
        assert mock_search.called

@pytest.mark.asyncio
async def test_async_main_ai_path():
    # Test path with AI/OCR enabled
    with patch("inquirer.list_input", return_value="English"), \
         patch("src.main.console.input") as mock_input, \
         patch("src.main.search_manga", new_callable=AsyncMock) as mock_search, \
         patch("src.main.get_manga_chapters", new_callable=AsyncMock) as mock_get_chaps, \
         patch("src.main.parse_chapter_selection") as mock_select, \
         patch("src.main.download_chapter_images", new_callable=AsyncMock) as mock_dl, \
         patch("src.main.create_pdf_from_images") as mock_pdf, \
         patch("src.main.shutil.rmtree"), \
         patch("src.main.console.status"), \
         patch("src.modules.ai.ocr_engine.OCREngine", new_callable=MagicMock), \
         patch("src.modules.ai.translator.TranslationEngine", new_callable=MagicMock):

        # manga name, range, use_ai='s'
        mock_input.side_effect = ["Manga", "1", "s"]

        mock_search.return_value = {"id": "m1", "title": "Manga"}
        mock_get_chaps.return_value = [{"id": "c1", "number": "1", "display": "1", "lang": "en"}]
        mock_select.return_value = [{"id": "c1", "number": "1", "display": "1", "lang": "en"}]
        mock_dl.return_value = [Path("img1.jpg")]

        await async_main()
        assert mock_pdf.called
