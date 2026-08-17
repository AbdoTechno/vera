import os
from typing import Optional, Dict, Any
from fastapi import APIRouter, Request, Header, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from src.config import CONFIG
from src.api.routes import get_service
from src.api.service import VERAClinicalService
from src.api.telegram_service import TelegramService
from src.utils.logger import logger

router = APIRouter(prefix="/telegram", tags=["Telegram Bot Integration"])

# Global Telegram Service singleton
_telegram_service: Optional[TelegramService] = None

def get_telegram_service() -> TelegramService:
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service

class SetWebhookRequest(BaseModel):
    webhook_url: Optional[str] = Field(default=None, description="Custom HTTPS webhook URL. If omitted, uses TELEGRAM_WEBHOOK_URL from config.")
    secret_token: Optional[str] = Field(default=None, description="Optional secret token for request verification.")

@router.post("/webhook", summary="Telegram Webhook Receiver")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_telegram_bot_api_secret_token: Optional[str] = Header(default=None, alias="X-Telegram-Bot-Api-Secret-Token"),
    telegram_svc: TelegramService = Depends(get_telegram_service),
    rag_svc: VERAClinicalService = Depends(get_service)
):
    """
    Receives incoming Telegram updates from the Telegram Bot webhook.
    Validates secret token (if configured) and executes VERA RAG query processing in background.
    """
    # 1. Validate Secret Token if configured
    configured_secret = CONFIG.telegram.webhook_secret or os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if configured_secret and x_telegram_bot_api_secret_token != configured_secret:
        logger.warning("Telegram webhook received unauthorized request (invalid secret token).")
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret token.")

    # 2. Parse incoming update JSON
    try:
        update_data = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON payload in Telegram webhook: {e}")
        return {"ok": False, "error": "invalid_json"}

    # 3. Process update directly or dispatch
    # Using background task for RAG execution ensures Telegram receives 200 OK within its 5-second timeout window
    background_tasks.add_task(telegram_svc.process_update, update_data, rag_svc)

    return {"ok": True, "status": "processing"}

@router.post("/set-webhook", summary="Register Telegram Webhook")
async def set_webhook(
    payload: Optional[SetWebhookRequest] = None,
    telegram_svc: TelegramService = Depends(get_telegram_service)
):
    """
    Registers the webhook URL with the Telegram Bot API.
    URL resolution order:
    1. payload.webhook_url
    2. TELEGRAM_WEBHOOK_URL environment variable / config.yaml
    """
    target_url = (payload.webhook_url if payload and payload.webhook_url else None) or CONFIG.telegram.webhook_url or os.getenv("TELEGRAM_WEBHOOK_URL", "")
    target_secret = (payload.secret_token if payload and payload.secret_token else None) or CONFIG.telegram.webhook_secret or os.getenv("TELEGRAM_WEBHOOK_SECRET", "")

    if not target_url:
        raise HTTPException(
            status_code=400,
            detail="Webhook URL not provided. Set TELEGRAM_WEBHOOK_URL in .env or pass webhook_url in request body."
        )

    if not target_url.startswith("https://"):
        raise HTTPException(
            status_code=400,
            detail="Telegram requires an HTTPS webhook URL."
        )

    res = await telegram_svc.set_webhook(target_url, secret_token=target_secret or None)
    return res

@router.post("/remove-webhook", summary="Delete Telegram Webhook")
async def remove_webhook(
    telegram_svc: TelegramService = Depends(get_telegram_service)
):
    """Deletes the registered Telegram webhook."""
    res = await telegram_svc.remove_webhook()
    return res

@router.get("/webhook-info", summary="Get Telegram Webhook Status")
async def get_webhook_info(
    telegram_svc: TelegramService = Depends(get_telegram_service)
):
    """Retrieves current Telegram webhook status and diagnostic info."""
    res = await telegram_svc.get_webhook_info()
    return res
