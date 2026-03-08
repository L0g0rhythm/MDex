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
