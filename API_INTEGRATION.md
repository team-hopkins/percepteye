# API Integration Notes

## Sign Language Detection API

The semantic router automatically integrates with the Sign Language Detection API using the specifications from `SIGN_LANGUAGE.md`.

### Endpoint Configuration

Set the **base URL** in your `.env` file:

```env
SIGN_LANGUAGE_API_URL=http://your-digital-ocean-ip:8000
```

The router automatically appends `/predict/base64` to call the correct endpoint.

### Request Format

The router sends:

```json
POST http://your-ip:8000/predict/base64
Content-Type: application/json

{
  "image_base64": "<base64_encoded_image>"
}
```

### Response Handling

The router expects and handles this response structure:

**Success with hand detected:**

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

**No hand detected:**

```json
{
  "success": true,
  "predicted_sign": null,
  "confidence": null,
  "hand_detected": false,
  "message": "No hand detected in image"
}
```

### Confidence Filtering

The semantic router uses a confidence threshold (default: 0.7) to filter predictions:

- Only predictions with `confidence > 0.7` are considered valid
- Lower confidence predictions are treated as uncertain

### Testing the Integration

1. **Check API health:**

```bash
curl http://your-sign-language-api:8000/health
```

2. **Test from semantic router:**

```bash
curl -X POST http://localhost:8000/route \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "your_base64_image",
    "audio_description": "Person making hand gestures"
  }'
```

3. **Expected routing decision:**

```json
{
  "routing_decision": {
    "route": "sign_language",
    "confidence": 0.95,
    "reasoning": "Hand gestures detected in frame"
  },
  "api_response": {
    "success": true,
    "predicted_sign": "B",
    "confidence": 0.9958,
    "contextual_meaning": "I need a bathroom",
    "alternative_contexts": [
      "The letter B",
      "I need to go back",
      "Book please"
    ],
    "hand_detected": true,
    "message": "Prediction successful"
  },
  "status": "success"
}
```

## Other APIs

### Speech API (Eleven Labs)

- Endpoint configured as-is in `SPEECH_API_URL`
- Handles audio data and text descriptions

### People Recognition API

- Endpoint configured as-is in `PEOPLE_RECOGNITION_API_URL`
- Receives base64 encoded images in `image` field

## Troubleshooting

### Sign Language API not responding

```bash
# Check if API is running
curl http://your-ip:8000/health

# Check if port 8000 is accessible
telnet your-ip 8000
```

### Wrong endpoint error

Make sure `SIGN_LANGUAGE_API_URL` is set to the **base URL** only:

- ✅ Correct: `http://your-ip:8000`
- ❌ Wrong: `http://your-ip:8000/predict/base64`

The router adds `/predict/base64` automatically.

### Low confidence predictions

Adjust the confidence threshold in `.env`:

```env
CONFIDENCE_THRESHOLD=0.6  # Lower for more sensitive detection
```

## Complete Integration Example

```python
# In your .env file
GEMINI_API_KEY=AIzaSy...
SIGN_LANGUAGE_API_URL=http://192.168.1.100:8000
CONFIDENCE_THRESHOLD=0.7

# The router will:
# 1. Analyze frame with Gemini
# 2. Detect hand gestures
# 3. Call http://192.168.1.100:8000/predict/base64
# 4. Return sign if confidence > 0.7 and hand_detected = true
```
