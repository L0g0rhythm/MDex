import argostranslate.package
import argostranslate.translate
import logging
from typing import Optional

class TranslationEngine:
    """Intelligent Local Translation Engine (Module 25)."""

    def __init__(self, from_code: str = "en", to_code: str = "pt"):
        self.from_code = from_code
        self.to_code = to_code
        self.is_active = from_code != to_code

        if self.is_active:
            self._ensure_packages()
        else:
            logging.info("Source and target languages are identical. Translation engine standby.")

    def _ensure_packages(self):
        """Checks and downloads translation models if not present."""
        try:
            # Singleton-like check to avoid redundant model loading
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = list(filter(lambda x: x.code == self.from_code, installed_languages))
            to_lang = list(filter(lambda x: x.code == self.to_code, installed_languages))

            if not from_lang or not to_lang:  # pragma: no cover
                logging.info(f"Installing missing translation package: {self.from_code} -> {self.to_code}")
                argostranslate.package.update_package_index()
                available_packages = argostranslate.package.get_available_packages()
                package_to_install = next(
                    filter(
                        lambda x: x.from_code == self.from_code and x.to_code == self.to_code,
                        available_packages
                    )
                )
                argostranslate.package.install_from_path(package_to_install.download())

            # Pre-load the translation object
            self.translation = argostranslate.translate.get_translation_from_codes(self.from_code, self.to_code)
            logging.info(f"Omni-v5 Translation Engine active: {self.from_code} -> {self.to_code}")
        except Exception as e:
            logging.error(f"Failed to initialize translation: {e}")
            self.is_active = False

    def translate(self, text: str) -> str:
        """Translates text with chunking for large inputs (Module 25)."""
        if not self.is_active or not text.strip():
            return text
        
        try:
            # Argos Translate can struggle with extremely long single strings.
            # We split by max length to ensure reliability (M25).
            MAX_CHUNK_LENGTH = 1000
            chunks = [text[i:i + MAX_CHUNK_LENGTH] for i in range(0, len(text), MAX_CHUNK_LENGTH)]
            
            translated_chunks = []
            for chunk in chunks:
                translated_chunks.append(self.translation.translate(chunk))
            
            return "".join(translated_chunks)
        except Exception as e:
            logging.error(f"Translation Failure: {e}")
            return text
