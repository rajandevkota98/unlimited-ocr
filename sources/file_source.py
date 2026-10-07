from typing import Optional
from fastapi import UploadFile

from core.config import settings
from core.exceptions import InvalidSourceFormatError, SourceError
from core.logger import get_logger
from sources.base import BaseSource, SourcePayload

logger = get_logger("sources.file")


class FileSource(BaseSource):
    """Source adapter for uploaded multipart files."""

    def __init__(self, file: UploadFile):
        self.file = file
        self.validate()

    def validate(self) -> None:
        """Validates file presence and content type against allowed MIME types."""
        if not self.file.filename:
            raise SourceError("File must have a valid filename", status_code=400)

        content_type = self.file.content_type or "application/octet-stream"
        if content_type not in settings.allowed_mime_types:
            logger.warning(f"Rejected unsupported file format: {content_type} ({self.file.filename})")
            raise InvalidSourceFormatError(
                f"Content type '{content_type}' is not supported. Allowed: {settings.allowed_mime_types}",
                details={"filename": self.file.filename, "content_type": content_type},
            )

    async def extract(self) -> SourcePayload:
        """Reads binary file contents and checks size limits."""
        logger.info(f"Extracting file source: {self.file.filename} ({self.file.content_type})")
        content = await self.file.read()

        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.max_upload_size_mb:
            raise SourceError(
                f"File size ({size_mb:.2f}MB) exceeds maximum permitted limit ({settings.max_upload_size_mb}MB)",
                status_code=413,
                error_code="FILE_TOO_LARGE",
            )

        return SourcePayload(
            data=content,
            filename=self.file.filename,
            content_type=self.file.content_type or "application/octet-stream",
            metadata={
                "source_type": "file_upload",
                "size_bytes": len(content),
            },
        )
