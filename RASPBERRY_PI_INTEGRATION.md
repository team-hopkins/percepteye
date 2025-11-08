# Raspberry Pi Client Integration Guide

## Overview

The Raspberry Pi will send camera frames and audio to the **Semantic Router API**, which will automatically route to the appropriate backend API (Face Recognition + TTS or Sign Language Detection).

---

## 🚀 Main Endpoint for Raspberry Pi

### **Primary Endpoint: `/route`**

This is the endpoint your Raspberry Pi should call. It analyzes the frame and automatically calls the appropriate backend API.

```
POST http://YOUR_SEMANTIC_ROUTER_IP:8001/route
Content-Type: application/json
```

---

## 📦 Request Payload Options

The `/route` endpoint accepts **three different payload formats**:

### **Option 1: Image + Audio Description (Recommended)**

```json
{
  "image_base64": "BASE64_ENCODED_IMAGE_STRING",
  "audio_description": "Optional text describing audio context"
}
```

### **Option 2: Image Only**

```json
{
  "image_base64": "BASE64_ENCODED_IMAGE_STRING"
}
```

### **Option 3: Audio Description Only**

```json
{
  "audio_description": "Text describing what's happening or what was spoken"
}
```

---

## 📋 Complete API Reference

### Endpoint: `POST /route`

**Request Headers:**

```
Content-Type: application/json
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_base64` | string | No* | Base64-encoded image from camera (JPEG or PNG) |
| `audio_description` | string | No* | Text description of audio context or transcription |
| `image_url` | string | No | Alternative: URL to image instead of base64 |

\*At least one field (image_base64 or audio_description) should be provided

**Response Format:**

```json
{
  "routing_decision": {
    "route": "face_recognition_tts" | "sign_language" | "none",
    "confidence": 0.95,
    "reasoning": "Explanation of why this route was chosen",
    "error": false
  },
  "api_response": {
    // Response from the backend API (Face Recognition or Sign Language)
    // Format depends on which API was called
  },
  "status": "success" | "skipped" | "error"
}
```

---

## 💻 Python Code Examples for Raspberry Pi

### **Example 1: Basic Image Capture and Send**

```python
import requests
import base64
from picamera2 import Picamera2
import io

# Initialize camera
camera = Picamera2()
camera.start()

# Semantic Router URL (update with your deployed URL)
ROUTER_URL = "http://YOUR_ROUTER_IP:8001/route"

def capture_and_route():
    # Capture image
    image_data = camera.capture_array()

    # Convert to JPEG and encode to base64
    from PIL import Image
    img = Image.fromarray(image_data)
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Send to router
    payload = {
        "image_base64": image_base64
    }

    response = requests.post(ROUTER_URL, json=payload, timeout=60)
    result = response.json()

    # Process result
    route = result['routing_decision']['route']
    confidence = result['routing_decision']['confidence']
    api_response = result['api_response']

    print(f"Route: {route} (confidence: {confidence})")
    print(f"API Response: {api_response}")

    return result

# Call the function
result = capture_and_route()
```

### **Example 2: Image + Audio Context**

```python
import requests
import base64
from picamera2 import Picamera2
import io

ROUTER_URL = "http://YOUR_ROUTER_IP:8001/route"
camera = Picamera2()
camera.start()

def capture_with_audio_context(audio_text):
    # Capture image
    image_data = camera.capture_array()

    # Convert to base64
    from PIL import Image
    img = Image.fromarray(image_data)
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Send to router with audio context
    payload = {
        "image_base64": image_base64,
        "audio_description": audio_text
    }

    response = requests.post(ROUTER_URL, json=payload, timeout=60)
    return response.json()

# Example usage
result = capture_with_audio_context("I see someone making hand gestures")
print(result)
```

### **Example 3: Continuous Monitoring Loop**

```python
import requests
import base64
import time
from picamera2 import Picamera2
from PIL import Image
import io

ROUTER_URL = "http://YOUR_ROUTER_IP:8001/route"
camera = Picamera2()
camera.start()

def process_frame():
    # Capture frame
    image_data = camera.capture_array()

    # Convert to base64
    img = Image.fromarray(image_data)
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    # Send to router
    try:
        response = requests.post(
            ROUTER_URL,
            json={"image_base64": image_base64},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            route = result['routing_decision']['route']

            # Handle different routes
            if route == 'face_recognition_tts':
                handle_face_recognition(result['api_response'])
            elif route == 'sign_language':
                handle_sign_language(result['api_response'])

            return result
        else:
            print(f"Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def handle_face_recognition(api_response):
    """Handle face recognition response"""
    faces = api_response.get('faces', [])
    announcement = api_response.get('announcement', '')

    print(f"Faces detected: {', '.join(faces)}")
    print(f"Announcement: {announcement}")

    # Play TTS audio if available
    tts_audio = api_response.get('eleven_tts_base64')
    if tts_audio:
        # Decode and play audio (implement audio playback)
        pass

def handle_sign_language(api_response):
    """Handle sign language response"""
    predicted_sign = api_response.get('predicted_sign')
    confidence = api_response.get('confidence', 0)

    print(f"Sign detected: {predicted_sign} (confidence: {confidence:.1%})")

    # Speak the detected sign (implement TTS)
    pass

# Main loop
while True:
    result = process_frame()
    time.sleep(1)  # Process 1 frame per second
```

### **Example 4: File-based Testing (Without Camera)**

```python
import requests
import base64

ROUTER_URL = "http://YOUR_ROUTER_IP:8001/route"

def test_with_file(image_path):
    # Load and encode image
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # Send to router
    payload = {"image_base64": image_base64}

    response = requests.post(ROUTER_URL, json=payload, timeout=60)
    result = response.json()

    print(f"Route: {result['routing_decision']['route']}")
    print(f"Confidence: {result['routing_decision']['confidence']}")
    print(f"Status: {result['status']}")

    return result

# Test with a sample image
result = test_with_file("test_image.jpg")
```

---

## 📊 Response Examples

### **Face Recognition Response**

```json
{
  "routing_decision": {
    "route": "face_recognition_tts",
    "confidence": 0.95,
    "reasoning": "Clear faces detected in frame",
    "error": false
  },
  "api_response": {
    "faces": ["Alice", "Unknown"],
    "locations": ["left", "right"],
    "unknown_count": 1,
    "announcement": "I see Alice on the left and one unknown person on the right.",
    "speech_text": "I see Alice on the left and one unknown person on the right.",
    "annotated_image_base64": "iVBORw0KGgoAAAANS...",
    "eleven_tts_base64": "SUQzBAAAAA...",
    "transcribed": null,
    "eleven_tts_error": null
  },
  "status": "success"
}
```

### **Sign Language Response**

```json
{
  "routing_decision": {
    "route": "sign_language",
    "confidence": 0.9,
    "reasoning": "Hand gestures detected, sign language is primary focus",
    "error": false
  },
  "api_response": {
    "success": true,
    "predicted_sign": "B",
    "confidence": 0.998,
    "hand_detected": true,
    "all_predictions": [
      { "sign": "B", "confidence": 0.998 },
      { "sign": "W", "confidence": 0.001 },
      { "sign": "E", "confidence": 0.001 }
    ],
    "message": "Prediction successful"
  },
  "status": "success"
}
```

### **Low Confidence / Skipped Response**

```json
{
  "routing_decision": {
    "route": "none",
    "confidence": 0.45,
    "reasoning": "Frame is unclear, no clear action detected",
    "error": false
  },
  "api_response": null,
  "status": "skipped"
}
```

---

## 🛠️ Alternative Endpoints

### **Option A: Get Routing Decision Only (No API Call)**

If you want to check what route would be chosen WITHOUT calling the backend API:

```
POST http://YOUR_ROUTER_IP:8001/analyze
```

**Use case**: Preview routing decision before making actual API call

**Response**: Only returns routing decision, no api_response

### **Option B: Upload Files Directly**

For uploading image/audio as files (not base64):

```
POST http://YOUR_ROUTER_IP:8001/route/upload
Content-Type: multipart/form-data
```

**Form fields:**

- `image`: Image file (optional)
- `audio`: Audio file (optional)
- `audio_description`: Text (optional)

---

## ⚙️ Configuration

### Required Environment Variables on Raspberry Pi

```bash
# Semantic Router URL (update after deployment)
ROUTER_URL=http://YOUR_ROUTER_IP:8001

# Optional: Timeout settings
REQUEST_TIMEOUT=60  # seconds
```

### Network Requirements

- Raspberry Pi must have internet access
- Firewall must allow outbound connections to port 8001
- Recommended: Use static IP or domain name for router

---

## 🎯 Best Practices

### 1. **Image Quality**

- Recommended resolution: 640x480 to 1920x1080
- Format: JPEG (for smaller size) or PNG (for quality)
- Quality: 75-85% for JPEG

### 2. **Error Handling**

```python
try:
    response = requests.post(ROUTER_URL, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
except requests.exceptions.Timeout:
    print("Request timed out - try again")
except requests.exceptions.ConnectionError:
    print("Cannot connect to router - check network")
except Exception as e:
    print(f"Error: {e}")
```

### 3. **Performance Optimization**

- Reduce image quality for faster transmission
- Add frame skipping (don't process every frame)
- Use async requests for non-blocking operation
- Cache routing decisions for similar frames

### 4. **Battery Optimization**

```python
# Process 1 frame per second instead of continuous
import time

while True:
    process_frame()
    time.sleep(1)  # 1 FPS
```

---

## 🔍 Testing the Integration

### Quick Test from Raspberry Pi

```bash
# Test 1: Health check
curl http://YOUR_ROUTER_IP:8001/health

# Test 2: Send test image
python3 << EOF
import requests
import base64

with open('test_image.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

response = requests.post(
    'http://YOUR_ROUTER_IP:8001/route',
    json={'image_base64': img_b64}
)
print(response.json())
EOF
```

---

## 📞 Support

If you encounter issues:

1. **Check router status**: `curl http://YOUR_ROUTER_IP:8001/health`
2. **View router logs**: `docker-compose logs -f semantic-router`
3. **Test with sample image**: Use the file-based testing example above
4. **Verify network**: Ensure Raspberry Pi can reach the router IP

---

## 🔗 Quick Reference

| Endpoint        | Method | Purpose                    | Timeout |
| --------------- | ------ | -------------------------- | ------- |
| `/health`       | GET    | Check if router is running | 10s     |
| `/analyze`      | POST   | Get routing decision only  | 30s     |
| `/route`        | POST   | Route and call API         | 60s     |
| `/route/upload` | POST   | Upload files directly      | 60s     |

**Recommended timeout**: 60 seconds (Face Recognition + TTS can be slow)

---

**Ready to integrate! Your teammate can use the examples above to start sending frames from the Raspberry Pi.** 🚀
