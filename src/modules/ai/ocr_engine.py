import easyocr
import logging
from pathlib import Path
import numpy as np
from PIL import Image

class OCREngine:
    """Local OCR Engine for extracting text from manga panels (Module 25)."""

    def __init__(self, languages: list[str] = ['en']):
        # Module 25: AI Security - Using a local model to ensure data sovereignty.
        logging.info(f"Initializing EasyOCR with languages: {languages}")
        self.reader = easyocr.Reader(languages)

    def extract_text(self, image_path: Path) -> list[dict]:
        """ Extracts text and bounding boxes from an image. """
        try:
            # Convert PIL Image to numpy array for EasyOCR
            with Image.open(image_path) as img:
                img_np = np.array(img)

            results = self.reader.readtext(img_np)
            return [
                {
                    "box": res[0],
                    "text": res[1],
                    "confidence": res[2]
                }
                for res in results
            ]
        except Exception as e:
            msg = f"OCR Error on {Path(image_path).name}: {e}"
            logging.error(msg)
            return []
