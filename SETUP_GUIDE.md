# PerceptEye - Setup Guide

## Getting Your Gemini API Key

### Step 1: Go to Google AI Studio

Visit: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

### Step 2: Sign In

- Sign in with your Google account
- Accept the terms of service if prompted

### Step 3: Create API Key

- Click **"Get API key"** or **"Create API key"**
- Choose "Create API key in new project" or select an existing project
- Your API key will be generated

### Step 4: Copy API Key

- Copy the generated API key (starts with `AIza...`)
- **Keep it secure and never commit it to version control**

### Step 5: Add to Environment

Add to your `.env` file:

```env
GEMINI_API_KEY=AIzaSy...your_actual_key_here
```

## Setting Up Your Digital Ocean API Endpoints

You need to provide the URLs for your three feature APIs:

```env
# Speech API (Eleven Labs)
SPEECH_API_URL=https://your-speech-api.digitalocean.com/api/process

# People Recognition API
PEOPLE_RECOGNITION_API_URL=https://your-people-api.digitalocean.com/api/recognize

# Sign Language API
SIGN_LANGUAGE_API_URL=https://your-sign-language-api.digitalocean.com/api/detect
```

Replace the URLs with your actual Digital Ocean deployment URLs.

## Complete Setup Steps

### 1. Clone Repository

```bash
git clone https://github.com/team-hopkins/percepteye.git
cd percepteye
```

### 2. Create Environment File

```bash
cp .env.example .env
```

### 3. Edit .env File

```bash
nano .env  # or use your preferred editor
```

Add your actual values:

```env
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-2.0-flash-exp
SPEECH_API_URL=https://your-actual-url.com/api/process
PEOPLE_RECOGNITION_API_URL=https://your-actual-url.com/api/recognize
SIGN_LANGUAGE_API_URL=https://your-actual-url.com/api/detect
CONFIDENCE_THRESHOLD=0.7
```

### 4. Run with Docker (Recommended)

```bash
docker-compose up -d
```

### 5. Or Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python api_server.py
```

### 6. Test the Setup

```bash
# Health check
curl http://localhost:8000/health

# Test analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"audio_description": "Someone is speaking"}'
```

## Available Gemini Models

You can use different Gemini models by changing `GEMINI_MODEL` in `.env`:

- **`gemini-2.0-flash-exp`** (Recommended) - Latest, fastest, free
- **`gemini-1.5-pro`** - Most capable, multimodal
- **`gemini-1.5-flash`** - Fast and efficient
- **`gemini-1.5-flash-8b`** - Lightweight and fast

## Troubleshooting

### "API key not valid" error

- Verify your API key is correct
- Check if API key has proper permissions
- Make sure there are no extra spaces in `.env` file

### "Rate limit exceeded" error

- Gemini free tier has rate limits
- Wait a few minutes and try again
- Consider upgrading to paid tier for higher limits

### Docker issues

```bash
# Rebuild container
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs -f
```

### Local Python issues

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

## API Rate Limits (Free Tier)

Google Gemini Free Tier:

- **15 requests per minute (RPM)**
- **1 million tokens per minute (TPM)**
- **1,500 requests per day (RPD)**

For production use, consider:

- Implementing request caching
- Adding rate limiting in your code
- Upgrading to paid tier if needed

## Next Steps

1. ✅ Get Gemini API key
2. ✅ Configure environment variables
3. ✅ Start the server
4. 📱 Integrate with Raspberry Pi (your teammate's task)
5. 🚀 Deploy to production

## Support

- **Gemini API Issues**: [Google AI Studio Help](https://ai.google.dev/docs)
- **Project Issues**: Create an issue on GitHub
- **Documentation**: See `README.md` and `API_DOCUMENTATION.md`

# PerceptEye - Semantic Router

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
