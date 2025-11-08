# PerceptEye Semantic Router - API Documentation

## Overview

The Semantic Router is a middleware API that intelligently routes requests to appropriate feature APIs based on video and audio frame analysis using Gemini via OpenRouter.

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for the router itself. Configure your Digital Ocean API credentials in the `.env` file.

---

## Endpoints

### 1. Health Check

Check if the router is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "router": "operational"
}
```

---

### 2. Analyze Frame

Analyze a frame and get the routing decision without calling the target API.

**Endpoint:** `POST /analyze`

**Request Body:**
```json
{
  "image_base64": "string (optional)",
  "audio_description": "string (optional)",
  "image_url": "string (optional)"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "audio_description": "Someone is speaking"
  }'
```

**Response:**
```json
{
  "route": "speech",
  "confidence": 0.89,
  "reasoning": "Clear audio indicators of speech detected",
  "error": false
}
```

**Possible Routes:**
- `speech` - Route to Speech API (Eleven Labs)
- `people_recognition` - Route to People Recognition API
- `sign_language` - Route to Sign Language API
- `none` - No clear action needed

---

### 3. Route and Execute

Analyze frame, determine route, and call the appropriate Digital Ocean API.

**Endpoint:** `POST /route`

**Request Body:**
```json
{
  "image_base64": "string (optional)",
  "audio_description": "string (optional)",
  "image_url": "string (optional)"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/route \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "audio_description": "Person making hand gestures"
  }'
```

**Response:**
```json
{
  "routing_decision": {
    "route": "sign_language",
    "confidence": 0.95,
    "reasoning": "Hand gestures and sign language patterns detected",
    "error": false
  },
  "api_response": {
    "gesture": "hello",
    "confidence": 0.92
  },
  "status": "success"
}
```

**Status Values:**
- `success` - Route determined and API called successfully
- `skipped` - Low confidence or error, API not called
- `error` - Error occurred during processing

---

### 4. Upload Files

Upload image and/or audio files directly instead of base64 encoding.

**Endpoint:** `POST /route/upload`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `image` (file, optional) - Image file from camera
- `audio` (file, optional) - Audio file
- `audio_description` (string, optional) - Text description

**Example Request:**
```bash
curl -X POST http://localhost:8000/route/upload \
  -F "image=@frame.jpg" \
  -F "audio_description=Someone speaking"
```

**Response:** Same as `/route` endpoint

---

### 5. Force Route Endpoints

For testing - bypass semantic routing and call specific APIs directly.

#### Force Speech API
**Endpoint:** `POST /route/speech`

**Request Body:**
```json
{
  "audio_description": "Text to process"
}
```

#### Force People Recognition API
**Endpoint:** `POST /route/people`

**Request Body:**
```json
{
  "image_base64": "base64_encoded_image"
}
```

#### Force Sign Language API
**Endpoint:** `POST /route/sign-language`

**Request Body:**
```json
{
  "image_base64": "base64_encoded_image"
}
```

---

## Integration Examples

### Python Example
```python
import requests
import base64

def send_frame_to_router(image_path, audio_desc=None):
    # Encode image
    with open(image_path, 'rb') as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    # Prepare request
    payload = {
        "image_base64": img_base64
    }
    if audio_desc:
        payload["audio_description"] = audio_desc
    
    # Send to router
    response = requests.post(
        "http://localhost:8000/route",
        json=payload
    )
    
    return response.json()

# Use it
result = send_frame_to_router("camera_frame.jpg", "Someone speaking")
print(f"Route: {result['routing_decision']['route']}")
print(f"Confidence: {result['routing_decision']['confidence']}")
```

### JavaScript/Node.js Example
```javascript
const fs = require('fs');
const axios = require('axios');

async function sendFrameToRouter(imagePath, audioDesc = null) {
  // Read and encode image
  const imageBuffer = fs.readFileSync(imagePath);
  const imageBase64 = imageBuffer.toString('base64');
  
  // Prepare request
  const payload = {
    image_base64: imageBase64
  };
  if (audioDesc) {
    payload.audio_description = audioDesc;
  }
  
  // Send to router
  const response = await axios.post(
    'http://localhost:8000/route',
    payload
  );
  
  return response.data;
}

// Use it
sendFrameToRouter('camera_frame.jpg', 'Someone speaking')
  .then(result => {
    console.log('Route:', result.routing_decision.route);
    console.log('Confidence:', result.routing_decision.confidence);
  });
```

### cURL Example
```bash
# Analyze only
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "audio_description": "Person waving hands in sign language"
  }'

# Route and execute
curl -X POST http://localhost:8000/route \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "'$(base64 -i frame.jpg)'",
    "audio_description": "Person speaking"
  }'

# Upload file
curl -X POST http://localhost:8000/route/upload \
  -F "image=@frame.jpg" \
  -F "audio_description=Someone speaking"
```

---

## Error Handling

### Low Confidence Response
```json
{
  "routing_decision": {
    "route": "none",
    "confidence": 0.45,
    "reasoning": "Unclear frame content",
    "error": false
  },
  "api_response": null,
  "status": "skipped"
}
```

### Error Response
```json
{
  "routing_decision": {
    "route": "none",
    "confidence": 0.0,
    "reasoning": "Error: API connection failed",
    "error": true
  },
  "api_response": null,
  "status": "error",
  "error": "Connection timeout to target API"
}
```

---

## Configuration

### Environment Variables

Required in `.env` file:

```env
# OpenRouter Configuration
OPENROUTER_API_KEY=sk-or-v1-xxx

# Model Selection
GEMINI_MODEL=google/gemini-2.0-flash-exp:free

# Target APIs (Your Digital Ocean endpoints)
SPEECH_API_URL=https://speech.yourdomain.com/api/process
PEOPLE_RECOGNITION_API_URL=https://people.yourdomain.com/api/recognize
SIGN_LANGUAGE_API_URL=https://signlang.yourdomain.com/api/detect

# Routing Threshold
CONFIDENCE_THRESHOLD=0.7
```

### Adjusting Confidence Threshold

Lower threshold (0.5) = More sensitive, routes more often
Higher threshold (0.9) = More conservative, only high-confidence routes

---

## Performance Considerations

- **Latency**: Gemini analysis typically takes 1-3 seconds
- **Rate Limits**: Free tier OpenRouter has rate limits
- **Image Size**: Recommend max 1MB images for faster processing
- **Concurrent Requests**: Server handles multiple requests asynchronously

---

## Troubleshooting

### Router returns `route: "none"` frequently
- Check image quality and lighting
- Provide more context in `audio_description`
- Lower `CONFIDENCE_THRESHOLD` in `.env`

### Target API errors
- Verify Digital Ocean API URLs are correct
- Check API credentials and authentication
- Test APIs independently with curl

### OpenRouter errors
- Verify `OPENROUTER_API_KEY` is valid
- Check rate limits on free tier
- Try different Gemini model

---

## Support

For issues:
1. Check logs: `python api_server.py` (console output)
2. Test with `python test_router.py`
3. Verify `.env` configuration
4. Check Digital Ocean API status
