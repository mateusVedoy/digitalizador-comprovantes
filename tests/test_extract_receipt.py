import pytest

from src.domain.gemini_gateway import IGeminiGateway
from src.domain.receipt_data import ReceiptData
from src.infra.drive_downloader import DriveDownloader
from src.infra.webhook_sender import WebhookSender
from src.shared.errors import ExtractionError, WebhookError
from src.use_case.extract_receipt import ExtractReceiptInput, ExtractReceiptUseCase


class FakeDownloader(DriveDownloader):
    async def download(self, drive_url: str) -> tuple[bytes, str]:
        return b"fake-image-bytes", "image/png"


class FakeGeminiGateway(IGeminiGateway):
    async def analyze_receipt(self, image_bytes: bytes, mime_type: str) -> ReceiptData:
        return ReceiptData(
            datetime="2026-03-15T14:30:00", amount=187.50, type="expense"
        )


class FakeGeminiGatewayFailing(IGeminiGateway):
    async def analyze_receipt(self, image_bytes: bytes, mime_type: str) -> ReceiptData:
        raise ExtractionError("Could not extract data from the receipt.")


class FakeWebhookSender(WebhookSender):
    def __init__(self):
        self.last_payload = None

    async def send(self, webhook_url: str, payload: dict) -> None:
        self.last_payload = payload


class FakeWebhookSenderFailing(WebhookSender):
    async def send(self, webhook_url: str, payload: dict) -> None:
        raise WebhookError("Failed to send data to webhook")


@pytest.mark.asyncio
class TestExtractReceiptUseCase:
    async def test_full_flow_success(self):
        webhook_sender = FakeWebhookSender()
        use_case = ExtractReceiptUseCase(
            downloader=FakeDownloader(),
            gemini_gateway=FakeGeminiGateway(),
            webhook_sender=webhook_sender,
        )

        input_data = ExtractReceiptInput(
            url="https://drive.google.com/file/d/abc123/view?usp=sharing",
            webhook_url="https://webhook.site/test",
        )
        result = await use_case.execute(input_data)

        assert result.datetime == "2026-03-15T14:30:00"
        assert result.amount == 187.50
        assert result.type == "expense"
        assert result.receipt_url == input_data.url
        assert result.webhook_status == "sent"
        assert webhook_sender.last_payload["receipt_url"] == input_data.url

    async def test_extraction_error_propagates(self):
        use_case = ExtractReceiptUseCase(
            downloader=FakeDownloader(),
            gemini_gateway=FakeGeminiGatewayFailing(),
            webhook_sender=FakeWebhookSender(),
        )

        with pytest.raises(ExtractionError):
            await use_case.execute(
                ExtractReceiptInput(
                    url="https://drive.google.com/file/d/abc123/view",
                    webhook_url="https://webhook.site/test",
                )
            )

    async def test_webhook_error_propagates(self):
        use_case = ExtractReceiptUseCase(
            downloader=FakeDownloader(),
            gemini_gateway=FakeGeminiGateway(),
            webhook_sender=FakeWebhookSenderFailing(),
        )

        with pytest.raises(WebhookError):
            await use_case.execute(
                ExtractReceiptInput(
                    url="https://drive.google.com/file/d/abc123/view",
                    webhook_url="https://webhook.site/test",
                )
            )


# Esse arquivo possui código gerado com IA
