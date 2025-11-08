# Semantic Router - API Integration Update

## Summary

The semantic router has been updated to integrate with the **merged Face Recognition + TTS API**, which combines the previously separate Speech API and People Recognition API into a single unified endpoint.

## What Changed

### Architecture Update

**Before:**

```
Semantic Router
    ├→ Speech API (Eleven Labs)
    ├→ People Recognition API
    └→ Sign Language API
```

**After:**

```
Semantic Router
    ├→ Face Recognition + TTS API (combined speech + face recognition)
    └→ Sign Language API
```

### API Routes

**Previous Routes:**

- `speech` - For audio/speech processing
- `people_recognition` - For face detection
- `sign_language` - For sign language gestures
- `none` - No action

**Updated Routes:**

- `face_recognition_tts` - For faces, people, AND audio/speech (replaces both `speech` and `people_recognition`)
- `sign_language` - For sign language gestures
- `none` - No action

### Environment Variables

**Removed:**

- `SPEECH_API_URL`
- `PEOPLE_RECOGNITION_API_URL`

**Added:**

- `FACE_RECOGNITION_TTS_API_URL` - Points to the combined Face Recognition + TTS API endpoint

**Unchanged:**

- `SIGN_LANGUAGE_API_URL` - Currently set to `http://138.197.12.52`
- `GEMINI_API_KEY` - Your Gemini API key
- `GEMINI_MODEL` - Gemini model to use
- `CONFIDENCE_THRESHOLD` - Confidence threshold for routing

### Updated Files

1. **semantic_router.py**

   - Updated `RouteType` enum
   - Updated `RouterConfig` dataclass
   - Updated system prompt for Gemini
   - Added `_call_face_recognition_tts_api()` method
   - Deprecated `_call_speech_api()` and `_call_people_recognition_api()`

2. **api_server.py**

   - Added `/route/face-recognition` endpoint
   - Deprecated `/route/speech` and `/route/people` endpoints (still work for backward compatibility)

3. **.env** and **.env.example**

   - Replaced `SPEECH_API_URL` and `PEOPLE_RECOGNITION_API_URL` with `FACE_RECOGNITION_TTS_API_URL`

4. **docker-compose.yml**

   - Updated environment variables

5. **README.md**

   - Updated architecture diagram
   - Updated feature list
   - Updated route examples

6. **New Test File**
   - `test_face_recognition.py` - Test script for the Face Recognition + TTS API integration

## Face Recognition + TTS API Details

### Endpoint

```
POST /process
Content-Type: multipart/form-data
```

### Request Parameters

| Field        | Type    | Required | Description                                                 |
| ------------ | ------- | -------- | ----------------------------------------------------------- |
| `image`      | string  | **Yes**  | Base64-encoded image                                        |
| `audio`      | file    | No       | Audio file for transcription (WAV/MP3)                      |
| `audio_text` | string  | No       | Text to synthesize to speech                                |
| `annotated`  | boolean | No       | Return annotated image with bounding boxes (default: false) |
| `announce`   | boolean | No       | Prepare announcement from recognized faces (default: false) |
| `speak`      | boolean | No       | Synthesize speech from announcement (default: false)        |

### Response Format

```json
{
  "faces": ["Alice", "Unknown"],
  "locations": ["left", "right"],
  "unknown_count": 1,
  "announcement": "I see Alice on the left and one unknown person on the right.",
  "speech_text": "I see Alice on the left and one unknown person on the right.",
  "annotated_image_base64": "iVBORw0KGg...",
  "eleven_tts_base64": "SUQzBAAAAA...",
  "transcribed": "I see Alice on the left",
  "eleven_tts_error": null
}
```

## Routing Logic

The semantic router now uses the following logic:

1. **Face Recognition + TTS** route is selected when:

   - Faces are visible in the frame, OR
   - Audio/speech is present, OR
   - Verbal communication is needed
   - Priority: Used for person identification, face detection, audio transcription, and text-to-speech

2. **Sign Language** route is selected when:

   - Hand gestures or sign language movements are **prominently** visible
   - Sign language is the **PRIMARY focus** of the frame
   - Note: If both faces and sign language are visible, Face Recognition is preferred unless sign language is dominant

3. **None** route when:
   - Frame is unclear
   - No relevant activity detected
   - Empty frame

## Testing

### Test Sign Language (Already Working)

```bash
python test_simple.py
```

### Test Face Recognition + TTS (New)

```bash
# You'll need an image with faces
python test_face_recognition.py test/faces.jpg
```

### Test via curl

```bash
# Face Recognition + TTS
curl -X POST "http://localhost:8001/route/face-recognition" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "YOUR_BASE64_IMAGE",
    "audio_description": "I see people"
  }'

# Sign Language
curl -X POST "http://localhost:8001/route/sign-language" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "YOUR_BASE64_SIGN_LANGUAGE_IMAGE"
  }'
```

## Current Status

✅ **Sign Language API** - Deployed and working at `http://138.197.12.52`

- Successfully tested with test/B_test.jpg
- Detecting sign 'B' with 99.6% confidence

⏳ **Face Recognition + TTS API** - Needs to be deployed

- URL placeholder in .env: `https://your-face-recognition-api.digitalocean.com/process`
- Once deployed, update `FACE_RECOGNITION_TTS_API_URL` in .env

## Next Steps

1. **Deploy Face Recognition + TTS API** to Digital Ocean
2. **Update .env** with the deployed URL:
   ```bash
   FACE_RECOGNITION_TTS_API_URL=http://YOUR_DEPLOYED_IP:8000/process
   ```
3. **Restart semantic router**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```
4. **Test the integration** with `test_face_recognition.py`

## Backward Compatibility

The deprecated endpoints still work for backward compatibility:

- `/route/speech` - Now calls Face Recognition + TTS API
- `/route/people` - Now calls Face Recognition + TTS API

However, new integrations should use `/route/face-recognition` instead.

## Documentation

See also:

- `Face_recognition_TTS.md` - Detailed API documentation for the Face Recognition + TTS API
- `SIGN_LANGUAGE.md` - Detailed API documentation for the Sign Language API
- `README.md` - Main semantic router documentation
- `API_DOCUMENTATION.md` - Complete API reference for semantic router
