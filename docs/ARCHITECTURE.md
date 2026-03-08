# MDex Omni-v5: Architecture Overview

MDex Omni-v5 is built on the **"One Function, One File"** principle, ensuring maximum modularity, testability, and maintainability.

## 🏗️ Core Architecture Components

### 1. Provider Registry (`src/api/provider_registry.py`)
The central hub for all manga providers. It uses a singleton pattern to manage and discover providers (currently specializing in MangaDex).

### 2. Base Provider Interface (`src/api/base_provider.py`)
An abstract contract that all providers must follow. This ensures that new providers can be added without changing the core or UI logic.
- `search(query)`
- `get_chapters(manga_id, languages)`
- `get_pages(chapter_id)`
- `close()`

### 3. Omni-Reader Engine (`src/modules/ai/`)
A multi-modal processing layer for enhancement and translation.
- **OCREngine**: Extracts text from images locally.
- **TranslationEngine**: Translates extracted text using Argos Translate models.
- **Levels of Processing**:
  - **Level 0**: Direct image-to-PDF.
  - **Level 1 (OCR)**: Image enhancement + Text extraction.
  - **Level 2 (Translation)**: Full translation + PDF injection.

### 4. Asynchronous Pipeline
Utilizes `asyncio.Semaphore` and `httpx.AsyncClient` for high-concurrency downloads without hitting API rate limits (compliant with MangaDex's 5req/s policy).

## 🛡️ Security Modules (L0g0rhythm Kernel)
- **M04**: Data integrity via SHA-256 hash verification on every downloaded image.
- **M14**: Traffic governance via dynamic rate limiting.
- **M25**: Privacy-first AI processing (Offline models only).

---
**Authority: L0g0rhythm | Kernel v3.5.8**
