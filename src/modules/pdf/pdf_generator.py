from fpdf import FPDF
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from src.core.config import ASSUMED_DPI

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
            if img.width > 10000 or img.height > 10000:
                continue

            # Module 25: AI Privacy & Security
            img = img.convert("RGB")

            if ocr_engine and translator:
                # 1. OCR Extraction
                ocr_results = ocr_engine.extract_text(img_path)

                # 2. Translation & Overlay
                draw = ImageDraw.Draw(img)
                # Note: For production, we would use a more sophisticated 'inpainting' or better font handling.
                # For this 'Omni-v5' foundation, we use standard PIL drawing.
                for res in ocr_results:
                    box = res["box"]
                    original_text = res["text"]
                    translated_text = translator.translate(original_text)

                    # Coordinates: EasyOCR returns [[x,y],[x,y],[x,y],[x,y]]
                    p1, p2, p3, p4 = box
                    left, top = p1[0], p1[1]
                    right, bottom = p3[0], p3[1]

                    # Simple Overlay (White box + Black text)
                    draw.rectangle([left, top, right, bottom], fill="white")
                    draw.text((left, top), translated_text, fill="black")

            w_px, h_px = img.size
            dpi = img.info.get('dpi', (ASSUMED_DPI, ASSUMED_DPI))
            w_pt = w_px * 72.0 / dpi[0]
            h_pt = h_px * 72.0 / dpi[1]

            orientation = 'L' if w_pt > h_pt else 'P'
            pdf.add_page(orientation=orientation, format=(w_pt, h_pt))

            # Save temporary "clean" image for PDF inclusion
            temp_img_path = img_path.with_suffix(".tmp.jpg")
            img.save(temp_img_path, "JPEG", quality=95)
            pdf.image(temp_img_path, x=0, y=0, w=w_pt, h=h_pt)

            if temp_img_path.exists():
                temp_img_path.unlink()

    pdf.output(str(output_pdf))
    return output_pdf
