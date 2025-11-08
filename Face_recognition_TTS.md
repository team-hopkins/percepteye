# Face Recognition API

This repository exposes a single FastAPI endpoint that runs face recognition on an uploaded image and optionally returns synthesized speech audio (via ElevenLabs TTS or a local fallback).

## Overview

- Endpoint: `POST /process`
- Content type: `multipart/form-data`
- Purpose: Accept a base64-encoded image plus optional audio file or `audio_text`, run face recognition, and return detected face names, locations, optional annotated image, transcription, and synthesized TTS audio (base64).

## Environment Variables

- `ELEVENLABS_API_KEY` (optional): API key for ElevenLabs speech-to-text and text-to-speech. If not provided, STT/TTS via ElevenLabs is skipped and local TTS fallback may be used.
- `ELEVENLABS_VOICE` (optional): Preferred ElevenLabs voice id or name. If not provided, the code attempts to use a fallback voice.

## /process — Request

POST /process expects `multipart/form-data`.

Form fields and types:

- `image` (string) — REQUIRED: a base64-encoded image. Accepts either a bare base64 string or a data URL (e.g. `data:image/png;base64,...`). The server validates base64 and attempts to decode as PNG/JPEG. If missing, the endpoint responds with HTTP 400.

- `audio` (file) — OPTIONAL: an uploaded audio file (e.g. WAV/MP3). If provided and `ELEVENLABS_API_KEY` is set, the server will attempt to transcribe it using ElevenLabs STT.

- `audio_text` (string) — OPTIONAL: explicit text to synthesize to speech. Precedence for TTS selection: `audio_text` > transcribed audio (`audio`) > announcement generated from recognized faces if `announce` or `speak` is true.

- `annotated` (boolean) — OPTIONAL, default `false`: if true, the response includes `annotated_image_base64` (PNG) with bounding boxes and labels drawn.

- `session_duration` (int) — OPTIONAL: unused in the single-call flow, included for compatibility with headless runner.

- `record_audio` (boolean) — OPTIONAL, default `false`: reserved flag; not required for typical requests.

- `announce` (boolean) — OPTIONAL, default `false`: if true, the system will prepare an announcement string describing recognized faces (but won't automatically speak it unless `speak` is true).

- `speak` (boolean) — OPTIONAL, default `false`: if true, the server will both prepare and attempt to speak (and synthesize) the announcement.

- `add_name` (string) — OPTIONAL: a string used by the headless runner; rarely needed for single-request flows.

- `add_padding` (int) — OPTIONAL, default `100`: padding used when drawing annotated images.

- `show_window` (boolean) — OPTIONAL, default `false`: not applicable for headless containerized runs.

Notes:

- The `image` must be provided in the request body. The endpoint currently returns 400 if missing.
- The server accepts PNG and JPEG images. If OpenCV cannot decode the image, a Pillow fallback is attempted.

Example (curl, minimal):

```bash
curl -X POST "http://localhost:8000/process" \
  -F "image=$(base64 -w 0 input.jpg)" \
  -F "audio_text=Hello, this is a test" \
  -F "annotated=true"
```

(If your `base64` command adds newlines, the server strips them. You can also pass a data URL.)

## /process — Response

On success the endpoint returns a JSON object with these fields:

- `faces` (list[str]) — list of recognized names (e.g. `['Alice', 'Unknown', 'Bob']`).
- `locations` (list[str]) — list of rough horizontal locations for each face: `"left" | "center" | "right"`.
- `unknown_count` (int) — number of faces considered unknown.
- `announcement` (string|null) — the announcement text generated from recognized faces when `announce` or `speak` is used (or null otherwise).
- `speech_text` (string|null) — the text that was used to synthesize audio (audio_text or STT or announcement).
- `annotated_image_base64` (string|null) — base64 PNG of the annotated image if `annotated=true` was requested.
- `eleven_tts_base64` (string|null) — base64-encoded audio bytes (MP3/WAV depending on backend). If ElevenLabs TTS succeeded, this contains ElevenLabs audio. If ElevenLabs failed and a local pyttsx3 fallback succeeded, it contains that audio. If no TTS was generated, this is null.
- `transcribed` (string|null) — the chosen transcription or spoken text (note: this mirrors the `speech_text` selection logic).
- `eleven_tts_error` (string|null) — a short error message if TTS/STT failed or fallback was used (helps with debugging).

Example response (success):

{
"faces": ["Alice", "Unknown"],
"locations": ["left", "right"],
"unknown_count": 1,
"announcement": "I see Alice on the left and one unknown person on the right.",
"speech_text": "I see Alice on the left and one unknown person on the right.",
"annotated_image_base64": "iVBORw0KGgoAAAANS...",
"eleven_tts_base64": "SUQzBAAAAA...",
"transcribed": "I see Alice on the left",
"eleven_tts_error": null
}

Error responses:

- 400 Bad Request: malformed or missing `image` base64, invalid base64, or decoding failures.
- 500 Internal Server Error: unexpected server-side error (face recognition initialization issues, runtime exceptions).

## Implementation notes / behavior

- The API uses the `FaceRecognitionWithTTS` class from `main_script.py` for recognition logic. The server initializes one instance at startup and reuses it.
- Image decoding path:
  1. Base64 decode
  2. Try `cv2.imdecode`
  3. If OpenCV fails, try Pillow fallback
- Face detection: The recognizer may internally upscale tiny images and map face coordinates back to the original image size.
- STT/TTS: If `audio` is provided, and `ELEVENLABS_API_KEY` is set, the audio is sent to ElevenLabs for transcription. For TTS, the server prefers `audio_text` if provided, otherwise uses transcribed text, otherwise announcement text. If ElevenLabs TTS fails or the voice is unavailable, the server attempts a local pyttsx3 fallback (if available in the runtime environment).

## Docker / Running locally

The repo includes a `Dockerfile` and `docker-compose.yml` to run the API in a container. Important notes:

- Building the image compiles native extensions like `dlib` (face_recognition) and can take several minutes and significant CPU/RAM.
- Ensure Docker has sufficient build resources (CPU/RAM) to compile `dlib` successfully.

Quick start (after setting `ELEVENLABS_API_KEY` in your environment):

```bash
# Build
docker compose build
# Run
docker compose up -d
# Check logs
docker compose logs -f
```

Open http://localhost:8000/docs to view the interactive FastAPI docs.

## Troubleshooting

- Error: "Could not decode image": The incoming image data may be truncated. Confirm you're sending a full base64 string.
- Error: "Form data requires python-multipart": Ensure `python-multipart` is installed (it is included in `requirements.txt`). Rebuild the image after updating `requirements.txt`.
- Error: pyttsx3/espeak voice errors in container: The container may not have the expected espeak voices installed; the server will try to continue and prefer ElevenLabs TTS when available.

## Example Python client

```python
import base64
import requests

with open('test.jpg','rb') as fh:
    b64 = base64.b64encode(fh.read()).decode('ascii')

resp = requests.post('http://localhost:8000/process', data={'image': b64, 'audio_text': 'Hello!'}, timeout=60)
print(resp.status_code)
print(resp.json())
```

## Security / Notes

- Do not commit your ElevenLabs API key into source control. Provide it via environment variables at runtime.
- This API can run resource-heavy workloads (dlib). For production deployments, consider prebuilt wheels for dlib or using a GPU-enabled image.

---

If you'd like, I can also:

- Add a short `README.docker.md` section with tips for reducing image size (multi-stage builds / caching).
- Add an automated curl or Python test script under `tests/` that posts a small sample image and prints the response.
