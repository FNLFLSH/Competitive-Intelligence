#!/usr/bin/env python3
"""
Main FastAPI application entry point
Imports and runs the integrated review scraper API
"""

import uvicorn
from integrated_review_scraper import app

if __name__ == "__main__":
    print("🚀 Starting Competitive Intelligence Backend API")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        "integrated_review_scraper:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 