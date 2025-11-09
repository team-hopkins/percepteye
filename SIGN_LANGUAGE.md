# Sign Language Detection API - Integration Guide for Semantic Router

## 🎯 Overview

This document provides instructions for integrating the Sign Language Detection API with the Gemini-based Semantic Router running on Raspberry Pi.

## 📡 API Endpoint Details

**Base URL (when deployed):** `http://your-digital-ocean-ip:8000`

**For local testing:** `http://localhost:8000`

## 🔌 API Endpoints

### 1. Health Check

```
GET /health
```

Use this to verify the API is running before making predictions.

**Response:**

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### 2. Get Supported Classes

```
GET /classes
```

Returns list of all ASL signs the model can detect.

**Response:**

```json
{
  "classes": [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "del",
    "space"
  ],
  "count": 28
}
```

### 3. Predict from Base64 Image (RECOMMENDED for Raspberry Pi)

```
POST /predict/base64
Content-Type: application/json
```

**Request Body:**

```json
{
  "image_base64": "<base64_encoded_image_string>"
}
```

**Response (Success with hand detected):**

```json
{
  "success": true,
  "predicted_sign": "B",
  "confidence": 0.9958,
  "contextual_meaning": "I need a bathroom",
  "alternative_contexts": ["The letter B", "I need to go back", "Book please"],
  "hand_detected": true,
  "message": "Prediction successful"
}
```

**Response (No hand detected):**

```json
{
  "success": true,
  "predicted_sign": null,
  "confidence": null,
  "contextual_meaning": null,
  "alternative_contexts": null,
  "hand_detected": false,
  "message": "No hand detected in image"
}
```

**Response (Error):**

```json
{
  "detail": "Error message here"
}
```

## 🤖 Integration Code for Semantic Router

### Python Implementation (Recommended)

```python
import cv2
import base64
import requests
import json

class SignLanguageDetector:
    """Sign Language Detection API client for Semantic Router"""

    def __init__(self, api_url="http://your-digital-ocean-ip:8000"):
        self.api_url = api_url
        self.predict_endpoint = f"{api_url}/predict/base64"
        self.health_endpoint = f"{api_url}/health"

    def check_health(self):
        """Check if API is healthy"""
        try:
            response = requests.get(self.health_endpoint, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    def detect_sign(self, frame):
        """
        Detect ASL sign from camera frame

        Args:
            frame: OpenCV image (numpy array) from camera

        Returns:
            dict: Prediction result with sign, confidence, and hand_detected status
        """
        try:
            # Encode frame to JPEG
            _, buffer = cv2.imencode('.jpg', frame)

            # Convert to base64
            image_base64 = base64.b64encode(buffer).decode('utf-8')

            # Send request
            payload = {"image_base64": image_base64}
            response = requests.post(
                self.predict_endpoint,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"API returned status {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Usage in Semantic Router
def main():
    # Initialize detector
    detector = SignLanguageDetector(api_url="http://your-digital-ocean-ip:8000")

    # Check API health before starting
    if not detector.check_health():
        print("Sign Language API is not available!")
        return

    # Open camera
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect sign language
        result = detector.detect_sign(frame)

        if result.get("success") and result.get("hand_detected"):
            sign = result["predicted_sign"]
            confidence = result["confidence"]
            contextual_meaning = result.get("contextual_meaning")

            print(f"Detected: {sign} (Confidence: {confidence:.1%})")

            # NEW: Display contextual meaning if available
            if contextual_meaning:
                print(f"Meaning: {contextual_meaning}")

                # Show alternative contexts
                alt_contexts = result.get("alternative_contexts", [])
                if alt_contexts:
                    print(f"Alternatives: {', '.join(alt_contexts)}")

            # You can now:
            # 1. Add to sentence buffer
            # 2. Trigger text-to-speech with contextual meaning
            # 3. Display on screen
            # 4. Log for analytics

        elif result.get("success") and not result.get("hand_detected"):
            print("No hand detected in frame")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

        # Optional: Show frame with prediction
        if result.get("hand_detected"):
            cv2.putText(
                frame,
                f"{result['predicted_sign']} ({result['confidence']:.0%})",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.imshow('Sign Language Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
```

## 🔄 Semantic Router Decision Logic

Here's how your semantic router should decide when to call the Sign Language API:

```python
def semantic_router_logic(frame, audio, context):
    """
    Main routing logic for SenseAI system

    Args:
        frame: Camera frame from Raspberry Pi
        audio: Audio input (if any)
        context: Current conversation context
    """

    # Use Gemini to analyze the situation
    gemini_analysis = analyze_with_gemini(frame, audio, context)

    # Routing decisions:

    # 1. If hands are visible in frame and making signs -> Sign Language API
    if gemini_analysis["hands_detected"] and gemini_analysis["likely_signing"]:
        result = sign_language_api.detect_sign(frame)
        if result["hand_detected"]:
            return {
                "action": "sign_language",
                "data": result,
                "response": f"I see you're signing: {result['predicted_sign']}"
            }

    # 2. If person speaking -> Speech-to-Text (ElevenLabs)
    elif gemini_analysis["person_speaking"]:
        text = eleven_labs_api.speech_to_text(audio)
        return {
            "action": "speech_to_text",
            "data": {"text": text},
            "response": text
        }

    # 3. If face detected but no signs/speech -> Face Recognition
    elif gemini_analysis["face_detected"]:
        person = face_recognition_api.identify(frame)
        return {
            "action": "face_recognition",
            "data": person,
            "response": f"Hello {person['name']}"
        }

    # 4. Default: wait for input
    else:
        return {
            "action": "waiting",
            "response": "Waiting for input..."
        }
```

## 📊 Response Structure Reference

| Field                  | Type           | Description                                        |
| ---------------------- | -------------- | -------------------------------------------------- |
| `success`              | boolean        | Whether the API call succeeded                     |
| `predicted_sign`       | string or null | The detected ASL sign (A-Z, del, space)            |
| `confidence`           | float or null  | Prediction confidence (0.0 to 1.0)                 |
| `contextual_meaning`   | string or null | AI-generated contextual interpretation of the sign |
| `alternative_contexts` | array or null  | List of alternative contextual meanings            |
| `hand_detected`        | boolean        | Whether a hand was detected in the image           |
| `message`              | string         | Human-readable status message                      |

## ⚠️ Important Considerations

### 1. Confidence Threshold

Only trust predictions with **confidence > 0.7** (70%):

```python
if result["confidence"] > 0.7:
    # High confidence - use the prediction
    process_sign(result["predicted_sign"])
else:
    # Low confidence - ask user to repeat or ignore
    print("Please sign more clearly")
```

### 2. Frame Rate Management

Don't send every frame to the API:

```python
import time

last_prediction_time = 0
PREDICTION_INTERVAL = 0.5  # seconds

current_time = time.time()
if current_time - last_prediction_time >= PREDICTION_INTERVAL:
    result = detector.detect_sign(frame)
    last_prediction_time = current_time
```

### 3. Sentence Building

Buffer consecutive signs to build words/sentences:

```python
from collections import deque
import time

class SignBuffer:
    def __init__(self, commit_threshold=3, timeout=2.0):
        self.buffer = deque(maxlen=10)
        self.commit_threshold = commit_threshold
        self.timeout = timeout
        self.last_sign_time = time.time()
        self.current_sentence = []

    def add_sign(self, sign, confidence):
        """Add a detected sign to the buffer"""
        if confidence < 0.7:
            return None

        self.buffer.append(sign)
        self.last_sign_time = time.time()

        # Check if we have a consensus (majority voting)
        if len(self.buffer) >= self.commit_threshold:
            most_common = max(set(self.buffer), key=list(self.buffer).count)
            count = list(self.buffer).count(most_common)

            if count >= self.commit_threshold:
                self.current_sentence.append(most_common)
                self.buffer.clear()
                return most_common

        return None

    def get_sentence(self):
        """Get the current sentence"""
        return ''.join(self.current_sentence)

    def clear(self):
        """Clear the buffer and sentence"""
        self.buffer.clear()
        self.current_sentence.clear()
```

### 4. Error Handling

Always handle API failures gracefully:

```python
try:
    result = detector.detect_sign(frame)
    if not result.get("success"):
        logger.error(f"API error: {result.get('error')}")
        # Fall back to other detection methods or notify user
except requests.exceptions.Timeout:
    logger.error("API timeout - network issue?")
except requests.exceptions.ConnectionError:
    logger.error("Cannot connect to API - is it running?")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## 🧪 Testing Checklist

Before deploying to production:

- [ ] API health check works
- [ ] Can detect all 28 signs (A-Z, del, space)
- [ ] Confidence scores are reasonable (>70% for clear signs)
- [ ] Handles "no hand detected" gracefully
- [ ] Network timeout handling works
- [ ] Frame rate management doesn't overload API
- [ ] Sentence building logic works correctly
- [ ] Integration with TTS works (speaks detected signs)

## 📞 API Rate Limits

**Current limits:** None (adjust based on your deployment)

**Recommended:** Max 10 requests/second per client

## 🔐 Security (Production)

For production deployment, add API key authentication:

```python
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(
    endpoint,
    json=payload,
    headers=headers,
    timeout=10
)
```

## 📦 Summary for Semantic Router

**To get predicted sign, send:**

1. Capture frame from camera
2. Encode as JPEG then base64
3. POST to `/predict/base64` with `{"image_base64": "<encoded_string>"}`
4. Parse response for `predicted_sign`, `confidence`, and `hand_detected`
5. Use sign if `hand_detected=true` and `confidence > 0.7`

**Key fields to extract:**

- `result["predicted_sign"]` - The detected sign (e.g., "B")
- `result["confidence"]` - How confident (e.g., 0.9958 = 99.58%)
- `result["hand_detected"]` - Whether a hand was found (true/false)

That's it! The API is designed to be simple and efficient for real-time integration. 🚀
