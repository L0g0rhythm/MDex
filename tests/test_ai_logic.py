import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock heavy dependencies before importing modules that use them
sys.modules["easyocr"] = MagicMock()
sys.modules["argostranslate"] = MagicMock()
sys.modules["argostranslate.package"] = MagicMock()
sys.modules["argostranslate.translate"] = MagicMock()

from pathlib import Path
from src.modules.ai.ocr_engine import OCREngine
from src.modules.ai.translator import TranslationEngine

@patch("easyocr.Reader")
def test_ocr_engine_extraction(mock_reader_class, tmp_path):
    mock_reader = MagicMock()
    mock_reader.readtext.return_value = [
        ([[10, 10], [50, 10], [50, 30], [10, 30]], "Hello", 0.95)
    ]
    mock_reader_class.return_value = mock_reader

    engine = OCREngine(languages=['en'])
    img_path = tmp_path / "test.png"
    from PIL import Image
    Image.new('RGB', (10, 10)).save(img_path)

    results = engine.extract_text(img_path)
    assert len(results) == 1
    assert results[0]["text"] == "Hello"

@patch("argostranslate.translate.get_installed_languages")
@patch("argostranslate.translate.get_translation_from_codes")
def test_translation_engine_logic(mock_get_trans, mock_get_langs):
    mock_lang_en = MagicMock()
    mock_lang_en.code = "en"
    mock_lang_pt = MagicMock()
    mock_lang_pt.code = "pt"
    mock_get_langs.return_value = [mock_lang_en, mock_lang_pt]

    mock_trans_obj = MagicMock()
    mock_trans_obj.translate.return_value = "Olá"
    mock_get_trans.return_value = mock_trans_obj

    # Bypass _ensure_packages for simple unit test
    with patch.object(TranslationEngine, '_ensure_packages'):
        engine = TranslationEngine(from_code="en", to_code="pt")
        engine.is_active = True
        engine.translation = mock_trans_obj
        assert engine.translate("Hello") == "Olá"

@patch("src.modules.ai.translator.argostranslate.package.get_available_packages")
@patch("src.modules.ai.translator.argostranslate.package.update_package_index")
@patch("src.modules.ai.translator.argostranslate.translate.get_installed_languages")
@patch("src.modules.ai.translator.argostranslate.translate.get_translation_from_codes")
def test_translation_engine_package_install(mock_get_trans, mock_get_langs, mock_update, mock_get_avail):
    # Test path where languages are NOT installed
    mock_get_langs.return_value = [] # Nothing installed
    
    mock_package = MagicMock()
    mock_package.from_code = "en"
    mock_package.to_code = "pt"
    mock_package.download.return_value = "/tmp/fake.pkg"
    
    mock_get_avail.return_value = [mock_package]
    mock_get_trans.return_value = MagicMock()
    
    with patch("src.modules.ai.translator.argostranslate.package.install_from_path") as mock_install:
        engine = TranslationEngine(from_code="en", to_code="pt")
        assert mock_update.called
        assert mock_install.called
        assert engine.is_active

def test_translation_failure_exception():
    # Bypass init
    with patch.object(TranslationEngine, '_ensure_packages'):
        engine = TranslationEngine(from_code="en", to_code="pt")
        engine.is_active = True
        engine.translation = MagicMock()
        engine.translation.translate.side_effect = Exception("Service Down")
        
        result = engine.translate("Hello")
        assert result == "Hello" # Should return original text on failure

def test_translation_engine_inactive():
    engine = TranslationEngine(from_code="en", to_code="en")
    assert engine.is_active is False
    assert engine.translate("Hello") == "Hello"

def test_ocr_engine_extraction_failure():
    with patch("easyocr.Reader") as mock_reader_class:
        mock_reader = MagicMock()
        mock_reader.readtext.side_effect = Exception("Read Error")
        mock_reader_class.return_value = mock_reader
        engine = OCREngine()
        # Ensure it hits the except block in extract_text
        results = engine.extract_text("path/to/img.jpg")
        assert results == []
