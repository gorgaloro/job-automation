#!/usr/bin/env python3
"""
Railway Production Main - Clean FastAPI app for Railway deployment
No secrets, minimal dependencies, ready to deploy
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="AI Job Search Platform API",
    description="Production-ready AI-powered job search automation platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🚀 AI Job Search Platform API",
        "status": "active",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-job-search-platform",
        "timestamp": "2025-01-25T13:40:00Z"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "status": "/api/v1/status"
        },
        "environment": os.getenv("RAILWAY_ENVIRONMENT", "production")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
