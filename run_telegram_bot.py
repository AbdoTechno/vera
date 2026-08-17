import asyncio
import os
import httpx
from src.config import CONFIG
from src.api.routes import get_service
from src.api.telegram_service import TelegramService
from src.utils.logger import logger

async def run_bot_polling():
    """Runs the Telegram Bot locally using Long Polling (zero tunnels / zero ngrok required)."""
    token = CONFIG.telegram.bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in your .env file.")
        return

    telegram_svc = TelegramService(bot_token=token)
    
    logger.info("Pre-warming VERA RAG services (vector store & retrieval)...")
    rag_svc = get_service()

    # Delete any existing webhook so polling receives updates directly
    logger.info("Clearing any existing webhook to enable Long Polling...")
    await telegram_svc.remove_webhook()

    logger.success("=================================================================")
    logger.success(" VERA Telegram Bot is LIVE in Local Polling Mode! ")
    logger.success(" Open Telegram and chat with: @veramedicalbot")
    logger.success(" Press CTRL+C to stop the bot.")
    logger.success("=================================================================")

    offset = 0

    async with httpx.AsyncClient(timeout=35.0) as client:
        while True:
            try:
                url = f"{telegram_svc.base_url}/getUpdates?offset={offset}&timeout=25"
                resp = await client.get(url)
                
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("result", [])
                    for update in results:
                        offset = update["update_id"] + 1
                        # Process update asynchronously in background
                        asyncio.create_task(telegram_svc.process_update(update, rag_svc))
                elif resp.status_code == 409:
                    # Webhook conflict: delete webhook and retry
                    logger.warning("Webhook conflict detected; clearing webhook...")
                    await telegram_svc.remove_webhook()
                    await asyncio.sleep(2)
                else:
                    logger.warning(f"Telegram getUpdates returned status {resp.status_code}")
                    await asyncio.sleep(1)

            except httpx.ReadTimeout:
                # Normal timeout for long polling
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Polling loop error: {e}")
                await asyncio.sleep(2)

if __name__ == "__main__":
    try:
        asyncio.run(run_bot_polling())
    except KeyboardInterrupt:
        logger.info("Telegram Bot stopped by user.")
