import os
from urllib.parse import urlparse
import httpx

from core.config import settings
from core.exceptions import InvalidSourceFormatError, SourceError, SourceNotFoundError
from core.logger import get_logger
from sources.base import BaseSource, SourcePayload

logger = get_logger("sources.url")


class URLSource(BaseSource):
    """Source adapter for retrieving remote files via HTTP/HTTPS."""

    def __init__(self, url: str):
        self.url = str(url).strip()
        self.validate()

    def validate(self) -> None:
        """Validates URI scheme."""
        parsed = urlparse(self.url)
        if parsed.scheme not in ("http", "https"):
            raise SourceError(
                f"Invalid URL scheme '{parsed.scheme}'. Only http and https are supported.",
                status_code=400,
                error_code="INVALID_URL_SCHEME",
            )
        if not parsed.netloc:
            raise SourceError("Invalid URL: missing host", status_code=400)

    async def extract(self) -> SourcePayload:
        """Downloads document or image bytes from remote URL."""
        logger.info(f"Fetching remote source from URL: {self.url}")
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                response = await client.get(self.url)
        except httpx.RequestError as exc:
            logger.error(f"Network error requesting URL {self.url}: {exc}")
            raise SourceError(
                f"Failed to fetch resource from URL: {str(exc)}",
                status_code=502,
                error_code="URL_FETCH_FAILED",
            )

        if response.status_code == 404:
            raise SourceNotFoundError(f"Remote resource not found at {self.url}")
        elif response.status_code != 200:
            raise SourceError(
                f"Remote server returned HTTP {response.status_code}",
                status_code=502,
                error_code="UPSTREAM_HTTP_ERROR",
            )

        raw_content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
        content = response.content

        size_mb = len(content) / (1024 * 1024)
        if size_mb > settings.max_upload_size_mb:
            raise SourceError(
                f"Remote file size ({size_mb:.2f}MB) exceeds limit ({settings.max_upload_size_mb}MB)",
                status_code=413,
                error_code="FILE_TOO_LARGE",
            )

        # Extract filename from path or default
        parsed = urlparse(self.url)
        filename = os.path.basename(parsed.path) or "downloaded_document"

        return SourcePayload(
            data=content,
            filename=filename,
            content_type=raw_content_type or "application/octet-stream",
            metadata={
                "source_type": "remote_url",
                "url": self.url,
                "size_bytes": len(content),
            },
        )
