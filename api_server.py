"""
FastAPI Server for Semantic Router
Middleware API that receives data from Raspberry Pi and routes to appropriate services
Uses Google Gemini API for intelligent routing
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import base64
import logging
from semantic_router import SemanticRouter, RouterConfig, create_router_from_env

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PerceptEye Semantic Router",
    description="Intelligent routing middleware using Google Gemini API",
    version="1.0.0"
)

# Add CORS middleware for Raspberry Pi communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the semantic router
router = create_router_from_env()


class FrameAnalysisRequest(BaseModel):
    """Request model for frame analysis"""
    image_base64: Optional[str] = None
    audio_description: Optional[str] = None
    image_url: Optional[str] = None


class FrameAnalysisResponse(BaseModel):
    """Response model for frame analysis"""
    route: str
    confidence: float
    reasoning: str
    error: bool = False


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PerceptEye Semantic Router",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "router": "operational"
    }


@app.post("/analyze", response_model=FrameAnalysisResponse)
async def analyze_frame(request: FrameAnalysisRequest):
    """
    Analyze a video frame and optional audio to determine routing decision
    
    Args:
        request: FrameAnalysisRequest containing image and/or audio data
        
    Returns:
        Routing decision with confidence score
    """
    try:
        logger.info("Received frame analysis request")
        
        result = router.analyze_frame(
            image_base64=request.image_base64,
            audio_description=request.audio_description,
            image_url=request.image_url
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/route")
async def route_frame(request: FrameAnalysisRequest):
    """
    Analyze frame, determine route, and call the appropriate API endpoint
    
    Args:
        request: FrameAnalysisRequest containing image and/or audio data
        
    Returns:
        Complete routing decision and API response
    """
    try:
        logger.info("Received routing request")
        
        result = router.route_and_call_api(
            image_base64=request.image_base64,
            audio_description=request.audio_description,
            image_url=request.image_url
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in route endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/route/upload")
async def route_frame_upload(
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    audio_description: Optional[str] = Form(None)
):
    """
    Upload files directly for routing (alternative to base64)
    
    Args:
        image: Image file from camera
        audio: Audio file
        audio_description: Text description of audio
        
    Returns:
        Complete routing decision and API response
    """
    try:
        logger.info("Received file upload routing request")
        
        # Process image
        image_base64 = None
        if image:
            image_bytes = await image.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Process audio
        audio_bytes = None
        if audio:
            audio_bytes = await audio.read()
        
        result = router.route_and_call_api(
            image_base64=image_base64,
            audio_data=audio_bytes,
            audio_description=audio_description
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in upload route endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/route/face-recognition")
async def force_route_face_recognition(request: FrameAnalysisRequest):
    """Force route to face recognition + TTS API (bypass semantic routing)"""
    try:
        result = router._call_face_recognition_tts_api(
            request.image_base64,
            None,
            request.audio_description
        )
        return {"api_response": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/route/speech")
async def force_route_speech(request: FrameAnalysisRequest):
    """DEPRECATED: Use /route/face-recognition instead. Speech is now part of Face Recognition + TTS API"""
    try:
        result = router._call_face_recognition_tts_api(None, None, request.audio_description)
        return {"api_response": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/route/people")
async def force_route_people(request: FrameAnalysisRequest):
    """DEPRECATED: Use /route/face-recognition instead. People recognition is now part of Face Recognition + TTS API"""
    try:
        result = router._call_face_recognition_tts_api(request.image_base64, None, None)
        return {"api_response": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/route/sign-language")
async def force_route_sign_language(request: FrameAnalysisRequest):
    """Force route to sign language API (bypass semantic routing)"""
    try:
        result = router._call_sign_language_api(request.image_base64)
        return {"api_response": result, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
