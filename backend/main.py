"""
QUBIC AEGIS - Main Entry Point (Expert Edition)
AI Multi-Agent Security System for Qubic Blockchain
"""
import os
import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes
from app.services.test_data_generator import initialize_test_data

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle Manager:
    1. Startup: Initializes test data so the dashboard is not empty on launch.
    2. Shutdown: Clean up resources if needed.
    """
    # STARTUP LOGIC
    print("\n🚀 QUBIC AEGIS SYSTEM STARTUP INITIATED")
    print("---------------------------------------")
    
    # Pre-generate realistic data so the demo looks active immediately
    print("📥 Pre-loading simulation data...")
    try:
        # Generate 500 historical transactions to populate graphs
        await initialize_test_data(num_transactions=500, force_regenerate=False)
        print("✅ Data Layer Ready: Historical context loaded.")
    except Exception as e:
        print(f"⚠️ Warning: Could not pre-load data: {e}")
    
    print("🤖 AI Agents: ONLINE")
    print("🛡️ Security Protocols: ACTIVE")
    print("---------------------------------------\n")
    
    yield
    
    # SHUTDOWN LOGIC
    print("\n🛑 System Shutdown...")

# Create FastAPI application with lifespan
app = FastAPI(
    title="QUBIC AEGIS API",
    description="Enterprise AI Security Layer for Qubic Network",
    version="2.1.0",
    lifespan=lifespan
)

# Configure CORS (Permissive for Hackathon Demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(routes.router, tags=["QUBIC AEGIS"])

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {
        "system": "QUBIC AEGIS",
        "status": "operational",
        "mode": "EXPERT_SIMULATION",
        "version": "2.1.0",
        "ai_engine": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
