from abc import ABC, abstractmethod

from src.domain.receipt_data import ReceiptData


class IGeminiGateway(ABC):
    """Abstract interface defining the Gemini contract."""

    @abstractmethod
    async def analyze_receipt(self, image_bytes: bytes, mime_type: str) -> ReceiptData:
        """Send image to Gemini and return extracted data via function calling."""


# Esse arquivo possui código gerado com IA
