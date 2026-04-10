class InvalidUrlError(Exception):
    """URL is missing, has invalid format, or is not a Google Drive link."""


class DownloadError(Exception):
    """Failed to download image from Drive."""


class ExtractionError(Exception):
    """Gemini could not extract data from the receipt."""


class GeminiError(Exception):
    """Error communicating with Gemini."""


class WebhookError(Exception):
    """Failed to send data to the webhook."""


# Esse arquivo possui código gerado com IA
