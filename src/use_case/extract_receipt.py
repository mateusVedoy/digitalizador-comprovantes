from dataclasses import dataclass
from typing import Optional

from src.domain.gemini_gateway import IGeminiGateway
from src.domain.llm_config import LlmConfig
from src.infra.drive_downloader import DriveDownloader
from src.infra.webhook_sender import WebhookSender


@dataclass
class ExtractReceiptInput:
    receipt_url: str
    webhook_url: str
    optional_config: Optional[LlmConfig] = None


@dataclass
class ExtractReceiptOutput:
    datetime: str
    amount: float
    type: str
    receipt_url: str
    webhook_status: str


class ExtractReceiptUseCase:
    """Orchestrates the flow: image download → Gemini → webhook."""

    def __init__(
        self,
        downloader: DriveDownloader,
        gemini_gateway: IGeminiGateway,
        webhook_sender: WebhookSender,
    ):
        self._downloader = downloader
        self._gemini_gateway = gemini_gateway
        self._webhook_sender = webhook_sender

    async def execute(self, input_data: ExtractReceiptInput) -> ExtractReceiptOutput:
        print(f"[extract_receipt] Iniciando processamento da URL: {input_data.receipt_url}")

        try:
            image_bytes, mime_type = await self._downloader.download(input_data.receipt_url)
            print(f"[extract_receipt] Download concluído — {len(image_bytes)} bytes, tipo: {mime_type}")
        except Exception as exc:
            print(f"[extract_receipt] ERRO no download da imagem: {exc}")
            raise

        try:
            receipt = await self._gemini_gateway.analyze_receipt(
                image_bytes, mime_type, input_data.optional_config,
            )
            print(f"[extract_receipt] LLM retornou dados — datetime={receipt.datetime}, amount={receipt.amount}, type={receipt.type}")
        except Exception as exc:
            print(f"[extract_receipt] ERRO na chamada à LLM: {exc}")
            raise

        webhook_payload = {
            "datetime": receipt.datetime,
            "amount": receipt.amount,
            "type": receipt.type,
            "receipt_url": input_data.receipt_url,
        }

        try:
            await self._webhook_sender.send(input_data.webhook_url, webhook_payload)
            print(f"[extract_receipt] Webhook enviado com sucesso para: {input_data.webhook_url}")
        except Exception as exc:
            print(f"[extract_receipt] ERRO ao enviar webhook: {exc}")
            raise

        return ExtractReceiptOutput(
            datetime=receipt.datetime,
            amount=receipt.amount,
            type=receipt.type,
            receipt_url=input_data.receipt_url,
            webhook_status="sent",
        )


# Esse arquivo possui código gerado com IA
