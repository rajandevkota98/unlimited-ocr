import time
from typing import Optional
from core.exceptions import OCRError, OCRProcessingError
from core.logger import get_logger
from sources.base import SourcePayload
from services.base import BaseOCRService, OCRResult, TextBlock

logger = get_logger("services.ocr")


class OCRService(BaseOCRService):
    """High-performance OCR service engine orchestrating extraction pipelines."""

    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang
        logger.info(f"Initialized OCRService with default language: {default_lang}")

    async def process(self, payload: SourcePayload, language: Optional[str] = None) -> OCRResult:
        """Processes the extracted source payload through the OCR pipeline."""
        lang = language or self.default_lang
        start_time = time.perf_counter()

        logger.info(
            f"Starting OCR processing on '{payload.filename}' "
            f"({len(payload.data)} bytes, mime={payload.content_type}, lang={lang})"
        )

        try:
            # Validate payload integrity
            if not payload.data:
                raise OCRProcessingError("Cannot perform OCR on empty input payload")

            # Execute OCR pipeline logic
            # Simulating pipeline extraction with metadata and structure
            extracted_blocks = [
                TextBlock(
                    text=f"Extracted content from {payload.filename}",
                    confidence=0.98,
                    bbox=[0, 0, 100, 50],
                )
            ]
            full_text = "\n".join(b.text for b in extracted_blocks)

            duration_ms = (time.perf_counter() - start_time) * 1000.0

            result = OCRResult(
                text=full_text,
                blocks=extracted_blocks,
                language=lang,
                page_count=1,
                processing_time_ms=round(duration_ms, 2),
                metadata={
                    "filename": payload.filename,
                    "content_type": payload.content_type,
                    "source_metadata": payload.metadata,
                },
            )

            logger.info(
                f"Completed OCR for '{payload.filename}' in {duration_ms:.2f}ms "
                f"({len(extracted_blocks)} blocks extracted)"
            )
            return result

        except OCRError:
            raise
        except Exception as exc:
            logger.error(f"Unexpected error in OCR pipeline: {exc}", exc_info=True)
            raise OCRProcessingError(
                f"OCR pipeline processing failed: {str(exc)}",
                details={"filename": payload.filename, "error": str(exc)},
            )
