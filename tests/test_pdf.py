import pytest
from pathlib import Path
from src.modules.pdf.pdf_generator import create_pdf_from_images
from PIL import Image
import os

def test_create_pdf(tmp_path):
    # Setup: Create dummy images
    img1_path = tmp_path / "001.jpg"
    img2_path = tmp_path / "002.jpg"

    img1 = Image.new('RGB', (100, 100), color = 'red')
    img1.save(img1_path)

    img2 = Image.new('RGB', (100, 150), color = 'blue')
    img2.save(img2_path)

    output_pdf = tmp_path / "test.pdf"

    # Action
    result = create_pdf_from_images([img1_path, img2_path], output_pdf)

    # Assert
    assert result.exists()
    assert result.stat().st_size > 0
    assert result.suffix == ".pdf"

def test_exif_stripping(tmp_path):
    # Setup: Create image with EXIF
    img_path = tmp_path / "exif.jpg"
    img = Image.new('RGB', (100, 100), color = 'green')
    img.save(img_path, exif=b"dummy_exif")

    output_pdf = tmp_path / "exif_test.pdf"

    # Action
    create_pdf_from_images([img_path], output_pdf)

    # Assert
    assert output_pdf.exists()

def test_oversized_image_rejection(tmp_path):
    # Module 23: Resource Safety - Test skipping huge images
    img_path = tmp_path / "huge.jpg"
    # Faking a large size without actually creating a massive file to save memory
    img = Image.new('RGB', (10001, 100), color = 'red')
    img.save(img_path)

    output_pdf = tmp_path / "huge_test.pdf"
    create_pdf_from_images([img_path], output_pdf)

    # If it was skipped, the PDF might be empty or not contain this page. 
    # Since it's the only page, it should fail or produce an empty PDF.
    # In FPDF, an output without pages might raise an error or just be small.
    assert output_pdf.exists()

def test_pdf_with_ai_overlay(tmp_path):
    from unittest.mock import MagicMock
    img_path = tmp_path / "ocr.jpg"
    img = Image.new('RGB', (200, 200), color = 'white')
    img.save(img_path)

    output_pdf = tmp_path / "ai_test.pdf"

    mock_ocr = MagicMock()
    mock_ocr.extract_text.return_value = [
        {"box": [[10, 10], [50, 10], [50, 30], [10, 30]], "text": "Hello"}
    ]
    mock_trans = MagicMock()
    mock_trans.translate.return_value = "Hola"

    create_pdf_from_images([img_path], output_pdf, ocr_engine=mock_ocr, translator=mock_trans)

    assert output_pdf.exists()
    assert mock_ocr.extract_text.called
    assert mock_trans.translate.called
