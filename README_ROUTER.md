# PerceptEye Semantic Router

An intelligent routing middleware that uses OpenRouter with Gemini to analyze video and audio frames and route requests to the appropriate API endpoints.

## Features

- **Intelligent Routing**: Uses Gemini (via OpenRouter) to analyze frames and determine which API to call
- **Multi-Modal Analysis**: Processes both video frames and audio input
- **Three API Routes**:
  - Speech (Text-to-Speech and Speech-to-Text via Eleven Labs)
  - People Recognition (Face detection and identification)
  - Sign Language Detection (Gesture recognition)
- **RESTful API**: FastAPI-based server for easy integration
- **Raspberry Pi Ready**: Includes client for camera capture and streaming

## Architecture

```
Raspberry Pi (Camera)
    ↓
Semantic Router (Middleware API)
    ↓ (analyzes with Gemini)
    ├→ Speech API (Eleven Labs)
    ├→ People Recognition API
    └→ Sign Language API
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
SPEECH_API_URL=https://your-speech-api.digitalocean.com/api/process
PEOPLE_RECOGNITION_API_URL=https://your-people-api.digitalocean.com/api/recognize
SIGN_LANGUAGE_API_URL=https://your-sign-language-api.digitalocean.com/api/detect
```

### 3. Get OpenRouter API Key

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Get your API key from the dashboard
3. Add it to your `.env` file

## Usage

### Starting the Server

```bash
python api_server.py
```

The server will start on `http://localhost:8000`

### API Endpoints

#### Health Check

```bash
GET /health
```

#### Analyze Frame (Decision Only)

```bash
POST /analyze
Content-Type: application/json

{
  "image_base64": "base64_encoded_image",
  "audio_description": "optional audio context"
}
```

Response:

```json
{
  "route": "speech|people_recognition|sign_language|none",
  "confidence": 0.85,
  "reasoning": "Clear hand gestures indicating sign language",
  "error": false
}
```

#### Route and Call API

```bash
POST /route
Content-Type: application/json

{
  "image_base64": "base64_encoded_image",
  "audio_description": "optional audio context"
}
```

Response:

```json
{
  "routing_decision": {
    "route": "sign_language",
    "confidence": 0.92,
    "reasoning": "Hand gestures detected"
  },
  "api_response": {
    // Response from the target API
  },
  "status": "success"
}
```

#### Upload Files

```bash
POST /route/upload
Content-Type: multipart/form-data

image: [file]
audio: [file] (optional)
audio_description: "text" (optional)
```

### Raspberry Pi Client

On your Raspberry Pi:

1. Install dependencies:

```bash
pip install opencv-python requests python-dotenv
```

2. Set the router URL:

```bash
export ROUTER_URL=http://your-server:8000
```

3. Run the client:

```bash
python raspberry_pi_client.py
```

The client will:

- Capture frames from the camera every 2 seconds
- Send frames to the semantic router
- Log routing decisions and API responses

## Testing

Run the test suite:

```bash
python test_router.py
```

This will test:

- Health check endpoint
- Frame analysis with different scenarios
- Routing decisions

## How It Works

1. **Frame Capture**: Raspberry Pi captures video frames and audio
2. **Send to Router**: Frames are sent to the semantic router API
3. **AI Analysis**: Gemini (via OpenRouter) analyzes the frame content
4. **Routing Decision**: Router determines which API to call based on:
   - Visual content (faces, hands, gestures)
   - Audio context (speech, sounds)
   - Confidence threshold (default: 0.7)
5. **API Call**: Router forwards request to appropriate API
6. **Response**: Result is returned to Raspberry Pi

## Configuration

### Confidence Threshold

Adjust the confidence threshold for routing decisions:

```env
CONFIDENCE_THRESHOLD=0.7  # 0.0 to 1.0
```

Lower values = more sensitive (may route more often)
Higher values = more conservative (only routes with high confidence)

### Gemini Model

Change the Gemini model used for analysis:

```env
GEMINI_MODEL=google/gemini-2.0-flash-exp:free
```

Available models on OpenRouter:

- `google/gemini-2.0-flash-exp:free` (Fast, free)
- `google/gemini-pro-vision` (More accurate, paid)
- `google/gemini-flash-1.5` (Balanced)

## Deployment

### Deploy to Raspberry Pi

1. Copy files to Raspberry Pi
2. Set up environment variables
3. Configure to run on startup using systemd:

```bash
sudo nano /etc/systemd/system/percepteye-client.service
```

```ini
[Unit]
Description=PerceptEye Client
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/percepteye
Environment="ROUTER_URL=http://your-server:8000"
ExecStart=/usr/bin/python3 raspberry_pi_client.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable percepteye-client
sudo systemctl start percepteye-client
```

### Deploy Router to Cloud

Deploy the semantic router API to your preferred platform:

#### Digital Ocean App Platform

1. Create a new app
2. Connect your repository
3. Set environment variables in the dashboard
4. Deploy!

#### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "api_server.py"]
```

Build and run:

```bash
docker build -t percepteye-router .
docker run -p 8000:8000 --env-file .env percepteye-router
```

## Troubleshooting

### Low Confidence Scores

If routing decisions have low confidence:

- Ensure good lighting for camera
- Provide clear audio descriptions
- Adjust confidence threshold
- Try a more powerful Gemini model

### API Errors

If target APIs fail:

- Check API URLs in `.env`
- Verify API endpoints are running
- Check network connectivity
- Review API logs

### Camera Issues on Raspberry Pi

```bash
# Test camera
raspistill -o test.jpg

# Check camera module
vcgencmd get_camera

# Enable camera
sudo raspi-config
# Interface Options > Camera > Enable
```

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
