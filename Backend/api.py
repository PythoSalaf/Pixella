#!/usr/bin/env python3
"""
Pixella - AI-Powered Image Authenticity Protocol
FastAPI Server
"""

import os
import json
import logging
import tempfile
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pixella.core.client import PixellaClient
from pixella.core.models import PixellaResult

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pixella API",
    description="AI-Powered Image Authenticity Protocol with Filecoin Storage",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class VerificationRequest(BaseModel):
    image_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class VerificationResponse(BaseModel):
    image_hash: str
    is_tampered: bool
    tamper_score: float
    confidence: float
    anomalies: list
    blockchain_tx: Optional[str] = None
    filecoin_cid: Optional[str] = None
    filecoin_deal_id: Optional[str] = None
    verification_url: str
    timestamp: str

# Global client instance
pixella_client = PixellaClient()

# Helper functions
def result_to_response(result: PixellaResult) -> Dict[str, Any]:
    """Convert PixellaResult to API response format"""
    return {
        "image_hash": result.image_hash,
        "is_tampered": result.tamper_result.is_tampered,
        "tamper_score": result.tamper_result.tamper_score,
        "confidence": result.tamper_result.confidence,
        "anomalies": result.tamper_result.anomalies,
        "blockchain_tx": result.blockchain_tx,
        "filecoin_cid": result.filecoin_cid,
        "filecoin_deal_id": result.filecoin_deal_id,
        "verification_url": result.verification_url,
        "timestamp": result.timestamp,
        "metadata": {
            "filename": result.metadata.filename,
            "size": result.metadata.size,
            "dimensions": result.metadata.dimensions,
            "format": result.metadata.format
        }
    }

# API routes
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Pixella API",
        "version": "1.0.0",
        "description": "AI-Powered Image Authenticity Protocol with Filecoin Storage"
    }

@app.post("/verify", response_model=VerificationResponse)
async def verify_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None)
):
    """Verify image authenticity"""
    temp_path = None
    try:
        # Parse metadata if provided
        try:
            user_metadata = json.loads(metadata) if metadata else {}
        except json.JSONDecodeError:
            logger.error("Invalid metadata JSON format")
            raise HTTPException(status_code=400, detail={
                "error": "invalid_metadata",
                "message": "Invalid metadata JSON format"
            })
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail={
                "error": "missing_filename",
                "message": "Uploaded file must have a filename"
            })
        
        # Save uploaded file to temp location with proper extension
        file_ext = Path(file.filename).suffix.lower()
        if not file_ext:
            file_ext = ".jpg"  # Default extension if none provided
            
        temp_path = tempfile.mktemp(suffix=file_ext)
        
        # Read file content and write to temp file
        try:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail={
                    "error": "empty_file",
                    "message": "Empty file uploaded"
                })
                
            with open(temp_path, "wb") as temp_file:
                temp_file.write(content)
        except Exception as e:
            logger.error(f"File read/write error: {e}")
            raise HTTPException(status_code=400, detail={
                "error": "file_io_error",
                "message": f"Error reading or writing file: {str(e)}"
            })
        
        # Process image
        logger.info(f"Processing uploaded image: {file.filename} (saved to {temp_path})")
        try:
            # Note: Currently the client doesn't support metadata as a parameter
            result = await pixella_client.process_image(temp_path)
            # Return result
            return result_to_response(result)
        except ValueError as e:
            # Handle validation errors (format, size, etc.)
            logger.error(f"Validation error: {e}")
            raise HTTPException(status_code=400, detail={
                "error": "validation_error",
                "message": str(e)
            })
        except FileNotFoundError as e:
            # Should not happen but handle just in case
            logger.error(f"File not found: {e}")
            raise HTTPException(status_code=404, detail={
                "error": "file_not_found",
                "message": str(e)
            })
        except Exception as e:
            # Handle other processing errors
            logger.error(f"Processing error: {e}")
            raise HTTPException(status_code=500, detail={
                "error": "processing_error",
                "message": f"Error processing image: {str(e)}"
            })
    finally:
        # Clean up temp file in background if it exists
        if temp_path and os.path.exists(temp_path):
            background_tasks.add_task(os.unlink, temp_path)

@app.get("/status")
async def get_status():
    """Get API status"""
    # Check if Filecoin storage is configured
    filecoin_provider = os.getenv("FILECOIN_PROVIDER", "mock")
    filecoin_configured = filecoin_provider != "mock" or os.getenv("FILECOIN_API_KEY") is not None
    
    # Check if blockchain is configured
    blockchain_configured = all([
        os.getenv("POLYGON_RPC_URL"),
        os.getenv("PRIVATE_KEY"),
        os.getenv("CONTRACT_ADDRESS")
    ])
    
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "ai_model": True,  # Assuming AI model is always available
            "blockchain": blockchain_configured,
            "filecoin": filecoin_configured
        },
        "filecoin_provider": filecoin_provider
    }

@app.get("/verify/{image_hash}")
async def get_verification(image_hash: str):
    """Get verification result by image hash"""
    # This would typically query a database for stored results
    # For now, return a placeholder
    return JSONResponse(
        status_code=404,
        content={"detail": f"Verification result for hash {image_hash} not found"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
