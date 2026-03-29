# ai_service/app/main.py
# FastAPI application entry point.
# Registers all API routes and configures CORS.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import handwriting, correction, tts, stt

# Create the FastAPI application instance
app = FastAPI(title="Digital Scribe AI Service", version="1.0.0")

# CORS: Allow requests from React frontend
# In production, replace "*" with your Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers with URL prefixes
app.include_router(handwriting.router, prefix="/api")
app.include_router(correction.router, prefix="/api")
app.include_router(tts.router, prefix="/api")
app.include_router(stt.router, prefix="/api")

@app.get("/health")
def health_check():
    # Simple endpoint to verify the service is running
    return {"status": "ok"}
