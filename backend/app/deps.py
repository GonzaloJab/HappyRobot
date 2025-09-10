"""
Dependencies and configuration for the FastAPI app
"""
import os
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

def get_allowed_origins() -> List[str]:
    """Get allowed CORS origins from environment variable"""
    origins = os.getenv("ALLOWED_ORIGINS", "*")
    if origins == "*":
        return ["*"]
    return [origin.strip() for origin in origins.split(",")]

def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware"""
    origins = get_allowed_origins()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def get_port() -> int:
    """Get port from environment variable, default to 8000"""
    return int(os.getenv("PORT", "8000"))
