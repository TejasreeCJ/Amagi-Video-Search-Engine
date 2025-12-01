# Docker Setup Guide

This guide explains how to containerize and deploy the Amagi Video Search Engine using Docker.

## Prerequisites

- Docker Desktop installed on Windows
- Docker Compose (included with Docker Desktop)
- Neo4j AuraDB credentials
- GEMINI_API_KEY from Google AI Studio

## Project Structure

The project consists of:

- **Backend**: Python FastAPI application (serves API and frontend)
- **Frontend**: Static HTML/CSS/JavaScript files (served by FastAPI)

## Environment Variables

The following environment variables are required:

### Required:

- `NEO4J_URI`: Your Neo4j AuraDB connection URI (e.g., `neo4j+s://xxxxx.databases.neo4j.io`)
- `NEO4J_USER`: Neo4j username (usually `neo4j`)
- `NEO4J_PASSWORD`: Neo4j AuraDB password
- `GEMINI_API_KEY`: Your Google Gemini API key

### Optional:

- `PINECONE_API_KEY`: Pinecone API key (if still using Pinecone)
- `PINECONE_ENVIRONMENT`: Pinecone environment (default: `us-east-1-aws`)
- `PINECONE_INDEX_NAME`: Pinecone index name (default: `nptel-video-search`)
- `YOUTUBE_API_KEY`: YouTube API key (optional)

## Setup Instructions

### Step 1: Create Environment File

Create a `.env` file in the project root directory with your credentials:

```env
# Neo4j AuraDB Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here

# Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Pinecone Configuration
PINECONE_API_KEY=your-pinecone-api-key-here
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=nptel-video-search

# Optional: YouTube API Key
YOUTUBE_API_KEY=your-youtube-api-key-here
```

**⚠️ IMPORTANT**:

- Never commit the `.env` file to version control (it's already in `.gitignore`)
- The `.env` file contains sensitive credentials
- In production, use Docker secrets or environment variables set directly in your deployment platform

### Step 2: Build and Run with Docker Compose (Recommended)

This is the easiest method:

```powershell
# Build and start the container
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

The application will be available at:

- **Frontend & API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Step 3: Build and Run with Docker (Manual)

If you prefer to use Docker directly:

```powershell
# Build the Docker image
docker build -t amagi-video-search .

# Run the container with environment variables
docker run -d `
  --name amagi-video-search `
  -p 8000:8000 `
  --env-file .env `
  amagi-video-search
```

Or set environment variables directly (not recommended for production):

```powershell
docker run -d `
  --name amagi-video-search `
  -p 8000:8000 `
  -e NEO4J_URI="neo4j+s://your-instance.databases.neo4j.io" `
  -e NEO4J_USER="neo4j" `
  -e NEO4J_PASSWORD="your-password" `
  -e GEMINI_API_KEY="your-api-key" `
  amagi-video-search
```

## Managing the Container

### View Logs

```powershell
# Using docker-compose
docker-compose logs -f

# Using docker
docker logs -f amagi-video-search
```

### Stop the Container

```powershell
# Using docker-compose
docker-compose down

# Using docker
docker stop amagi-video-search
docker rm amagi-video-search
```

### Restart the Container

```powershell
# Using docker-compose
docker-compose restart

# Using docker
docker restart amagi-video-search
```

### Access Container Shell

```powershell
docker exec -it amagi-video-search /bin/bash
```

## Security Best Practices

### 1. Environment Variables

- **Never commit `.env` files** to version control
- Use Docker secrets or environment variables in production
- Rotate API keys regularly
- Use different credentials for development and production

### 2. Production Deployment

For production deployments, consider:

- Using Docker secrets instead of `.env` files
- Setting environment variables directly in your deployment platform (AWS ECS, Azure Container Instances, etc.)
- Using a secrets management service (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- Enabling HTTPS/TLS
- Restricting CORS origins
- Using a reverse proxy (nginx) in front of the application

### 3. Example: Using Docker Secrets (Docker Swarm)

```powershell
# Create secrets
echo "your-neo4j-uri" | docker secret create neo4j_uri -
echo "your-neo4j-password" | docker secret create neo4j_password -
echo "your-gemini-key" | docker secret create gemini_api_key -

# Use in docker-compose.yml
services:
  backend:
    secrets:
      - neo4j_uri
      - neo4j_password
      - gemini_api_key
    environment:
      NEO4J_URI_FILE: /run/secrets/neo4j_uri
      NEO4J_PASSWORD_FILE: /run/secrets/neo4j_password
      GEMINI_API_KEY_FILE: /run/secrets/gemini_api_key
```

## Troubleshooting

### Container won't start

1. Check logs: `docker-compose logs` or `docker logs amagi-video-search`
2. Verify environment variables are set correctly
3. Check if port 8000 is already in use: `netstat -ano | findstr :8000`

### Connection errors to Neo4j

1. Verify `NEO4J_URI` is correct (should start with `neo4j+s://` for AuraDB)
2. Check if your IP is whitelisted in Neo4j AuraDB dashboard
3. Verify credentials are correct

### API key errors

1. Verify `GEMINI_API_KEY` is set correctly
2. Check if the API key is valid and has proper permissions
3. Check container logs for specific error messages

### Frontend can't connect to API

1. The frontend now uses relative URLs, so it should work automatically
2. If issues persist, check browser console (F12) for CORS errors
3. Verify the backend is running: `curl http://localhost:8000/api/health`

## Building for Production

### Multi-stage Build (Optional)

For smaller production images, you can use a multi-stage build. Update `Dockerfile`:

```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg git && rm -rf /var/lib/apt/lists/*
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["python", "run_server.py"]
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j AuraDB Documentation](https://neo4j.com/docs/aura/)
- [Google Gemini API Documentation](https://ai.google.dev/docs)

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify all environment variables are set
3. Ensure Docker Desktop is running
4. Check that ports are not in use by other applications
