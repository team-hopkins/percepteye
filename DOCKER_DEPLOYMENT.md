# Docker Deployment Guide for PerceptEye Semantic Router

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Get Docker Compose](https://docs.docker.com/compose/install/))
- `.env` file configured with your API keys

## Quick Start

### 1. Configure Environment Variables

Create `.env` file from the example:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
OPENROUTER_API_KEY=your_key_here
SPEECH_API_URL=https://your-speech-api.digitalocean.com/api/process
PEOPLE_RECOGNITION_API_URL=https://your-people-api.digitalocean.com/api/recognize
SIGN_LANGUAGE_API_URL=https://your-sign-language-api.digitalocean.com/api/detect
```

### 2. Build and Run with Docker Compose

```bash
# Build and start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

The API will be available at: `http://localhost:8000`

### 3. Test the Deployment

```bash
# Health check
curl http://localhost:8000/health

# Test analysis endpoint
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"audio_description": "Someone is speaking"}'
```

## Docker Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f semantic-router

# View real-time stats
docker stats percepteye-semantic-router
```

### Building and Updating

```bash
# Rebuild after code changes
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Pull latest changes and restart
docker-compose up -d --build
```

### Maintenance

```bash
# Stop and remove containers, networks
docker-compose down

# Stop and remove containers, networks, volumes
docker-compose down -v

# Remove unused images
docker image prune -a

# View container logs (last 100 lines)
docker-compose logs --tail=100 semantic-router
```

## Using Docker (without Compose)

### Build the Image

```bash
docker build -t percepteye-router:latest .
```

### Run the Container

```bash
docker run -d \
  --name percepteye-router \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  percepteye-router:latest
```

### View Logs

```bash
docker logs -f percepteye-router
```

### Stop and Remove

```bash
docker stop percepteye-router
docker rm percepteye-router
```

## Production Deployment

### 1. Environment Variables

For production, use environment variables instead of `.env` file:

```bash
docker run -d \
  --name percepteye-router \
  -p 8000:8000 \
  -e OPENROUTER_API_KEY=your_key \
  -e SPEECH_API_URL=https://your-api.com \
  -e PEOPLE_RECOGNITION_API_URL=https://your-api.com \
  -e SIGN_LANGUAGE_API_URL=https://your-api.com \
  -e CONFIDENCE_THRESHOLD=0.7 \
  --restart unless-stopped \
  percepteye-router:latest
```

### 2. Using with Reverse Proxy (Nginx)

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for long-running requests
        proxy_read_timeout 90s;
        proxy_connect_timeout 90s;
    }
}
```

### 3. Docker Compose with Nginx

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  semantic-router:
    build: .
    container_name: percepteye-router
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - SPEECH_API_URL=${SPEECH_API_URL}
      - PEOPLE_RECOGNITION_API_URL=${PEOPLE_RECOGNITION_API_URL}
      - SIGN_LANGUAGE_API_URL=${SIGN_LANGUAGE_API_URL}
    restart: always
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: percepteye-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - semantic-router
    restart: always
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

## Deployment Platforms

### Deploy to Digital Ocean

1. **Using App Platform:**
   - Connect your repository
   - Set environment variables in the dashboard
   - App Platform will detect Dockerfile automatically

2. **Using Droplet:**
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt-get install docker-compose-plugin

# Clone your repository
git clone your-repo-url
cd percepteye

# Create .env file
nano .env

# Run with Docker Compose
docker-compose up -d
```

### Deploy to AWS ECS

```bash
# Build for ARM64 (if using Graviton)
docker buildx build --platform linux/amd64,linux/arm64 -t percepteye-router .

# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker tag percepteye-router:latest your-account.dkr.ecr.us-east-1.amazonaws.com/percepteye-router:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/percepteye-router:latest
```

### Deploy to Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/your-project/percepteye-router

# Deploy
gcloud run deploy percepteye-router \
  --image gcr.io/your-project/percepteye-router \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENROUTER_API_KEY=your_key,SPEECH_API_URL=your_url
```

## Monitoring and Debugging

### View Container Logs

```bash
# Follow logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Logs from specific time
docker-compose logs --since 30m
```

### Execute Commands Inside Container

```bash
# Open shell
docker-compose exec semantic-router sh

# Run Python
docker-compose exec semantic-router python -c "import semantic_router; print('OK')"

# Check environment variables
docker-compose exec semantic-router env
```

### Health Checks

```bash
# Check health status
docker inspect percepteye-semantic-router | jq '.[0].State.Health'

# Manual health check
curl http://localhost:8000/health
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs semantic-router

# Check if port is in use
lsof -i :8000

# Remove and rebuild
docker-compose down
docker-compose up -d --build
```

### Connection Issues

```bash
# Test from within container
docker-compose exec semantic-router curl http://localhost:8000/health

# Check network
docker network inspect percepteye-network
```

### Performance Issues

```bash
# Check resource usage
docker stats

# Increase resources in docker-compose.yml
services:
  semantic-router:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## Security Best Practices

1. **Never commit `.env` file**
2. **Use secrets management in production**
3. **Run as non-root user** (already configured)
4. **Keep base images updated**
5. **Scan for vulnerabilities:**
   ```bash
   docker scan percepteye-router:latest
   ```

## Updating the Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build

# Or without downtime
docker-compose build
docker-compose up -d --no-deps semantic-router
```

## Backup and Restore

### Backup Configuration

```bash
# Backup .env file
cp .env .env.backup

# Export image
docker save percepteye-router:latest | gzip > percepteye-router.tar.gz
```

### Restore

```bash
# Load image
gunzip -c percepteye-router.tar.gz | docker load

# Restore .env
cp .env.backup .env
```
