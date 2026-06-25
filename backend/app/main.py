"""Main FastAPI application."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger
from app.db.database import init_db
from app.api.v1 import transaction, ranking, summary
from app.middleware.error_handler import (
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Transaction Ranking System - Production Grade Backend",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


# Include routers
app.include_router(transaction.router, prefix="/api/v1")
app.include_router(ranking.router, prefix="/api/v1")
app.include_router(summary.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting up application")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
)
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get(
    "/api/health",
    tags=["Health"],
    summary="API health check",
)
async def api_health_check() -> dict:
    """API health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
