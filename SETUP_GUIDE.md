# Quick Setup Guide - Step by Step

This is a condensed step-by-step guide for setting up the Amagi Video Search Engine.

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] FFmpeg installed (for Whisper)
- [ ] Neo4j Desktop or AuraDB account
- [ ] Google Gemini API key

## Installation Steps

### 1. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**
- Download from https://ffmpeg.org/download.html
- Or use Chocolatey: `choco install ffmpeg`
- Add to PATH if not automatic

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg      # CentOS/RHEL
```

Verify: `ffmpeg -version`

### 3. Set Up Neo4j

**Option A: Neo4j Desktop (Local)**
1. Download: https://neo4j.com/download/
2. Install and launch
3. Create new project → Add Local DBMS
4. Set name and password (remember it!)
5. Start the database
6. Note: URI = `bolt://localhost:7687`, User = `neo4j`

**Option B: Neo4j AuraDB (Cloud)**
1. Sign up: https://neo4j.com/cloud/aura/
2. Create free instance
3. Copy connection details (URI, username, password)

### 4. Get Google Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

### 5. Configure Environment

```bash
# Create .env file
python setup_env.py

# Edit .env file and add:
# - GEMINI_API_KEY=your_key_here
# - NEO4J_URI=bolt://localhost:7687 (or your AuraDB URI)
# - NEO4J_USER=neo4j
# - NEO4J_PASSWORD=your_password_here
```

### 6. Verify Setup

```bash
python test_setup.py
```

Should show all checks passing ✓

### 7. Start the Server

```bash
python run_server.py
```

Server runs on: http://localhost:8000

### 8. Open Frontend

**Option A:** Open `frontend/index.html` directly in browser

**Option B:** Use local server:
```bash
cd frontend
python -m http.server 8080
```
Then open: http://localhost:8080

## Quick Test

1. Open the web interface
2. Paste a YouTube playlist URL
3. Click "Process Playlist"
4. Wait for processing (may take a few minutes)
5. Search for a topic
6. Click a result to watch the video clip

## Common Issues

**"Module not found"** → Activate virtual environment and reinstall: `pip install -r requirements.txt`

**"Neo4j connection failed"** → Check Neo4j is running and credentials in .env are correct

**"GEMINI_API_KEY not set"** → Add your API key to .env file

**"FFmpeg not found"** → Install FFmpeg and ensure it's in PATH

**"No transcripts found"** → Enable Whisper: Set `WHISPER_ENABLED=true` in .env

## Next Steps

- Process your first playlist
- Try different search queries
- Enable Whisper for videos without subtitles
- Customize embedding model in `backend/config.py`

For detailed information, see [README.md](README.md)

