# Amagi Video Search Engine (Neo4j + Knowledge Graph Edition)

A comprehensive web application to search for specific video clips in YouTube playlists using speech-to-text data, vector embeddings, and interactive knowledge graphs. Features hybrid search combining semantic similarity with keyword matching, powered by Neo4j graph database and Google Gemini AI.

## Features

- 🔍 **Hybrid Search**: Combines vector similarity (80%) and keyword search (20%) for intelligent topic matching
- 📹 **Clip Retrieval**: Get precise video clips (not just full videos) matching your query
- 🧠 **Knowledge Graph**: Interactive visualization of chapter relationships and learning paths
- 🎯 **LLM Chapter Generation**: Uses Google Gemini to automatically create meaningful chapters from transcripts
- 📊 **Vector Embeddings**: Uses sentence-transformers for semantic search
- 🕸️ **Neo4j Graph Database**: Stores video-chapter relationships and enables graph-based recommendations
- 🎬 **Video Player**: Watch videos with clip timeline visualization and jump-to-clip functionality
- ⏱️ **Timestamp Navigation**: Jump directly to relevant clips in videos
- 🤖 **Whisper Fallback**: Automatic transcription for videos without subtitles
- 🔗 **Learning Paths**: Graph-based discovery of prerequisite topics and optimal learning sequences
- 🐳 **Docker Support**: Containerized deployment with docker-compose

## Architecture

### Backend
- **FastAPI**: RESTful API for video search and knowledge graph operations
- **yt-dlp**: Extracts video information and transcripts from YouTube
- **Google Gemini**: Generates intelligent chapters from raw transcripts using sliding window analysis
- **sentence-transformers**: Creates vector embeddings from chapter text
- **Neo4j**: Graph database for storing video-chapter relationships and vector search
- **Knowledge Graph Service**: Analyzes chapter relationships and builds interactive graphs
- **Whisper**: Fallback transcription for videos without subtitles

### Frontend
- **HTML/CSS/JavaScript**: Modern, responsive web interface
- **YouTube IFrame API**: Embedded video player with clip navigation
- **Knowledge Graph Visualization**: Interactive D3.js-based graph with multiple layouts
- **Search Interface**: Clean, intuitive search experience with result cards
- **Learning Path Discovery**: Visual pathways through prerequisite topics

## Quick Start

For detailed setup guides, see:
- [QUICKSTART.md](QUICKSTART.md) - Basic setup
- [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) - Docker deployment
- [neo4j_readme.md](neo4j_readme.md) - Neo4j-specific setup

### Quick Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Set up Neo4j database**:
   - Download Neo4j Desktop from https://neo4j.com/download/
   - Create a new project and database
   - Note the connection details (default: bolt://localhost:7687)

3. **Configure environment**:
```bash
python setup_env.py
# Edit .env file with your API keys:
# - GEMINI_API_KEY (from https://makersuite.google.com/app/apikey)
# - NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
```

4. **Test setup**:
```bash
python test_neo4j.py
python test_setup.py
```

5. **Run the server**:
```bash
python run_server.py
```

6. **Open frontend**: Open `frontend/index.html` in your browser

### Docker Setup (Alternative)

```bash
# Build and run with docker-compose
docker-compose up --build

# Or run individual containers
docker build -t amagi-video-search .
docker run -p 8000:8000 amagi-video-search
```

## Development Scripts (Windows)

We have provided PowerShell scripts to make development easier:

- **`dev.ps1`**: Automatically kills old processes, starts the backend and frontend servers, and opens the browser. Use this to start or restart the app.
- **`stop.ps1`**: Kills the backend and frontend processes.

To run them from PowerShell:
```powershell
..\dev.ps1
```

## Setup Details

### Prerequisites

- Python 3.8+
- Pinecone account (free tier available at https://www.pinecone.io/)

### Installation

See [QUICKSTART.md](QUICKSTART.md) for detailed installation instructions.

## Usage

### 1. Process a Playlist

1. Open the web application
2. Enter a YouTube playlist URL (e.g., NPTEL lecture series)
3. Click "Process Playlist"
4. Wait for the processing to complete (this may take several minutes depending on playlist size and API rate limits)

### 2. Search for Video Clips

1. Enter your search query in the search box (e.g., "law of conservation of energy")
2. Click "Search"
3. Browse through the results showing relevant video clips
4. Click on any result to watch the video with the clip highlighted

### 3. Explore Knowledge Graph

1. Navigate to the **🧠 Knowledge Graph** page
2. Click **"🔨 Build Knowledge Graph"** to analyze chapter relationships
3. Explore the interactive graph:
   - Click nodes to view chapter details
   - Switch between Force Directed, Hierarchical, and Circular layouts
   - Filter by specific videos
   - Discover learning paths by clicking "🎯 Show Learning Path"

### 4. Watch and Navigate

1. Click on a search result to open the video player
2. The clip timeline shows where the relevant content is located
3. Click "Jump to Clip" to navigate directly to the relevant section
4. The transcript for the clip is displayed below the video
5. View related videos based on content similarity

## How It Works

### 1. Transcript Extraction
- Uses `yt-dlp` to extract automatic captions from YouTube videos
- Parses VTT format to get text with precise timestamps
- Creates segments for each transcript chunk

### 2. Embedding Generation
- Uses `sentence-transformers/all-MiniLM-L6-v2` model for embeddings
- Creates overlapping chunks for better context preservation
- Each chunk includes: text, start time, end time, video metadata

### 3. Vector Storage
- Stores embeddings in Pinecone vector database
- Each vector includes metadata: video ID, title, URL, timestamps, transcript text
- Uses cosine similarity for semantic search

### 4. RAG-based Search
- User query is converted to an embedding
- Searches Pinecone for similar vectors (semantic search)
- Returns top-k most relevant clips with metadata
- Results include relevance scores and full context

### 5. Clip Display
- Frontend displays video player with YouTube IFrame API
- Timeline slider shows clip location
- Jump-to-clip functionality navigates to precise timestamps

## Configuration

### Environment Variables (.env file)

```bash
# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Optional: Custom embedding model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Embedding Model
The default model is `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). You can change it in `backend/config.py`:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

Other good options:
- `sentence-transformers/all-mpnet-base-v2` (768 dimensions, better quality)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

### Chapter Generation Settings
Adjust window size and overlap in `backend/llm_service.py`:

```python
window_size_seconds = 300  # 5 minutes
overlap_seconds = 60       # 1 minute
```

### Knowledge Graph Settings
Configure graph building parameters in `backend/knowledge_graph_service.py`:

```python
similarity_threshold = 0.7  # Minimum similarity for relationships
max_connections = 5         # Maximum connections per chapter
```

## Project Structure

```
Amagi/
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── youtube_scraper.py      # YouTube data extraction
│   ├── embedding_service.py    # Vector embedding generation
│   ├── pinecone_service.py     # Pinecone integration
│   └── rag_service.py          # RAG search service
├── frontend/
│   ├── index.html              # Main HTML page
│   ├── styles.css              # Styling
│   └── app.js                  # Frontend logic
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## API Endpoints

### Video Processing & Search

#### `POST /api/process-playlist`
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

#### `POST /api/search`
Search for video chapters matching a query using hybrid search.

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

### Knowledge Graph

#### `POST /api/knowledge-graph/build`
Build the knowledge graph by analyzing chapter relationships.

**Parameters:**
- `similarity_threshold` (float, default: 0.7): Minimum similarity for relationships
- `max_connections` (int, default: 5): Maximum connections per chapter

**Response:**
```json
{
  "message": "Knowledge graph built successfully",
  "nodes_created": 45,
  "relationships_created": 120
}
```

#### `GET /api/knowledge-graph`
Get graph data for visualization.

**Parameters:**
- `video_id` (optional): Filter by specific video
- `limit` (int, default: 100): Maximum nodes to return

**Response:**
```json
{
  "nodes": [
    {
      "id": "chapter_1",
      "label": "Newton's Laws",
      "title": "Newton's First Law",
      "description": "Inertia and force...",
      "video_title": "Physics Basics",
      "start": 0,
      "end": 300
    }
  ],
  "relationships": [
    {
      "source": "chapter_1",
      "target": "chapter_2",
      "type": "NEXT_TOPIC",
      "strength": 1.0
    }
  ]
}
```

#### `GET /api/knowledge-graph/learning-path/{target_chapter_id}`
Get the optimal learning path to a target chapter.

**Response:**
```json
{
  "learning_path": [
    {
      "chapter_id": "prereq_1",
      "title": "Basic Concepts",
      "reason": "Prerequisite for understanding Newton's Laws"
    },
    {
      "chapter_id": "target_chapter",
      "title": "Newton's Laws",
      "reason": "Target learning objective"
    }
  ]
}
```

## Troubleshooting

### Issue: "GEMINI_API_KEY not set"
- Make sure you've created a `.env` file with your Gemini API key from https://makersuite.google.com/app/apikey
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

### Issue: "Knowledge graph not building"
- Ensure at least 2+ videos have been processed
- Check Neo4j connection and database contents
- Try lowering similarity_threshold if too few relationships are created

### Issue: "LLM chapter generation failed"
- Check your Gemini API key and quota
- Rate limiting may cause temporary failures
- The system continues with raw transcript chunks as fallback

### Issue: "YouTube player not loading"
- Check your internet connection
- Make sure the YouTube IFrame API is accessible
- Try a different browser or clear cache

### Issue: "Docker build fails"
- Ensure Docker and docker-compose are installed
- Check that all required ports are available
- Verify .env file is properly configured

## Future Enhancements

- [ ] Support for multiple languages
- [ ] Advanced filtering (by video, date, duration)
- [ ] Batch processing for large playlists
- [ ] Export search results
- [ ] User authentication and saved searches
- [ ] Better chunking strategies for long transcripts
- [ ] Integration with other video platforms
- [ ] Advanced RAG with LLM for query understanding

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Google for Gemini AI and YouTube
- Neo4j for graph database technology
- sentence-transformers for embeddings
- yt-dlp for YouTube data extraction
- OpenAI for Whisper transcription
- D3.js for graph visualization

