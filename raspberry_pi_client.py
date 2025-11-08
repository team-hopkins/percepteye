"""
Raspberry Pi Client for PerceptEye
Captures video and audio from camera and sends to semantic router
"""

import cv2
import base64
import requests
import time
import logging
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerceptEyeClient:
    """Client for Raspberry Pi to communicate with semantic router"""
    
    def __init__(self, router_url: str):
        self.router_url = router_url
        self.camera = None
        
    def initialize_camera(self, camera_index: int = 0):
        """Initialize the camera"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                raise Exception("Failed to open camera")
            logger.info("Camera initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing camera: {str(e)}")
            return False
    
    def capture_frame(self) -> Optional[bytes]:
        """Capture a single frame from camera"""
        if not self.camera:
            logger.error("Camera not initialized")
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            logger.error("Failed to capture frame")
            return None
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    
    def send_frame_for_analysis(self, frame_bytes: bytes, audio_description: Optional[str] = None):
        """Send frame to semantic router for analysis"""
        try:
            # Convert to base64
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            
            # Prepare request
            payload = {
                "image_base64": frame_base64
            }
            
            if audio_description:
                payload["audio_description"] = audio_description
            
            # Send to router
            response = requests.post(
                f"{self.router_url}/analyze",
                json=payload,
                timeout=10
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Routing decision: {result['route']} (confidence: {result['confidence']})")
            return result
            
        except Exception as e:
            logger.error(f"Error sending frame: {str(e)}")
            return None
    
    def send_frame_for_routing(self, frame_bytes: bytes, audio_description: Optional[str] = None):
        """Send frame to semantic router for analysis and API call"""
        try:
            # Convert to base64
            frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
            
            # Prepare request
            payload = {
                "image_base64": frame_base64
            }
            
            if audio_description:
                payload["audio_description"] = audio_description
            
            # Send to router
            response = requests.post(
                f"{self.router_url}/route",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Routing result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error routing frame: {str(e)}")
            return None
    
    def run_continuous_capture(self, interval: float = 1.0, analysis_only: bool = False):
        """
        Continuously capture frames and send to router
        
        Args:
            interval: Time between captures in seconds
            analysis_only: If True, only analyze without calling APIs
        """
        logger.info("Starting continuous frame capture")
        
        if not self.initialize_camera():
            return
        
        try:
            while True:
                # Capture frame
                frame_bytes = self.capture_frame()
                if not frame_bytes:
                    time.sleep(interval)
                    continue
                
                # Send for processing
                if analysis_only:
                    result = self.send_frame_for_analysis(frame_bytes)
                else:
                    result = self.send_frame_for_routing(frame_bytes)
                
                if result:
                    logger.info(f"Result: {result}")
                
                # Wait before next capture
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Stopping capture")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.camera:
            self.camera.release()
            logger.info("Camera released")


def main():
    """Main function for Raspberry Pi client"""
    router_url = os.getenv("ROUTER_URL", "http://localhost:8000")
    
    client = PerceptEyeClient(router_url)
    
    # Run continuous capture
    # Set analysis_only=True to just get routing decisions
    # Set analysis_only=False to also call the target APIs
    client.run_continuous_capture(interval=2.0, analysis_only=False)


if __name__ == "__main__":
    main()
