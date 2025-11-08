# PerceptEye - Semantic Router

An intelligent routing middleware API that uses OpenRouter with Gemini to analyze video and audio frames and route requests to the appropriate feature API.

## System Architecture

```
Raspberry Pi (Camera)
    ↓ (sends frames)
Semantic Router API (Middleware)
    ↓ (analyzes with Google Gemini API)
    ├→ Speech API (Eleven Labs - Digital Ocean)
    ├→ People Recognition API (Digital Ocean)
    └→ Sign Language API (Digital Ocean)
```

## Features

### Three Feature APIs (deployed on Digital Ocean):

1. **Speech API** - Text-to-Speech and Speech-to-Text using Eleven Labs
2. **People Recognition API** - Face detection and person identification
3. **Sign Language Detection API** - Gesture recognition from image frames

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

Server runs on: `http://localhost:8000`

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
  "route": "speech|people_recognition|sign_language|none",
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
SPEECH_API_URL=https://your-speech-api.digitalocean.com/api/process
PEOPLE_RECOGNITION_API_URL=https://your-people-api.digitalocean.com/api/recognize
# Sign Language API base URL (e.g., http://your-ip:8000)
SIGN_LANGUAGE_API_URL=https://your-sign-language-api.digitalocean.com:8000

# Routing Configuration
CONFIDENCE_THRESHOLD=0.7
```

### Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Get API key" or "Create API key"
4. Copy the key to your `.env` file

## Testing

Run the test suite:

```bash
python test_router.py
```

## For Your Teammate (Raspberry Pi Integration)

The Raspberry Pi should send POST requests to:

- `http://your-server:8000/analyze` - To get routing decision only
- `http://your-server:8000/route` - To get decision + API result
- `http://your-server:8000/route/upload` - To upload files directly

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
