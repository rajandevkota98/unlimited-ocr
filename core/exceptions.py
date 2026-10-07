from typing import Any, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.logger import get_logger

logger = get_logger("exceptions")


class AppException(Exception):
    """Base custom application exception with structured error representation."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "APP_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class SourceError(AppException):
    """Base exception for source ingestion/extraction failures."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "SOURCE_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=details,
        )


class SourceNotFoundError(SourceError):
    """Raised when the specified source file or remote resource does not exist."""

    def __init__(self, message: str = "Source not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="SOURCE_NOT_FOUND",
            details=details,
        )


class InvalidSourceFormatError(SourceError):
    """Raised when source format or content type is unsupported."""

    def __init__(self, message: str = "Unsupported source format", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=415,
            error_code="INVALID_SOURCE_FORMAT",
            details=details,
        )


class OCRError(AppException):
    """Base exception for OCR engine processing failures."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "OCR_ERROR",
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=details,
        )


class OCRProcessingError(OCRError):
    """Raised when OCR processing encounters an unrecoverable engine failure."""

    def __init__(self, message: str = "Failed to process OCR request", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="OCR_PROCESSING_FAILED",
            details=details,
        )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handles custom AppException and formats unified JSON response."""
    logger.error(
        f"Custom exception caught on {request.method} {request.url.path}: "
        f"[{exc.error_code}] {exc.message} (details={exc.details})"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handles FastAPI/Pydantic request validation errors."""
    errors = exc.errors()
    logger.warning(
        f"Validation failed on {request.method} {request.url.path}: {len(errors)} error(s)"
    )
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "error_code": "VALIDATION_ERROR",
            "message": "Input validation failed",
            "details": errors,
            "path": str(request.url.path),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handles unhandled system exceptions with 500 internal server error."""
    logger.critical(
        f"Unhandled exception on {request.method} {request.url.path}: {type(exc).__name__}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred",
            "details": {"exception_type": type(exc).__name__},
            "path": str(request.url.path),
        },
    )
