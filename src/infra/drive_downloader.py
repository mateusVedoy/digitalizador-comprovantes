import re

import httpx

from src.shared.errors import DownloadError, InvalidUrlError

_DRIVE_FILE_ID_REGEX = re.compile(r"/file/d/([a-zA-Z0-9_-]+)")
_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}


class DriveDownloader:
    """Extracts FILE_ID from Google Drive URL and downloads image bytes."""

    async def download(self, drive_url: str) -> tuple[bytes, str]:
        file_id = self._extract_file_id(drive_url)
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        print(f"[drive_downloader] Iniciando download — file_id={file_id}")

        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            try:
                response = await client.get(download_url)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                print(f"[drive_downloader] ERRO no download: {exc}")
                raise DownloadError(
                    f"Failed to download image from Drive: {exc}"
                ) from exc

        content_type = response.headers.get("content-type", "").split(";")[0].strip()
        if content_type not in _ALLOWED_MIME_TYPES:
            print(f"[drive_downloader] ERRO: tipo não suportado — {content_type}")
            raise DownloadError(
                f"Unsupported format: {content_type}. Only JPEG and PNG are accepted."
            )

        print(f"[drive_downloader] Download concluído — {len(response.content)} bytes, tipo: {content_type}")
        return response.content, content_type

    @staticmethod
    def _extract_file_id(url: str) -> str:
        match = _DRIVE_FILE_ID_REGEX.search(url)
        if not match:
            raise InvalidUrlError(
                "Invalid URL. Please provide a Google Drive sharing link."
            )
        return match.group(1)


# Esse arquivo possui código gerado com IA
