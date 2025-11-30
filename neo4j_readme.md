# Amagi project - Video Search Engine (Neo4j + LLM)

A web application to search for specific video clips in YouTube playlists using speech-to-text data, vector embeddings, and graph-based relationships with Neo4j and LLM-powered chapter generation.

## Features

- 🔍 **Hybrid Search**: Combines vector similarity (80%) and keyword search (20%) for intelligent topic matching
- 📹 **Clip Retrieval**: Get precise video clips (not just full videos) matching your query
- 🎯 **LLM Chapter Generation**: Uses Google Gemini to automatically create meaningful chapters from transcripts
- 📊 **Vector Embeddings**: Uses sentence-transformers for semantic search
- 🕸️ **Neo4j Graph Database**: Stores video-chapter relationships and enables graph-based recommendations
- 🎬 **Video Player**: Watch videos with clip timeline visualization and jump-to-clip functionality
- ⏱️ **Timestamp Navigation**: Jump directly to relevant clips in videos
- 🤖 **Whisper Fallback**: Automatic transcription for videos without subtitles
- 🔗 **Related Videos**: Graph-based recommendations for similar content

## Architecture

### Backend
- **FastAPI**: RESTful API for video search and playlist processing
- **yt-dlp**: Extracts video information and transcripts from YouTube
- **Google Gemini**: Generates intelligent chapters from raw transcripts
- **sentence-transformers**: Creates vector embeddings from chapter text
- **Neo4j**: Graph database for storing video-chapter relationships and vector search
- **Whisper**: Fallback transcription for videos without subtitles

### Frontend
- **HTML/CSS/JavaScript**: Modern, responsive web interface
- **YouTube IFrame API**: Embedded video player with clip navigation
- **Search Interface**: Clean, intuitive search experience with result cards

## How It Works

### 1. Transcript Extraction
- Uses `yt-dlp` to extract automatic captions from YouTube videos
- Parses VTT format to get text with precise timestamps
- Falls back to Whisper AI for videos without subtitles

### 2. Chapter Generation
- Raw transcripts are divided into 5-minute windows with 1-minute overlap
- Google Gemini analyzes each window to identify topics and create chapters
- Each chapter includes: title, description, key concepts, and precise timestamps

### 3. Embedding Creation
- Uses `sentence-transformers/all-MiniLM-L6-v2` model for embeddings
- Creates vectors for each chapter (title + description)
- 384-dimensional vectors for efficient similarity search

### 4. Graph Storage
- Videos and chapters stored as nodes in Neo4j graph database
- Relationships: Video → HAS_CHAPTER → Chapter
- Vector indexes for fast similarity search
- Fulltext indexes for keyword search

### 5. Hybrid Search
- User query converted to embedding
- Searches Neo4j using both vector similarity and keyword matching
- Weighted combination: 80% semantic similarity + 20% keyword relevance
- Returns top-k most relevant chapters with video metadata

### 6. Clip Display
- Frontend displays video player with YouTube IFrame API
- Timeline shows clip location with visual markers
- Jump-to-clip functionality navigates to precise timestamps
- Related videos suggested based on graph relationships

## Prerequisites

- Python 3.8+
- Neo4j Database (local installation or Neo4j AuraDB)
- Google Gemini API Key

## Setup Instructions

### Windows

#### 1. Install Python
```bash
# Download from https://www.python.org/downloads/
# Or using Chocolatey:
choco install python
```

#### 2. Install Neo4j Desktop
```bash
# Download from https://neo4j.com/download/
# Create a new project and database
# Default credentials: neo4j/neo4j (change password on first login)
```

#### 3. Get Google Gemini API Key
- Visit https://makersuite.google.com/app/apikey
- Create a new API key
- Copy the key for later use

#### 4. Clone and Setup Project
```bash
cd Downloads
git clone <repository-url>
cd Amagi-Video-Search-Engine

# Install dependencies
pip install -r requirements.txt

# Setup environment
python setup_env.py
# Edit .env file with your API keys
```

#### 5. Configure Neo4j
- Open Neo4j Desktop
- Start your database
- Note the connection details (usually bolt://localhost:7687)
- Update .env file with Neo4j credentials

#### 6. Test Setup
```bash
python test_neo4j.py
python test_setup.py
```

#### 7. Run the Application
```bash
# Start backend
python run_server.py

# Open frontend in browser
start frontend/index.html
```

### macOS

#### 1. Install Python
```bash
# Using Homebrew
brew install python

# Or download from https://www.python.org/downloads/
```

#### 2. Install Neo4j Desktop
```bash
# Download from https://neo4j.com/download/
# Or using Homebrew:
brew install --cask neo4j
```

#### 3. Get Google Gemini API Key
- Visit https://makersuite.google.com/app/apikey
- Create a new API key

#### 4. Clone and Setup Project
```bash
cd Downloads
git clone <repository-url>
cd Amagi-Video-Search-Engine

# Install dependencies
pip install -r requirements.txt

# Setup environment
python setup_env.py
```

#### 5. Configure Neo4j
- Open Neo4j Desktop
- Create and start a database
- Update .env with connection details

#### 6. Test Setup
```bash
python test_neo4j.py
python test_setup.py
```

#### 7. Run the Application
```bash
# Start backend
python run_server.py

# Open frontend
open frontend/index.html
```

### Linux (Ubuntu/Debian)

#### 1. Install Python
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### 2. Install Neo4j
```bash
# Add Neo4j repository
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com/ stable latest' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt update

# Install Neo4j
sudo apt install neo4j

# Start Neo4j service
sudo systemctl enable neo4j
sudo systemctl start neo4j

# Set password (default user: neo4j)
sudo neo4j-admin set-initial-password your_password_here
```

#### 3. Get Google Gemini API Key
- Visit https://makersuite.google.com/app/apikey
- Create a new API key

#### 4. Clone and Setup Project
```bash
cd Downloads
git clone <repository-url>
cd Amagi-Video-Search-Engine

# Install dependencies
pip install -r requirements.txt

# Setup environment
python setup_env.py
```

#### 5. Configure Neo4j
- Update .env with Neo4j credentials (usually bolt://localhost:7687)

#### 6. Test Setup
```bash
python test_neo4j.py
python test_setup.py
```

#### 7. Run the Application
```bash
# Start backend
python run_server.py

# Open frontend
xdg-open frontend/index.html
```

## Usage

### 1. Process a Playlist

1. Open the web application in your browser
2. Enter a YouTube playlist URL in the "Process Playlist" section
3. Click "Process Playlist"
4. Wait for processing to complete (may take several minutes depending on playlist size and API rate limits)

### 2. Search for Video Clips

1. Enter your search query in the search box (e.g., "law of conservation of energy")
2. Click "Search"
3. Browse through the results showing relevant video clips
4. Click on any result to watch the video with the clip highlighted

### 3. Watch and Navigate

1. Click on a search result to open the video player
2. The clip timeline shows where the relevant content is located
3. Click "Jump to Clip" to navigate directly to the relevant section
4. The transcript for the clip is displayed below the video
5. View related videos based on content similarity

## Configuration

### Environment Variables (.env file)

```bash
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### Embedding Model
The default model is `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). You can change it in `backend/config.py`:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

Other options:
- `sentence-transformers/all-mpnet-base-v2` (768 dimensions, better quality)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

### Chapter Generation Settings
Adjust window size and overlap in `backend/llm_service.py`:

```python
window_size_seconds = 300  # 5 minutes
overlap_seconds = 60       # 1 minute
```

## API Endpoints

### `POST /api/process-playlist`
Process a YouTube playlist and store chapters in Neo4j.

**Request:**
```json
{
  "playlist_url": "https://www.youtube.com/playlist?list=..."
}
```

**Response:**
```json
{
  "message": "Playlist processed successfully",
  "videos_processed": 5,
  "total_videos": 10
}
```

### `POST /api/search`
Search for video chapters matching a query.

**Request:**
```json
{
  "query": "law of conservation of energy",
  "top_k": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "video_title": "Physics Lecture 1",
      "video_url": "https://www.youtube.com/watch?v=abc123",
      "chapter_title": "Conservation Laws",
      "chapter_description": "Discussion of conservation of energy principle...",
      "start": 125.5,
      "end": 180.2,
      "score": 0.95
    }
  ],
  "query": "law of conservation of energy"
}
```

### `GET /api/related/{video_id}`
Get related videos based on graph relationships.

**Response:**
```json
{
  "related_videos": [
    {
      "title": "Similar Physics Lecture",
      "id": "def456",
      "strength": 3
    }
  ]
}
```

## Project Structure

```
Amagi-Video-Search-Engine/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── youtube_scraper.py      # YouTube data extraction
│   ├── embedding_service.py    # Vector embedding generation
│   ├── llm_service.py          # Google Gemini chapter generation
│   ├── neo4j_service.py        # Neo4j graph database integration
│   └── rag_service.py          # Legacy RAG service (Pinecone-based)
├── frontend/
│   ├── index.html              # Main HTML page
│   ├── styles.css              # Styling
│   └── app.js                  # Frontend logic
├── requirements.txt            # Python dependencies
├── setup_env.py               # Environment setup script
├── test_neo4j.py              # Neo4j connection test
├── run_server.py             # Server startup script
└── neo4j_readme.md           # This file
```

## Troubleshooting

### Issue: "GEMINI_API_KEY not set"
- Make sure you've created a `.env` file with your Gemini API key
- Check that the key is correct and has the right permissions
- Free tier has rate limits (~15 requests per minute)

### Issue: "Neo4j connection failed"
- Ensure Neo4j is running and accessible
- Check NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD in .env
- For Neo4j Desktop, verify the database is started
- For AuraDB, ensure the instance is active

### Issue: "No transcripts found"
- Some videos may not have automatic captions
- The system falls back to Whisper transcription (slower)
- Check if the video has English subtitles available

### Issue: "Search returns no results"
- Make sure you've processed a playlist first
- Check that Neo4j has chapters stored
- Verify the vector index was created successfully

### Issue: "LLM chapter generation failed"
- Check your Gemini API key and quota
- Rate limiting may cause temporary failures
- The system continues with raw transcript chunks as fallback

### Issue: "YouTube player not loading"
- Check your internet connection
- Make sure the YouTube IFrame API is accessible
- Try a different browser or clear cache

## Future Enhancements

- [ ] Support for multiple languages
- [ ] Advanced filtering (by video, date, duration)
- [ ] Batch processing for large playlists
- [ ] Export search results and chapters
- [ ] User authentication and saved searches
- [ ] Better chapter merging and refinement
- [ ] Integration with other video platforms
- [ ] Enhanced graph relationships and recommendations

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Google for Gemini AI and YouTube
- Neo4j for graph database technology
- sentence-transformers for embeddings
- yt-dlp for YouTube data extraction
- OpenAI for Whisper transcription
