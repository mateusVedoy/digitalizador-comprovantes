import httpx

from src.shared.errors import WebhookError


class WebhookSender:
    """Posts extracted data to the webhook via httpx."""

    async def send(self, webhook_url: str, payload: dict) -> None:
        print(f"[webhook_sender] Enviando payload para: {webhook_url}")
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                response = await client.post(webhook_url, json=payload)
                response.raise_for_status()
                print(f"[webhook_sender] Webhook enviado — status {response.status_code}")
            except httpx.HTTPError as exc:
                print(f"[webhook_sender] ERRO ao enviar webhook: {exc}")
                raise WebhookError(
                    f"Failed to send data to webhook: {exc}"
                ) from exc


# Esse arquivo possui código gerado com IA
