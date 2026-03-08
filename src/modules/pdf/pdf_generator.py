from fpdf import FPDF
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from src.core.config import ASSUMED_DPI
import logging

logger = logging.getLogger("mdex.pdf")

def create_pdf_from_images(
    image_paths: list[Path],
    output_pdf: Path,
    ocr_engine=None,
    translator=None
):
    """Generates a high-quality PDF, optionally with OCR and translation (Module 25)."""
    pdf = FPDF(unit="pt")

    for img_path in image_paths:
        with Image.open(img_path) as img:
            # Module 23: Resource Safety
            if img.width > 10000 or img.height > 10000:  # pragma: no cover
                continue  # pragma: no cover

            # Module 25: AI Privacy & Security - Strip metadata by creating a new image (M25)
            # This ensures no EXIF or other hidden data is leaked in the final PDF
            img_clean = Image.new("RGB", img.size)
            img_clean.paste(img.convert("RGB"))

            if ocr_engine and translator:
                # 1. OCR Extraction
                ocr_results = ocr_engine.extract_text(img_path)

                # 2. Translation & Overlay
                draw = ImageDraw.Draw(img_clean)
                # Note: For production, we would use a more sophisticated 'inpainting' or better font handling.
                # For this 'Omni-v5' foundation, we use standard PIL drawing.
                for res in ocr_results:
                    conf = res.get("confidence", 0)
                    if conf < 0.2: continue # Ignore noise (M21: Quality)

                    box = res["box"]
                    original_text = res["text"]
                    translated_text = translator.translate(original_text)

                    # Normalize to ensure left <= right and top <= bottom (Module 21: Quality)
                    xs = [p[0] for p in box]
                    ys = [p[1] for p in box]
                    left, top = min(xs), min(ys)
                    right, bottom = max(xs), max(ys)

                    # 3. Premium Overlay: White background box + High-contrast black text
                    # Draw a solid white box to cover the original text (Inpainting v1)
                    # Add a small padding to the box
                    pad = 2
                    draw.rectangle([left-pad, top-pad, right+pad, bottom+pad], fill="white", outline="white")
                    
                    # Draw the translated text
                    # Note: In a real production system, we'd calculate font size to fit the box
                    draw.text((left, top), translated_text.upper(), fill="black")

            w_px, h_px = img_clean.size
            dpi = img.info.get('dpi', (ASSUMED_DPI, ASSUMED_DPI))
            w_pt = w_px * 72.0 / dpi[0]
            h_pt = h_px * 72.0 / dpi[1]

            orientation = 'L' if w_pt > h_pt else 'P'
            pdf.add_page(orientation=orientation, format=(w_pt, h_pt))

            # Save temporary "clean" image for PDF inclusion
            temp_img_path = img_path.with_suffix(".tmp.jpg")
            img_clean.save(temp_img_path, "JPEG", quality=95)
            pdf.image(temp_img_path, x=0, y=0, w=w_pt, h=h_pt)

            if temp_img_path.exists():
                temp_img_path.unlink()

    logger.info(f"Outputting PDF to {output_pdf}")
    pdf.output(str(output_pdf))
    if output_pdf.exists():
        logger.info(f"PDF successfully created: {output_pdf.name} ({output_pdf.stat().st_size} bytes)")
    else:
        logger.error(f"PDF creation failed silently: {output_pdf}")
    return output_pdf
