import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from pathlib import Path
from src.main import async_main

@pytest.mark.asyncio
async def test_main_cli_full_flow():
    mock_provider = AsyncMock()
    mock_provider.close = AsyncMock()
    
    with patch("src.main.inquirer.list_input", return_value="English"), \
         patch("src.main.console.input", side_effect=["Solo", "1", "n"]), \
         patch("src.main.ProviderRegistry.get_provider", return_value=mock_provider), \
         patch("src.main.search_manga", new_callable=AsyncMock, return_value={"id": "1", "title": "S"}), \
         patch("src.main.get_manga_chapters", new_callable=AsyncMock, return_value=[{"id": "c1", "number": "1", "lang": "en", "display": "1"}]), \
         patch("src.main.parse_chapter_selection", return_value=[{"id": "c1", "number": "1", "lang": "en", "display": "1"}]), \
         patch("src.main.download_chapter_images", new_callable=AsyncMock, return_value=[Path("p1.jpg")]), \
         patch("src.main.create_pdf_from_images"), \
         patch("src.main.shutil.rmtree"):
        
        await async_main()

@pytest.mark.asyncio
async def test_main_cli_empty_search():
    with patch("inquirer.list_input", return_value="English"), \
         patch("src.ui.terminal.console.input", side_effect=[""]):
        await async_main()

    mock_p = AsyncMock()
    mock_p.close = AsyncMock()
    with patch("inquirer.list_input", return_value="English"), \
         patch("src.ui.terminal.console.input", side_effect=["Solo"]), \
         patch("src.api.provider_registry.ProviderRegistry.get_provider", return_value=mock_p), \
         patch("src.modules.search.search_manga", new_callable=AsyncMock, return_value=None):
        await async_main()

@pytest.mark.asyncio
async def test_main_cli_no_chapters_found():
    mock_p = AsyncMock()
    mock_p.close = AsyncMock()
    with patch("inquirer.list_input", return_value="English"), \
         patch("src.ui.terminal.console.input", side_effect=["Solo"]), \
         patch("src.api.provider_registry.ProviderRegistry.get_provider", return_value=mock_p), \
         patch("src.modules.search.search_manga", new_callable=AsyncMock, return_value={"id": "1", "title": "S"}), \
         patch("src.modules.search.get_chapters.get_manga_chapters", new_callable=AsyncMock, return_value=[]):
        await async_main()

@pytest.mark.asyncio
async def test_main_cli_ai_flow():
    mock_p = AsyncMock()
    mock_p.close = AsyncMock()
    with patch("src.main.inquirer.list_input", return_value="English"), \
         patch("src.main.console.input", side_effect=["Solo", "1", "s"]), \
         patch("src.main.ProviderRegistry.get_provider", return_value=mock_p), \
         patch("src.main.search_manga", new_callable=AsyncMock, return_value={"id": "1", "title": "M"}), \
         patch("src.main.get_manga_chapters", new_callable=AsyncMock, return_value=[{"id": "c1", "number": "1", "lang": "pt-br", "display": "1"}]), \
         patch("src.main.parse_chapter_selection", return_value=[{"id": "c1", "number": "1", "lang": "pt-br", "display": "1"}]), \
         patch("src.main.download_chapter_images", new_callable=AsyncMock, return_value=[Path("p1.jpg")]), \
         patch("src.main.create_pdf_from_images"), \
         patch("src.main.shutil.rmtree") as mock_rm:
        from src.modules.ai.ocr_engine import OCREngine
        from src.modules.ai.translator import TranslationEngine
        with patch("src.main.OCREngine", return_value=MagicMock()), \
             patch("src.main.TranslationEngine", return_value=MagicMock()):
            await async_main()
            assert mock_rm.called

@pytest.mark.asyncio
async def test_terminal_ui_coverage():
    from src.ui.terminal import display_error, display_success
    with patch("src.ui.terminal.console.print") as mock_print:
        display_error("Test Error")
        display_success("Test Success")
        assert mock_print.called
