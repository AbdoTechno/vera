from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from src.api.routes import router as api_router, get_service
from src.api.telegram_router import router as telegram_router
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm RAG pipeline & vector store in background on server boot
    logger.info("Pre-warming VERA RAG services and vector store...")
    get_service()
    logger.success("VERA RAG services pre-warmed and ready for instant queries.")
    yield
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
