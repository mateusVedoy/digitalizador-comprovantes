import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl

from src.infra.drive_downloader import DriveDownloader
from src.infra.gemini_client import GeminiClient
from src.infra.webhook_sender import WebhookSender
from src.shared.errors import (
    DownloadError,
    ExtractionError,
    GeminiError,
    InvalidUrlError,
    WebhookError,
)
from src.use_case.extract_receipt import ExtractReceiptInput, ExtractReceiptUseCase

app = FastAPI(title="Receipt Extraction API")

# --- Dependency wiring ---
_api_key = os.environ.get("GEMINI_API_KEY", "")
_downloader = DriveDownloader()
_gemini_client = GeminiClient(api_key=_api_key)
_webhook_sender = WebhookSender()
_use_case = ExtractReceiptUseCase(
    downloader=_downloader,
    gemini_gateway=_gemini_client,
    webhook_sender=_webhook_sender,
)


# --- Request model ---
class ReceiptRequest(BaseModel):
    url: str
    webhook_url: HttpUrl


# --- Exception handlers ---
@app.exception_handler(InvalidUrlError)
async def invalid_url_handler(_: Request, exc: InvalidUrlError):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(DownloadError)
async def download_error_handler(_: Request, exc: DownloadError):
    return JSONResponse(status_code=400, content={"error": str(exc)})


@app.exception_handler(ExtractionError)
async def extraction_error_handler(_: Request, exc: ExtractionError):
    return JSONResponse(status_code=422, content={"error": str(exc)})


@app.exception_handler(GeminiError)
async def gemini_error_handler(_: Request, exc: GeminiError):
    return JSONResponse(status_code=502, content={"error": str(exc)})


@app.exception_handler(WebhookError)
async def webhook_error_handler(_: Request, exc: WebhookError):
    return JSONResponse(status_code=502, content={"error": str(exc)})


# --- Endpoint ---
@app.post("/api/receipt")
async def extract_receipt(request: ReceiptRequest):
    if not _api_key:
        return JSONResponse(
            status_code=401,
            content={"error": "GEMINI_API_KEY not configured."},
        )

    input_data = ExtractReceiptInput(
        url=request.url,
        webhook_url=str(request.webhook_url),
    )
    result = await _use_case.execute(input_data)

    return {
        "datetime": result.datetime,
        "amount": result.amount,
        "type": result.type,
        "receipt_url": result.receipt_url,
        "webhook_status": result.webhook_status,
    }


# Esse arquivo possui código gerado com IA
