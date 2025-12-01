# Docker Quick Start Guide

## Quick Setup (Windows)

### 1. Create `.env` file

Create a `.env` file in the project root with your credentials:

```env
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
GEMINI_API_KEY=your-gemini-api-key
```

### 2. Build and Run

```powershell
docker-compose up --build
```

### 3. Access the Application

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Common Commands

```powershell
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

## Security Note

⚠️ **Never commit your `.env` file!** It contains sensitive credentials.

For production, use:

- Docker secrets
- Environment variables in your deployment platform
- Secrets management services (AWS Secrets Manager, Azure Key Vault, etc.)

See `DOCKER_SETUP.md` for detailed instructions.
