"""
CineDNA V3 — FastAPI entry point.
Run: uv run uvicorn main:app --reload --port 8000
"""
import sys
import os

# Ensure backend/ is on the path
sys.path.insert(0, os.path.dirname(__file__))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from db.database import init_db
from api.routes import chat, dna, recommendations, profile, movie
from mcp_server.server import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[CineDNA] Initialising database...")
    init_db()
    print("[CineDNA] DB ready.")
    yield
    # Shutdown
    print("[CineDNA] Shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade Agentic AI Movie Companion",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(chat.router)
app.include_router(dna.router)
app.include_router(recommendations.router)
app.include_router(profile.router)
app.include_router(movie.router)

# MCP SSE endpoint (for external MCP clients like Claude Desktop)
app.mount("/mcp", mcp.sse_app())


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "mcp": "/mcp/sse",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
