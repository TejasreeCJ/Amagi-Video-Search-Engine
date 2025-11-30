# NPTEL Video Search Engine

A web application to search for specific video clips in NPTEL (or any YouTube) playlists using speech-to-text data and vector embeddings with RAG (Retrieval Augmented Generation).

## Features

- 🔍 **Intelligent Search**: Search for specific topics, concepts, or questions in video transcripts
- 📹 **Clip Retrieval**: Get precise video clips (not just full videos) matching your query
- 🎯 **RAG-based**: Uses Retrieval Augmented Generation for better context understanding
- 📊 **Vector Embeddings**: Uses sentence-transformers for semantic search
- 💾 **Pinecone Storage**: Stores and retrieves vector embeddings efficiently
- 🎬 **Video Player**: Watch videos with clip timeline visualization
- ⏱️ **Timestamp Navigation**: Jump directly to relevant clips in videos

## Architecture

### Backend

- **FastAPI**: RESTful API for video search
- **yt-dlp**: Extracts video information and transcripts from YouTube
- **sentence-transformers**: Creates vector embeddings from transcript text
- **Neo4j**: Graph database for storing and searching embeddings and metadata
- **RAG Service**: Retrieval Augmented Generation for query processing

### Frontend

- **HTML/CSS/JavaScript**: Modern, responsive web interface
- **YouTube IFrame API**: Embedded video player with clip navigation
- **Search Interface**: Clean, intuitive search experience

## Quick Start

For a detailed setup guide, see [QUICKSTART.md](QUICKSTART.md).

### Quick Setup

1. **Install dependencies**:

```bash
pip install -r requirements.txt
```

2. **Configure environment**:

```bash
python setup_env.py
# Edit .env file with your Pinecone API key
```

3. **Test setup**:

```bash
python test_setup.py
```

4. **Run the server**:

```bash
python run_server.py
```

5. **Open frontend**: Open `frontend/index.html` in your browser

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
4. Wait for the processing to complete (this may take several minutes depending on playlist size)

### 2. Search for Video Clips

1. Enter your search query in the search box (e.g., "law of conservation of energy")
2. Click "Search"
3. Browse through the results showing relevant video clips
4. Click on any result to watch the video with the clip highlighted

### 3. Watch and Navigate

1. Click on a search result to open the video player
2. The clip timeline shows where the relevant content is
3. Click "Jump to Clip" to navigate directly to the relevant section
4. The transcript for the clip is displayed below the video

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

### Embedding Model

The default model is `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions). You can change it in `backend/config.py`:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

Other good options:

- `sentence-transformers/all-mpnet-base-v2` (768 dimensions, better quality)
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilingual)

### Chunk Size

Adjust chunk size and overlap in `backend/config.py`:

```python
CHUNK_SIZE = 500  # characters
CHUNK_OVERLAP = 100  # characters
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

### `POST /api/process-playlist`

Process a YouTube playlist and store embeddings in Pinecone.

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
  "videos_processed": 10,
  "chunks_created": 250
}
```

### `POST /api/search`

Search for video clips matching a query.

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
  "clips": [
    {
      "video_id": "abc123",
      "video_title": "Physics Lecture 1",
      "video_url": "https://www.youtube.com/watch?v=abc123",
      "clip_start": 125.5,
      "clip_end": 180.2,
      "transcript": "The law of conservation of energy states that...",
      "relevance_score": 0.95
    }
  ],
  "query": "law of conservation of energy"
}
```

## Troubleshooting

### Issue: "PINECONE_API_KEY not set"

- Make sure you've created a `.env` file with your Pinecone API key
- Check that the key is correct and has the right permissions

### Issue: "No transcripts found"

- Some videos may not have automatic captions
- Try a different playlist or video that has captions enabled
- Check if the video has English subtitles available

### Issue: "Search returns no results"

- Make sure you've processed a playlist first
- Check that the Pinecone index has vectors stored
- Try a different search query

### Issue: "YouTube player not loading"

- Check your internet connection
- Make sure the YouTube IFrame API is accessible
- Check browser console for errors

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

- NPTEL for educational content
- YouTube for video hosting
- Pinecone for vector database
- sentence-transformers for embeddings
- yt-dlp for YouTube data extraction
