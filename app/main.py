"""Main FastAPI application module."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import pets
from app.core.config import settings
from app.core.database import close_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    print("Starting up Pet Directory API...")
    # Initialize database if needed
    # await init_db()  # Uncomment if you want to create tables on startup

    yield

    # Shutdown
    print("Shutting down Pet Directory API...")
    await close_db()


app: FastAPI = FastAPI(
    title=settings.APP_NAME,
    description="A RESTful API service for managing pets in a directory with background reporting",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(pets.router)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    summary="Root endpoint",
    tags=["default"],
)
async def root() -> dict[str, str]:
    """
    Root endpoint with API information.

    Returns:
        Dictionary with welcome message and documentation URLs
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    summary="Health check",
    tags=["monitoring"],
)
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for monitoring.

    Returns:
        Dictionary with health status and application info
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
    }


@app.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    response_class=JSONResponse,
    summary="Readiness check",
    tags=["monitoring"],
)
async def readiness_check() -> dict[str, bool]:
    """
    Readiness check endpoint for Kubernetes.

    Returns:
        Dictionary indicating if the service is ready
    """
    # In a real application, you might check database connectivity here
    return {"ready": True}
