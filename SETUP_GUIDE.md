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
