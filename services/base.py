from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from sources.base import SourcePayload


@dataclass
class TextBlock:
    """Represents an extracted text block with bounding box information."""

    text: str
    confidence: float
    bbox: Optional[List[int]] = None  # [x, y, w, h]


@dataclass
class OCRResult:
    """Standardized OCR processing output structure."""

    text: str
    blocks: List[TextBlock] = field(default_factory=list)
    language: str = "en"
    page_count: int = 1
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseOCRService(ABC):
    """Abstract interface for OCR service implementations."""

    @abstractmethod
    async def process(self, payload: SourcePayload, language: Optional[str] = None) -> OCRResult:
        """Processes payload and returns structured OCR result."""
        pass
