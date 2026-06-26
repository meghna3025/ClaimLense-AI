"""
ClaimSense AI — FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings

# ──────────────────────────────────────────────────────────────
#  Logging
# ──────────────────────────────────────────────────────────────

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(name)-30s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
#  Lifespan
# ──────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ClaimSense AI starting up…")
    if not settings.openai_api_key:
        logger.warning(
            "OPENAI_API_KEY is not set. "
            "Set it in .env or as an environment variable before processing claims."
        )
    yield
    logger.info("ClaimSense AI shutting down.")


# ──────────────────────────────────────────────────────────────
#  App
# ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="ClaimSense AI",
    description=(
        "AI-powered automobile insurance claim processing system. "
        "Powered by Google Gemini and LangGraph."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:4173",   # Vite preview
        "http://127.0.0.1:5173",
        "http://localhost:3000",   # CRA / other
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "service": "ClaimSense AI",
        "version": "1.0.0",
        "docs": "/docs",
    }
