from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import pets

app = FastAPI(
    title="Pet Directory API",
    description="A simple API for managing pets in a directory",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pets.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Pet Directory API",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}