"""Services package containing core business logic and OCR pipelines."""

from services.base import BaseOCRService, OCRResult
from services.ocr_service import OCRService

__all__ = ["BaseOCRService", "OCRResult", "OCRService"]
