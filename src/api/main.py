import os
import asyncio
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.config import CONFIG
from src.api.routes import router as api_router, get_service
from src.api.telegram_router import router as telegram_router
from src.api.telegram_service import TelegramService
from src.utils.logger import logger

DEFAULT_TELEGRAM_BOT_TOKEN = "8932080168:AAE8ki9YyH4QXQmOPfsI9HSfmc7rLSP9wnM"

async def _start_telegram_bot_background(rag_svc):
    token = os.getenv("TELEGRAM_BOT_TOKEN") or CONFIG.telegram.bot_token or DEFAULT_TELEGRAM_BOT_TOKEN

    telegram_svc = TelegramService(bot_token=token)
    
    # If a public HTTPS URL is detected (e.g. on Render), auto-register webhook
    webhook_base = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("TELEGRAM_WEBHOOK_URL") or CONFIG.telegram.webhook_url
    if webhook_base and webhook_base.startswith("https://"):
        full_webhook_url = f"{webhook_base.rstrip('/')}/telegram/webhook"
        logger.info(f"Auto-registering Telegram Webhook: {full_webhook_url}")
        res = await telegram_svc.set_webhook(full_webhook_url)
        logger.info(f"Telegram Webhook Registration: {res.get('description', 'OK')}")
        return None
    else:
        # Run resilient background polling loop inside FastAPI
        logger.info("Starting background Telegram Polling loop inside FastAPI...")
        try:
            await telegram_svc.remove_webhook()
        except Exception:
            pass

        async def polling_worker():
            offset = 0
            async with httpx.AsyncClient(timeout=35.0) as client:
                while True:
                    try:
                        url = f"{telegram_svc.base_url}/getUpdates?offset={offset}&timeout=25"
                        resp = await client.get(url)
                        if resp.status_code == 200:
                            data = resp.json()
                            for update in data.get("result", []):
                                offset = update["update_id"] + 1
                                asyncio.create_task(telegram_svc.process_update(update, rag_svc))
                        elif resp.status_code == 409:
                            await telegram_svc.remove_webhook()
                            await asyncio.sleep(2)
                        else:
                            await asyncio.sleep(2)
                    except httpx.ReadTimeout:
                        continue
                    except asyncio.CancelledError:
                        break
                    except Exception as e:
                        logger.error(f"Telegram polling background error: {e}")
                        await asyncio.sleep(3)

        return asyncio.create_task(polling_worker())

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm RAG pipeline & vector store in background on server boot
    logger.info("Pre-warming VERA RAG services and vector store...")
    rag_svc = get_service()
    logger.success("VERA RAG services pre-warmed and ready for instant queries.")
    
    bot_task = await _start_telegram_bot_background(rag_svc)
    yield
    if bot_task:
        bot_task.cancel()
    logger.info("Shutting down VERA services.")

app = FastAPI(
    title="VERA - Clinical Intelligence Platform API",
    description=(
        "Evidence-grounded clinical decision-support API for physicians and researchers. "
        "Provides dynamic BYOK LLM key injection, transparent RAG simulation, and verified citations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Enable CORS for Flutter mobile, web, and local emulators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount raw_pdfs directory as static files so Flutter app can load/render PDFs directly
pdf_dir = Path("./data/raw_pdfs")
if pdf_dir.exists():
    app.mount("/pdfs", StaticFiles(directory=str(pdf_dir)), name="pdfs")

# Include API routers
app.include_router(api_router)
app.include_router(telegram_router)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": "VERA Clinical Intelligence Platform API",
        "status": "online",
        "documentation": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
