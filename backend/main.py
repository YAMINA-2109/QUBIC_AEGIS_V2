"""
QUBIC AEGIS - Main Entry Point
AI Multi-Agent Security System for Qubic Blockchain
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="QUBIC AEGIS API",
    description="AI Multi-Agent Security System for Qubic Blockchain",
    version="1.0.0"
)

# Configure CORS to allow frontend connections (BLINDÉ pour hackathon)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise tout pour le hackathon
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, tags=["QUBIC AEGIS"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to QUBIC AEGIS API",
        "status": "operational",
        "endpoints": {
            "websocket": "/ws/monitor",
            "automation": "/api/trigger-automation",
            "health": "/api/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

