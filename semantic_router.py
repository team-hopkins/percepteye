"""
Semantic Router for PerceptEye
Routes audio and video frames to appropriate API endpoints based on content analysis
Uses Google Gemini API for intelligent routing decisions
"""

import os
import base64
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
import requests
from dataclasses import dataclass
import json
import google.generativeai as genai
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RouteType(Enum):
    """Available API endpoints"""
    FACE_RECOGNITION_TTS = "face_recognition_tts"  # Combined Face Recognition + TTS (replaces speech and people_recognition)
    SIGN_LANGUAGE = "sign_language"
    NONE = "none"


@dataclass
class RouterConfig:
    """Configuration for the semantic router"""
    gemini_api_key: str
    face_recognition_tts_api_url: str  # Combined Face Recognition + TTS API
    sign_language_api_url: str
    gemini_model: str = "gemini-2.0-flash-exp"
    confidence_threshold: float = 0.7


class SemanticRouter:
    """
    Semantic Router that analyzes video and audio frames to determine
    which API endpoint to call among speech, people recognition, and sign language
    """
    
    def __init__(self, config: RouterConfig):
        self.config = config
        
        # Configure Gemini
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(config.gemini_model)
        
        # System prompt for the routing decision
        self.system_prompt = """You are an intelligent routing system for an assistive technology platform called PerceptEye.

Your role is to analyze video frames and audio input to determine which API service should be called:

1. **FACE_RECOGNITION_TTS** - Combined Face Recognition and Text-to-Speech/Speech-to-Text
   - Use when: Faces are visible OR audio/speech is present OR verbal communication is needed
   - Indicators: Human faces, people in frame, audio input, speech patterns, mouth movements
   - This API handles BOTH face recognition AND speech processing (via ElevenLabs TTS/STT)
   - Use this for: person identification, face detection, audio transcription, text-to-speech

2. **SIGN_LANGUAGE** - Sign language gesture detection
   - Use when: Hand gestures or sign language movements are prominently visible
   - Indicators: Hands in prominent position, gesturing, sign language patterns, hand shapes
   - Only use this when sign language is the PRIMARY focus of the frame

3. **NONE** - No clear action needed
   - Use when: Frame is unclear, no relevant activity detected, or empty frame

Priority Rules:
- If faces AND sign language are both visible, prefer FACE_RECOGNITION_TTS unless sign language is the dominant feature
- If audio/speech is present with any visual content, prefer FACE_RECOGNITION_TTS
- Only route to SIGN_LANGUAGE when hands/gestures are the primary focus

Analyze the provided frame(s) and audio description, then respond with ONLY a JSON object in this exact format:
{
  "route": "face_recognition_tts" | "sign_language" | "none",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}

Be decisive and prioritize based on the most prominent features in the frame."""

    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode image file to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def encode_image_bytes_to_base64(self, image_bytes: bytes) -> str:
        """Encode image bytes to base64 string"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _decode_base64_to_image(self, image_base64: str) -> Image.Image:
        """Decode base64 string to PIL Image"""
        image_bytes = base64.b64decode(image_base64)
        return Image.open(io.BytesIO(image_bytes))

    def analyze_frame(
        self,
        image_base64: Optional[str] = None,
        audio_description: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Analyze a video frame and optional audio to determine routing decision
        
        Args:
            image_base64: Base64 encoded image string
            audio_description: Description or transcription of audio input
            image_url: URL to image (alternative to base64)
            
        Returns:
            Dictionary containing routing decision
        """
        try:
            # Prepare the prompt
            prompt_parts = [self.system_prompt]
            
            # Add text context
            text_content = "\n\nAnalyze this frame"
            if audio_description:
                text_content += f" with audio input: {audio_description}"
            text_content += ". Determine the appropriate routing decision."
            
            prompt_parts.append(text_content)
            
            # Add image if available
            if image_base64:
                image = self._decode_base64_to_image(image_base64)
                prompt_parts.append(image)
            elif image_url:
                # Download image from URL
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                prompt_parts.append(image)
            
            logger.info(f"Sending request to Gemini API with model: {self.config.gemini_model}")
            
            # Generate content with Gemini
            response = self.model.generate_content(
                prompt_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=500,
                )
            )
            
            # Extract the routing decision
            content = response.text
            logger.info(f"Received response: {content}")
            
            # Parse the JSON response
            routing_decision = self._parse_routing_response(content)
            
            return routing_decision
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            return {
                "route": RouteType.NONE.value,
                "confidence": 0.0,
                "reasoning": f"Error: {str(e)}",
                "error": True
            }
    
    def _parse_routing_response(self, content: str) -> Dict:
        """Parse the routing response from Gemini"""
        try:
            # Try to find JSON in the response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                routing_data = json.loads(json_str)
                
                # Validate the response
                if "route" in routing_data and "confidence" in routing_data:
                    return {
                        "route": routing_data["route"],
                        "confidence": float(routing_data["confidence"]),
                        "reasoning": routing_data.get("reasoning", ""),
                        "error": False
                    }
            
            # If JSON parsing fails, return default
            return {
                "route": RouteType.NONE.value,
                "confidence": 0.0,
                "reasoning": "Failed to parse routing decision",
                "error": True
            }
            
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return {
                "route": RouteType.NONE.value,
                "confidence": 0.0,
                "reasoning": f"Parse error: {str(e)}",
                "error": True
            }
    
    def route_and_call_api(
        self,
        image_base64: Optional[str] = None,
        audio_data: Optional[bytes] = None,
        audio_description: Optional[str] = None,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Analyze frame, determine route, and call the appropriate API
        
        Args:
            image_base64: Base64 encoded image
            audio_data: Raw audio bytes
            audio_description: Text description of audio
            image_url: URL to image
            
        Returns:
            Dictionary containing routing decision and API response
        """
        # Get routing decision
        routing_decision = self.analyze_frame(
            image_base64=image_base64,
            audio_description=audio_description,
            image_url=image_url
        )
        
        # Check confidence threshold
        if routing_decision.get("error") or routing_decision["confidence"] < self.config.confidence_threshold:
            logger.warning(f"Low confidence or error in routing: {routing_decision}")
            return {
                "routing_decision": routing_decision,
                "api_response": None,
                "status": "skipped"
            }
        
        # Call the appropriate API
        route_type = routing_decision["route"]
        api_response = None
        
        try:
            if route_type == RouteType.FACE_RECOGNITION_TTS.value:
                api_response = self._call_face_recognition_tts_api(image_base64, audio_data, audio_description)
            elif route_type == RouteType.SIGN_LANGUAGE.value:
                api_response = self._call_sign_language_api(image_base64)
            
            return {
                "routing_decision": routing_decision,
                "api_response": api_response,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error calling API: {str(e)}")
            return {
                "routing_decision": routing_decision,
                "api_response": None,
                "status": "error",
                "error": str(e)
            }
    
    def _call_face_recognition_tts_api(
        self, 
        image_base64: Optional[str], 
        audio_data: Optional[bytes] = None, 
        audio_description: Optional[str] = None
    ) -> Dict:
        """
        Call the combined Face Recognition + TTS API
        
        API Endpoint: POST /process
        Content-Type: multipart/form-data
        
        Form fields:
        - image (string, REQUIRED): base64-encoded image
        - audio (file, OPTIONAL): audio file for transcription
        - audio_text (string, OPTIONAL): text to synthesize to speech
        - annotated (boolean, OPTIONAL): return annotated image with bounding boxes
        - announce (boolean, OPTIONAL): prepare announcement from recognized faces
        - speak (boolean, OPTIONAL): synthesize speech from announcement
        
        Response:
        {
            "faces": ["Alice", "Unknown"],
            "locations": ["left", "right"],
            "unknown_count": 1,
            "announcement": "I see Alice on the left...",
            "speech_text": "...",
            "annotated_image_base64": "...",
            "eleven_tts_base64": "...",
            "transcribed": "...",
            "eleven_tts_error": null
        }
        """
        logger.info("Calling Face Recognition + TTS API")
        
        # Prepare multipart form data
        files = {}
        data = {}
        
        # Image is required
        if not image_base64:
            return {"error": "No image provided for face recognition"}
        
        # Add image as base64 string (not file)
        data['image'] = image_base64
        
        # Add audio file if available
        if audio_data:
            files['audio'] = ('audio.wav', audio_data, 'audio/wav')
        
        # Add audio text if available
        if audio_description:
            data['audio_text'] = audio_description
        
        # Request annotated image and speech
        data['annotated'] = 'true'
        data['announce'] = 'true'
        data['speak'] = 'true'
        
        try:
            # Make request to /process endpoint
            response = requests.post(
                self.config.face_recognition_tts_api_url,
                data=data,
                files=files if files else None,
                timeout=60  # Longer timeout for face recognition + TTS
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Log the results
            faces = result.get('faces', [])
            unknown_count = result.get('unknown_count', 0)
            announcement = result.get('announcement', '')
            
            logger.info(f"Faces detected: {', '.join(faces)}")
            logger.info(f"Unknown faces: {unknown_count}")
            if announcement:
                logger.info(f"Announcement: {announcement}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Face Recognition + TTS API: {str(e)}")
            return {
                "error": str(e),
                "faces": [],
                "unknown_count": 0,
                "announcement": None
            }
    
    def _call_speech_api(self, audio_data: Optional[bytes], audio_description: Optional[str]) -> Dict:
        """
        DEPRECATED: Speech API functionality is now part of Face Recognition + TTS API
        This method is kept for backward compatibility
        """
        logger.warning("Speech API is deprecated. Use Face Recognition + TTS API instead.")
        return self._call_face_recognition_tts_api(None, audio_data, audio_description)
    
    def _call_people_recognition_api(self, image_base64: str) -> Dict:
        """
        DEPRECATED: People Recognition functionality is now part of Face Recognition + TTS API
        This method is kept for backward compatibility
        """
        logger.warning("People Recognition API is deprecated. Use Face Recognition + TTS API instead.")
        return self._call_face_recognition_tts_api(image_base64)
    
    def _call_sign_language_api(self, image_base64: str) -> Dict:
        """
        Call the Sign Language API
        Expects POST to /predict/base64 endpoint with image_base64 field
        
        API Response structure:
        {
            "success": bool,
            "predicted_sign": str or null,
            "confidence": float or null,
            "contextual_meaning": str or null,
            "alternative_contexts": array or null,
            "hand_detected": bool,
            "message": str
        }
        """
        logger.info("Calling Sign Language Detection API")
        
        # Sign Language API expects /predict/base64 endpoint
        api_url = self.config.sign_language_api_url
        if not api_url.endswith('/predict/base64'):
            # Ensure we're using the correct endpoint
            api_url = api_url.rstrip('/') + '/predict/base64'
        
        response = requests.post(
            api_url,
            json={"image_base64": image_base64},  # API expects "image_base64" field
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Log the detection result
        if result.get("success") and result.get("hand_detected"):
            sign = result.get('predicted_sign')
            confidence = result.get('confidence', 0)
            contextual = result.get('contextual_meaning')
            
            log_msg = f"Sign detected: {sign} (confidence: {confidence:.2%})"
            if contextual:
                log_msg += f" - Meaning: {contextual}"
            logger.info(log_msg)
        elif result.get("success") and not result.get("hand_detected"):
            logger.info("No hand detected in frame")
        
        return result


def create_router_from_env() -> SemanticRouter:
    """Create a router instance from environment variables"""
    config = RouterConfig(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        face_recognition_tts_api_url=os.getenv("FACE_RECOGNITION_TTS_API_URL", ""),
        sign_language_api_url=os.getenv("SIGN_LANGUAGE_API_URL", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
        confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    )
    
    return SemanticRouter(config)


if __name__ == "__main__":
    # Example usage
    router = create_router_from_env()
    
    # Example: Analyze a frame
    # result = router.analyze_frame(
    #     image_base64="...",
    #     audio_description="Someone is speaking"
    # )
    # print(result)
