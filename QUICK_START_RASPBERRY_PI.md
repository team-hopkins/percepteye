# 🚀 Quick Start - Raspberry Pi Integration

## Main Endpoint

```
POST http://YOUR_ROUTER_IP:8001/route
```

## Payload

```json
{
  "image_base64": "BASE64_ENCODED_IMAGE",
  "audio_description": "Optional text context"
}
```

## Minimal Python Code

```python
import requests
import base64
from picamera2 import Picamera2
from PIL import Image
import io

ROUTER_URL = "http://YOUR_ROUTER_IP:8001/route"
camera = Picamera2()
camera.start()

# Capture and send
image_data = camera.capture_array()
img = Image.fromarray(image_data)
buffer = io.BytesIO()
img.save(buffer, format='JPEG')
image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

response = requests.post(
    ROUTER_URL,
    json={"image_base64": image_base64},
    timeout=60
)

result = response.json()
print(f"Route: {result['routing_decision']['route']}")
print(f"Response: {result['api_response']}")
```

## Test Without Camera

```python
import requests
import base64

with open('test.jpg', 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

response = requests.post(
    'http://YOUR_ROUTER_IP:8001/route',
    json={'image_base64': img_b64},
    timeout=60
)

print(response.json())
```

## Response Format

```json
{
  "routing_decision": {
    "route": "face_recognition_tts" | "sign_language" | "none",
    "confidence": 0.95
  },
  "api_response": { /* API-specific response */ },
  "status": "success"
}
```

---

**See `RASPBERRY_PI_INTEGRATION.md` for complete documentation**
