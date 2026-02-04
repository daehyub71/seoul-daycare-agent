"""
FastAPI Main Application
Seoul Daycare Search & Recommendation AI Service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import settings

# Create FastAPI app
app = FastAPI(
    title="Seoul Daycare Search AI",
    description="AI-powered daycare search and recommendation service for Seoul",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "service": "Seoul Daycare Search AI",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API routes
from api.routes import router as api_router

app.include_router(api_router, prefix="/api/v1", tags=["api"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
