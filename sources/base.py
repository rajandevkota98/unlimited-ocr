from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class SourcePayload:
    """Standardized representation of raw document or image bytes from an input source."""

    data: bytes
    filename: str
    content_type: str
    metadata: Dict[str, Any]


class BaseSource(ABC):
    """Abstract base class defining interface for data/document sources."""

    @abstractmethod
    async def extract(self) -> SourcePayload:
        """Extract and return the standardized source payload."""
        pass

    @abstractmethod
    def validate(self) -> None:
        """Validate source constraints such as size or format."""
        pass
