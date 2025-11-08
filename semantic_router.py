"""
Semantic Router for PerceptEye
Routes audio and video frames to appropriate API endpoints based on content analysis
Uses OpenRouter with Gemini for intelligent routing decisions
"""

import os
import base64
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum
import requests
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RouteType(Enum):
    """Available API endpoints"""
    SPEECH = "speech"
    PEOPLE_RECOGNITION = "people_recognition"
    SIGN_LANGUAGE = "sign_language"
    NONE = "none"


@dataclass
class RouterConfig:
    """Configuration for the semantic router"""
    openrouter_api_key: str
    speech_api_url: str
    people_recognition_api_url: str
    sign_language_api_url: str
    gemini_model: str = "google/gemini-2.0-flash-exp:free"
    confidence_threshold: float = 0.7


class SemanticRouter:
    """
    Semantic Router that analyzes video and audio frames to determine
    which API endpoint to call among speech, people recognition, and sign language
    """
    
    def __init__(self, config: RouterConfig):
        self.config = config
        self.openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # System prompt for the routing decision
        self.system_prompt = """You are an intelligent routing system for an assistive technology platform called PerceptEye.

Your role is to analyze video frames and audio input to determine which API service should be called:

1. **SPEECH** - Text-to-Speech and Speech-to-Text using Eleven Labs
   - Use when: Audio input is present, someone is speaking, or verbal communication is detected
   - Indicators: Audio waveforms, mouth movements, speech patterns

2. **PEOPLE_RECOGNITION** - Person identification and recognition
   - Use when: Clear faces are visible in the frame, need to identify people
   - Indicators: Human faces, people in the frame, need for person identification

3. **SIGN_LANGUAGE** - Sign language gesture detection
   - Use when: Hand gestures, sign language movements are visible
   - Indicators: Hands in prominent position, gesturing, sign language patterns

4. **NONE** - No clear action needed
   - Use when: Frame is unclear, no relevant activity detected

Analyze the provided frame(s) and audio description, then respond with ONLY a JSON object in this exact format:
{
  "route": "speech" | "people_recognition" | "sign_language" | "none",
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
            # Prepare the user message
            user_content = []
            
            # Add text context
            text_content = "Analyze this frame"
            if audio_description:
                text_content += f" with audio input: {audio_description}"
            text_content += ". Determine the appropriate routing decision."
            
            user_content.append({
                "type": "text",
                "text": text_content
            })
            
            # Add image content
            if image_base64:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                })
            elif image_url:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                })
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.config.openrouter_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.gemini_model,
                "messages": [
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            logger.info(f"Sending request to OpenRouter with model: {self.config.gemini_model}")
            
            # Make the API call
            response = requests.post(
                self.openrouter_base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract the routing decision
            content = result['choices'][0]['message']['content']
            logger.info(f"Received response: {content}")
            
            # Parse the JSON response
            # Try to extract JSON from the response
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
            if route_type == RouteType.SPEECH.value:
                api_response = self._call_speech_api(audio_data, audio_description)
            elif route_type == RouteType.PEOPLE_RECOGNITION.value:
                api_response = self._call_people_recognition_api(image_base64)
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
    
    def _call_speech_api(self, audio_data: Optional[bytes], audio_description: Optional[str]) -> Dict:
        """Call the Speech API"""
        logger.info("Calling Speech API")
        
        # Prepare the request based on what's available
        if audio_data:
            files = {'audio': audio_data}
            response = requests.post(self.config.speech_api_url, files=files, timeout=30)
        elif audio_description:
            response = requests.post(
                self.config.speech_api_url,
                json={"text": audio_description},
                timeout=30
            )
        else:
            return {"error": "No audio data or description provided"}
        
        response.raise_for_status()
        return response.json()
    
    def _call_people_recognition_api(self, image_base64: str) -> Dict:
        """Call the People Recognition API"""
        logger.info("Calling People Recognition API")
        
        response = requests.post(
            self.config.people_recognition_api_url,
            json={"image": image_base64},
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    def _call_sign_language_api(self, image_base64: str) -> Dict:
        """Call the Sign Language API"""
        logger.info("Calling Sign Language API")
        
        response = requests.post(
            self.config.sign_language_api_url,
            json={"image": image_base64},
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()


def create_router_from_env() -> SemanticRouter:
    """Create a router instance from environment variables"""
    config = RouterConfig(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        speech_api_url=os.getenv("SPEECH_API_URL", ""),
        people_recognition_api_url=os.getenv("PEOPLE_RECOGNITION_API_URL", ""),
        sign_language_api_url=os.getenv("SIGN_LANGUAGE_API_URL", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "google/gemini-2.0-flash-exp:free"),
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
