"""
Simple FastAPI Demo App for Deployment Testing
"""
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI(
    title="FastAPI Demo",
    description="Simple API for testing deplight-platform deployment",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hello from Deplight Platform!",
        "timestamp": datetime.now().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "dev"),
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint for ALB"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/status")
async def status():
    """API status endpoint"""
    return {
        "api": "online",
        "features": ["fast-deployment", "ai-powered", "zero-config"],
        "deployment_time": "< 2 minutes"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
