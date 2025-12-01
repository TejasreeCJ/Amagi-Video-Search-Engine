# Docker Commands Reference

## Starting the Container

### Option 1: Using Docker Compose (Recommended)

```powershell
# Start the container (foreground - you'll see logs)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Start and rebuild if needed
docker-compose up --build -d
```

### Option 2: Using Docker Directly

```powershell
# If you built the image manually
docker run -d --name amagi-video-search -p 8000:8000 --env-file .env amagi-video-search
```

## Checking if Application is Running

### 1. Check Container Status

```powershell
# List running containers
docker ps

# Or with docker-compose
docker-compose ps
```

You should see output like:
```
CONTAINER ID   IMAGE                    STATUS          PORTS                    NAMES
abc123def456   amagi-video-search       Up 2 minutes    0.0.0.0:8000->8000/tcp   amagi-video-search-backend
```

### 2. Check Container Health

```powershell
# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Or with docker-compose
docker-compose ps
```

### 3. Test the Application Endpoints

#### In Browser:
- **Frontend**: http://localhost:8000
- **API Health Check**: http://localhost:8000/api/health
- **API Documentation**: http://localhost:8000/docs

#### Using PowerShell (curl equivalent):
```powershell
# Test health endpoint
Invoke-WebRequest -Uri http://localhost:8000/api/health

# Or using curl (if available)
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "healthy"}
```

### 4. Check if Port is Listening

```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Or using PowerShell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

## Viewing Application Logs

### Real-time Logs (Follow Mode)

```powershell
# View logs in real-time (follow mode)
docker-compose logs -f

# Or using docker directly
docker logs -f amagi-video-search-backend
```

### View Recent Logs

```powershell
# Last 100 lines
docker-compose logs --tail=100

# Last 50 lines
docker logs --tail=50 amagi-video-search-backend
```

### View Logs Since Container Started

```powershell
# All logs since container start
docker-compose logs

# Or
docker logs amagi-video-search-backend
```

### View Logs with Timestamps

```powershell
# With timestamps
docker-compose logs -f -t

# Or
docker logs -f -t amagi-video-search-backend
```

### View Logs for Specific Time Period

```powershell
# Logs since 10 minutes ago
docker logs --since 10m amagi-video-search-backend

# Logs since 1 hour ago
docker logs --since 1h amagi-video-search-backend

# Logs between timestamps
docker logs --since 2024-01-01T00:00:00 --until 2024-01-01T12:00:00 amagi-video-search-backend
```

## Common Operations

### Stop the Container

```powershell
# Stop (keeps container)
docker-compose stop

# Or
docker stop amagi-video-search-backend
```

### Start a Stopped Container

```powershell
# Start stopped container
docker-compose start

# Or
docker start amagi-video-search-backend
```

### Restart the Container

```powershell
# Restart
docker-compose restart

# Or
docker restart amagi-video-search-backend
```

### Remove the Container

```powershell
# Stop and remove
docker-compose down

# Remove with volumes
docker-compose down -v

# Or using docker
docker stop amagi-video-search-backend
docker rm amagi-video-search-backend
```

### Access Container Shell

```powershell
# Open bash shell in running container
docker exec -it amagi-video-search-backend /bin/bash

# Or sh if bash not available
docker exec -it amagi-video-search-backend /bin/sh
```

### Check Container Resource Usage

```powershell
# CPU and memory usage
docker stats amagi-video-search-backend

# Or all containers
docker stats
```

## Troubleshooting

### Container Won't Start

```powershell
# Check what went wrong
docker-compose logs

# Check container status
docker ps -a

# Inspect container
docker inspect amagi-video-search-backend
```

### Application Not Responding

```powershell
# Check if container is running
docker ps

# Check logs for errors
docker-compose logs --tail=50

# Test health endpoint
Invoke-WebRequest -Uri http://localhost:8000/api/health
```

### Port Already in Use

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Change port in docker-compose.yml:
# ports:
#   - "8001:8000"  # Use 8001 on host instead
```

### View Environment Variables

```powershell
# Check environment variables in container
docker exec amagi-video-search-backend env

# Or inspect
docker inspect amagi-video-search-backend | Select-String -Pattern "Env"
```

## Quick Reference

| Task | Command |
|------|---------|
| Start container | `docker-compose up -d` |
| View logs | `docker-compose logs -f` |
| Stop container | `docker-compose stop` |
| Restart container | `docker-compose restart` |
| Check status | `docker-compose ps` |
| Remove container | `docker-compose down` |
| Rebuild and start | `docker-compose up --build -d` |
| Access shell | `docker exec -it amagi-video-search-backend /bin/bash` |

