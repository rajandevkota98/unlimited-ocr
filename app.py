import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl

from core.config import settings
from core.exceptions import (
    AppException,
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from core.logger import get_logger, setup_custom_logging
from services.ocr_service import OCRService
from sources.file_source import FileSource
from sources.url_source import URLSource

# Initialize custom logging
setup_custom_logging(settings.log_level)
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context for startup and shutdown procedures."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version} [{settings.app_env}]")
    # Initialize service instances
    app.state.ocr_service = OCRService()
    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing and correlation logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info(f"--> {request.method} {request.url.path}")

    try:
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(f"<-- {request.method} {request.url.path} {response.status_code} ({duration_ms:.2f}ms)")
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        return response
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        logger.error(f"<-- FAIL {request.method} {request.url.path} ({duration_ms:.2f}ms) - {exc}")
        raise


# Register custom exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Request and response models
class URLOCRRequest(BaseModel):
    url: HttpUrl
    language: Optional[str] = "en"


@app.get("/", tags=["Status"])
async def root():
    """Root status endpoint returning service information."""
    return {
        "status": "online",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
    }


@app.get("/health", tags=["Status"])
async def health():
    """Health check endpoint for liveness and readiness probes."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
    }


@app.post("/api/v1/ocr/upload", tags=["OCR"])
async def process_file_ocr(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en"),
):
    """Processes an uploaded document or image file using FileSource and OCRService."""
    source = FileSource(file=file)
    payload = await source.extract()

    ocr_service: OCRService = app.state.ocr_service
    result = await ocr_service.process(payload=payload, language=language)

    return {
        "status": "success",
        "data": {
            "text": result.text,
            "blocks": [
                {
                    "text": b.text,
                    "confidence": b.confidence,
                    "bbox": b.bbox,
                }
                for b in result.blocks
            ],
            "language": result.language,
            "page_count": result.page_count,
            "processing_time_ms": result.processing_time_ms,
            "metadata": result.metadata,
        },
    }


@app.post("/api/v1/ocr/url", tags=["OCR"])
async def process_url_ocr(request: URLOCRRequest):
    """Processes a remote document or image URL using URLSource and OCRService."""
    source = URLSource(url=str(request.url))
    payload = await source.extract()

    ocr_service: OCRService = app.state.ocr_service
    result = await ocr_service.process(payload=payload, language=request.language)

    return {
        "status": "success",
        "data": {
            "text": result.text,
            "blocks": [
                {
                    "text": b.text,
                    "confidence": b.confidence,
                    "bbox": b.bbox,
                }
                for b in result.blocks
            ],
            "language": result.language,
            "page_count": result.page_count,
            "processing_time_ms": result.processing_time_ms,
            "metadata": result.metadata,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
