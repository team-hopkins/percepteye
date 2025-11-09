# PerceptEye - Semantic Router

YCP2025@hacks

An intelligent routing middleware API that uses Google Gemini to analyze video and audio frames and route requests to the appropriate feature API.

## System Architecture

```
Raspberry Pi (Camera)
    ↓ (sends frames)
Semantic Router API (Middleware)
    ↓ (analyzes with Google Gemini API)
    ├→ Face Recognition + TTS API (Digital Ocean) - Handles faces, speech, and audio
    └→ Sign Language API (Digital Ocean) - Handles sign language gestures
```

## Features

### Two Feature APIs (deployed on Digital Ocean):

1. **Face Recognition + TTS API** - Combined face detection, person identification, and Text-to-Speech/Speech-to-Text using Eleven Labs

   - Face detection and recognition
   - Audio transcription (Speech-to-Text)
   - Text synthesis (Text-to-Speech)
   - Annotated images with bounding boxes
   - Announcement generation

2. **Sign Language Detection API** - Gesture recognition from image frames
   - Hand gesture detection
   - Sign language classification
   - Confidence scoring

### Semantic Router:

- Receives audio and video frames from Raspberry Pi
- Uses Google Gemini API to analyze content
- Intelligently routes to the appropriate feature API
- Acts as middleware between Raspberry Pi and feature APIs

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 2: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start server
python api_server.py
```

Server runs on: `http://localhost:8001` (Docker) or `http://localhost:8000` (local Python)

## API Endpoints

### Health Check

```
GET /health
```

### Analyze Frame (Get Routing Decision)

```
POST /analyze
Content-Type: application/json

{
  "image_base64": "base64_encoded_image",
  "audio_description": "optional audio context",
  "image_url": "optional image URL"
}
```

**Response:**

```json
{
  "route": "face_recognition_tts|sign_language|none",
  "confidence": 0.85,
  "reasoning": "Detected hand gestures indicating sign language",
  "error": false
}
```

### Route and Execute (Analyze + Call Target API)

```
POST /route
Content-Type: application/json

{
  "image_base64": "base64_encoded_image",
  "audio_description": "optional audio context"
}
```

**Response:**

```json
{
  "routing_decision": {
    "route": "sign_language",
    "confidence": 0.92,
    "reasoning": "Clear hand gestures detected"
  },
  "api_response": {
    // Response from the target Digital Ocean API
  },
  "status": "success"
}
```

### Upload Files

```
POST /route/upload
Content-Type: multipart/form-data

image: file (optional)
audio: file (optional)
audio_description: string (optional)
```

### Force Route to Specific API (for testing)

```
POST /route/speech
POST /route/people
POST /route/sign-language
```

## Configuration

Edit `.env` file:

```env
# Google Gemini API Key (Get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_key_here

# Gemini Model
GEMINI_MODEL=gemini-2.0-flash-exp

# Your Digital Ocean API Endpoints
# Face Recognition + TTS API (combines face detection, recognition, and speech)
FACE_RECOGNITION_TTS_API_URL=http://143.198.4.179/process
# Sign Language Detection API
SIGN_LANGUAGE_API_URL=http://138.197.12.52

# Routing Configuration
CONFIDENCE_THRESHOLD=0.7
```

### Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API key" or "Create API key"
4. Copy the key to your `.env` file

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python test.py

# Run specific tests
python test.py --test health
python test.py --test sign_language
python test.py --test face_recognition
python test.py --test scenarios

# Test with custom router URL
python test.py --router-url http://localhost:8000
```

The test suite includes:

- ✅ Health check
- ✅ Sign Language Detection API
- ✅ Face Recognition + TTS API
- ✅ Multiple routing scenarios
- ✅ Direct API endpoint tests

## For Your Teammate (Raspberry Pi Integration)

The Raspberry Pi should send POST requests to:

- `http://your-server:8001/analyze` - To get routing decision only
- `http://your-server:8001/route` - To get decision + API result
- `http://your-server:8001/route/upload` - To upload files directly

Example request from Raspberry Pi:

```python
import requests
import base64

# Capture frame (your teammate's code)
with open("frame.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode('utf-8')

# Send to router
response = requests.post(
    "http://your-server:8000/route",
    json={
        "image_base64": img_base64,
        "audio_description": "optional audio context"
    }
)

result = response.json()
print(result)
```

## Deployment

### Docker Deployment (Recommended)

**Quick Start:**

```bash
# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Access API at http://localhost:8000
```

**See `DOCKER_DEPLOYMENT.md` for complete Docker documentation.**

### Other Platforms

- Digital Ocean App Platform
- AWS ECS/Lambda
- Google Cloud Run
- Kubernetes

See `README_ROUTER.md` for detailed deployment instructions.

I had a few things on my mind, please don't try to implement the code
Just help me visualize if it is feasible or not
There are two types of API we route there currently:

- Face Recognition + TTS API
- Sign Language Detection API
  I was thinking if there are no faces or hand gestures.
  Then we can leverage gemini-2.5-flash, which will share what nearby object it sees to help the blind people see nearby objects
