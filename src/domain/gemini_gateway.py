from abc import ABC, abstractmethod
from typing import Optional

from src.domain.llm_config import LlmConfig
from src.domain.receipt_data import ReceiptData


class IGeminiGateway(ABC):
    """Abstract interface defining the Gemini contract."""

    @abstractmethod
    async def analyze_receipt(
        self,
        image_bytes: bytes,
        mime_type: str,
        optional_config: Optional[LlmConfig] = None,
    ) -> ReceiptData:
        """Send image to Gemini and return extracted data via function calling."""


# Esse arquivo possui código gerado com IA
