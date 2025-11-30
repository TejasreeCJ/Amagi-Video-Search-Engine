# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Neo4j AuraDB Account** (free tier available at https://neo4j.com/cloud/platform/aura-graph-database/)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
python setup_env.py
```

This will create a template `.env` file. You need to fill in your API keys.

### 3. Get Database Credentials

#### Neo4j AuraDB (Recommended)
1. Sign up at [Neo4j AuraDB](https://neo4j.com/cloud/platform/aura-graph-database/)
2. Create a new **Free** instance
3. Download the credentials file (contains your password)
4. Copy the **Connection URI** (starts with `neo4j+s://`)
5. Update `.env`:
   - `NEO4J_URI`: Your Connection URI
   - `NEO4J_USER`: `neo4j`
   - `NEO4J_PASSWORD`: The password you saved

### 4. Test Setup

```bash
python test_setup.py
```

This will verify that all dependencies are installed and Neo4j is configured correctly.

### 5. Start the Backend Server

```bash
python run_server.py
```

The server will start on `http://localhost:8000`

### 6. Open the Frontend

Open `frontend/index.html` in your web browser, or serve it using:

```bash
cd frontend
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

## Usage

### Step 1: Process a Playlist

1. Find a YouTube playlist URL (e.g., NPTEL lecture series)
2. Paste the URL in the "Process Playlist" section
3. Click "Process Playlist"
4. Wait for processing to complete (this may take several minutes)

### Step 2: Search for Clips

1. Enter your search query (e.g., "law of conservation of energy")
2. Click "Search"
3. Browse through the results
4. Click on any result to watch the video with the clip highlighted

### Step 3: Watch and Navigate

1. The video player will open with the full video
2. The timeline shows where the relevant clip is located
3. Click "Jump to Clip" to navigate directly to the relevant section
4. The video will automatically pause at the end of the clip

## Example Playlist URLs

- NPTEL Physics: `https://www.youtube.com/playlist?list=PLbMVogVj5nJQ2vsW_hmyvVfO4GYWaaPpO`
- Any YouTube playlist with captions enabled

## Troubleshooting

### Issue: "PINECONE_API_KEY not set"
- Make sure `.env` file exists in the project root
- Verify the API key is correct
- Restart the server after updating `.env`

### Issue: "No transcripts found"
- Ensure the videos have automatic captions enabled
- Some videos may not have English subtitles
- Try a different playlist

### Issue: "Search returns no results"
- Make sure you've processed a playlist first
- Check that the Pinecone index has vectors
- Verify the index name matches in `.env`

### Issue: "YouTube player not loading"
- Check your internet connection
- Ensure YouTube IFrame API is accessible
- Check browser console for errors
- Try a different browser

## Next Steps

- Process multiple playlists to build a larger search index
- Experiment with different search queries
- Customize the embedding model in `backend/config.py`
- Adjust chunk size and overlap for better results

## Advanced Configuration

### Change Embedding Model

Edit `backend/config.py`:

```python
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Better quality, 768 dimensions
```

Note: If you change the model, you'll need to update the Pinecone index dimension accordingly.

### Adjust Chunk Size

Edit `backend/config.py`:

```python
CHUNK_SIZE = 500  # Increase for more context, decrease for more granular clips
CHUNK_OVERLAP = 100  # Increase for better context preservation
```

### Change Pinecone Index

Edit `.env`:

```
PINECONE_INDEX_NAME=your-custom-index-name
```

Make sure the index exists and has the correct dimension (384 for default model).

