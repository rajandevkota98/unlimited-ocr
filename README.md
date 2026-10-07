# Unlimited OCR

High-performance OCR service built with FastAPI, designed with modular input sources, service orchestration, custom exception handling, and custom structured logging.

---

## Architecture Overview

```
unlimited-ocr/
├── core/
│   ├── __init__.py
│   ├── config.py                    # Environment & application settings
│   ├── exceptions.py                # Custom exception hierarchy & FastAPI handlers
│   └── logger.py                    # Colorized custom logger & log formatter
├── sources/
│   ├── __init__.py
│   ├── base.py                      # BaseSource abstract interface & payload
│   ├── file_source.py               # FileSource for multipart uploads
│   └── url_source.py                # URLSource for remote document retrieval
├── services/
│   ├── __init__.py
│   ├── base.py                      # BaseOCRService & OCRResult definitions
│   └── ocr_service.py               # Concrete OCR execution pipeline
├── app.py                           # FastAPI application entrypoint & routing
├── requirements.txt
└── .gitignore
```

---

## Key Features

1. **FastAPI Application (`app.py`)**:
   - Asynchronous request handling with lifespan lifecycle management.
   - Built-in timing & request correlation middleware.
   - Swagger interactive docs available at `/docs`.

2. **Modular Ingestion (`sources/`)**:
   - `FileSource`: Handles local/uploaded multipart file data with MIME type validation and size checking.
   - `URLSource`: Fetches remote images or documents via asynchronous HTTP clients with timeout controls.

3. **Core Processing Engine (`services/`)**:
   - `OCRService`: Encapsulates OCR pipelines, text block localization, confidence metrics, and performance tracking.

4. **Custom Exception Handling (`core/exceptions.py`)**:
   - Custom exceptions: `AppException`, `SourceError`, `SourceNotFoundError`, `InvalidSourceFormatError`, `OCRError`, `OCRProcessingError`.
   - Global exception handlers return unified JSON error responses with status codes, error codes, and details.

5. **Custom Logging (`core/logger.py`)**:
   - Custom colored log formatter for terminal output.
   - Per-module loggers via `get_logger(name)`.

---

## Getting Started

### Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run Server
```bash
uvicorn app:app --reload --port 8000
```
