# Project Summary: NPTEL Video Search Engine

## Overview

This project implements a video search engine that allows users to search for specific clips within YouTube playlists (specifically NPTEL lectures) using speech-to-text data and vector embeddings. The system uses RAG (Retrieval Augmented Generation) for intelligent search and retrieval.

## Key Components

### 1. Backend (`backend/`)

#### `main.py`
- FastAPI application with REST endpoints
- Handles playlist processing and video search
- Lazy loading of services for better error handling

#### `youtube_scraper.py`
- Extracts video information from YouTube playlists
- Retrieves transcripts with timestamps using yt-dlp
- Supports automatic and manual captions
- Parses VTT subtitle format

#### `embedding_service.py`
- Creates vector embeddings using sentence-transformers
- Implements chunking strategy with overlap for better context
- Uses `all-MiniLM-L6-v2` model (384 dimensions) by default

#### `pinecone_service.py`
- Manages Pinecone vector database operations
- Handles index creation and vector storage
- Implements semantic search with metadata filtering

#### `rag_service.py`
- Implements RAG-based search functionality
- Converts queries to embeddings and searches Pinecone
- Returns relevant video clips with metadata

#### `config.py`
- Centralized configuration
- Environment variable management
- Model and chunking parameters

### 2. Frontend (`frontend/`)

#### `index.html`
- Main web interface
- Search box and playlist processing UI
- Video player modal with clip timeline

#### `styles.css`
- Modern, responsive design
- Gradient backgrounds and smooth animations
- Mobile-friendly layout

#### `app.js`
- API integration with backend
- YouTube IFrame API integration
- Video player controls and clip navigation
- Timeline visualization

### 3. Utilities

#### `test_setup.py`
- Verifies all dependencies are installed
- Tests environment configuration
- Validates Pinecone connection

#### `test_youtube_scraper.py`
- Tests YouTube transcript extraction
- Validates playlist processing

#### `setup_env.py`
- Creates .env file template
- Guides user through configuration

#### `run_server.py`
- Convenient script to start the FastAPI server

## Architecture Flow

### 1. Playlist Processing
```
YouTube Playlist URL
    ↓
YouTube Scraper (yt-dlp)
    ↓
Extract Videos + Transcripts (with timestamps)
    ↓
Chunk Transcripts (with overlap)
    ↓
Create Embeddings (sentence-transformers)
    ↓
Store in Pinecone (with metadata)
```

### 2. Search Flow
```
User Query
    ↓
Create Query Embedding
    ↓
Search Pinecone (cosine similarity)
    ↓
Retrieve Top-K Clips
    ↓
Return Video Clips with Timestamps
    ↓
Display in Frontend with Video Player
```

## Key Features

### 1. Transcript Extraction
- Uses yt-dlp to extract automatic captions
- Falls back to manual subtitles if available
- Supports multiple languages (prefers English)
- Parses VTT format with precise timestamps

### 2. Vector Embeddings
- Uses sentence-transformers for semantic understanding
- Creates overlapping chunks for context preservation
- Configurable chunk size and overlap
- Supports different embedding models

### 3. RAG Implementation
- Semantic search using vector similarity
- Returns relevant clips (not just videos)
- Includes relevance scores
- Preserves context with overlapping chunks

### 4. Video Player
- YouTube IFrame API integration
- Clip timeline visualization
- Jump-to-clip functionality
- Auto-pause at clip end

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **yt-dlp**: YouTube data extraction
- **sentence-transformers**: Vector embeddings
- **Pinecone**: Vector database
- **Python-dotenv**: Environment management

### Frontend
- **HTML/CSS/JavaScript**: Vanilla web technologies
- **YouTube IFrame API**: Video playback
- **Fetch API**: Backend communication

## Configuration

### Environment Variables
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment/region
- `PINECONE_INDEX_NAME`: Pinecone index name

### Model Configuration
- `EMBEDDING_MODEL`: Embedding model name (default: all-MiniLM-L6-v2)
- `CHUNK_SIZE`: Character count per chunk (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 100)

## Usage Workflow

1. **Setup**: Configure Pinecone and install dependencies
2. **Process Playlist**: Extract and index videos from a YouTube playlist
3. **Search**: Enter queries to find relevant video clips
4. **Watch**: View videos with clip highlights and navigation

## Advantages of RAG Approach

1. **Semantic Understanding**: Finds relevant content even if exact keywords don't match
2. **Context Preservation**: Overlapping chunks maintain context
3. **Scalability**: Pinecone handles large-scale vector search efficiently
4. **Accuracy**: Vector embeddings capture semantic meaning better than keyword search
5. **Flexibility**: Easy to update embeddings or change models

## Future Enhancements

1. **Multi-language Support**: Support for multiple languages in transcripts
2. **Advanced Filtering**: Filter by video, date, duration, etc.
3. **Batch Processing**: Process multiple playlists simultaneously
4. **LLM Integration**: Use LLM for query understanding and result ranking
5. **Export Features**: Export search results and transcripts
6. **User Authentication**: Save searches and preferences
7. **Better Chunking**: Smarter chunking based on semantic boundaries
8. **Video Thumbnails**: Show thumbnail previews in results

## Performance Considerations

1. **Embedding Model**: Lightweight model (384 dims) for fast inference
2. **Chunking**: Balanced chunk size for context vs. granularity
3. **Pinecone**: Serverless vector database for scalability
4. **Caching**: Consider caching embeddings for processed videos
5. **Batch Processing**: Process videos in batches for efficiency

## Security Considerations

1. **API Keys**: Store in .env file (not committed to git)
2. **CORS**: Configured for development (restrict in production)
3. **Input Validation**: Validate playlist URLs and queries
4. **Rate Limiting**: Consider rate limiting for API endpoints

## Testing

1. **Setup Test**: `python test_setup.py`
2. **Scraper Test**: `python test_youtube_scraper.py`
3. **API Test**: Use FastAPI docs at `http://localhost:8000/docs`

## Deployment

### Development
- Run locally with `python run_server.py`
- Open frontend in browser

### Production
- Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
- Serve frontend through web server (Nginx, Apache)
- Configure CORS properly
- Use environment-specific configuration
- Set up monitoring and logging

## Troubleshooting

See [QUICKSTART.md](QUICKSTART.md) for common issues and solutions.

## License

This project is open source and available under the MIT License.

