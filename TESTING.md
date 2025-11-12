# Testing Guide

## Quick Test Steps

### 1. Start the Backend Server

Open a terminal and run:

```bash
python run_server.py
```

The server should start on `http://localhost:8000`

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Open the Frontend

Open `frontend/index.html` in your web browser. You can:
- Double-click the file to open it in your default browser
- Or serve it using a simple HTTP server:
  ```bash
  cd frontend
  python -m http.server 8080
  ```
  Then open `http://localhost:8080` in your browser

### 3. Test Playlist Processing

1. Find a YouTube playlist URL (preferably one with English captions)
2. Paste it in the "Process Playlist" section
3. Click "Process Playlist"
4. Wait for processing to complete (this may take several minutes depending on playlist size)

**Example Playlist URLs:**
- NPTEL Physics: `https://www.youtube.com/playlist?list=PLbMVogVj5nJQ2vsW_hmyvVfO4GYWaaPpO`
- Any playlist with captions enabled

### 4. Test Search Functionality

1. Enter a search query in the search box (e.g., "law of conservation of energy")
2. Click "Search"
3. Browse through the results
4. Click on any result to watch the video with the clip highlighted

## Testing with API (Programmatic)

You can also test using the example script:

```bash
python example_usage.py
```

Or use curl/Postman to test the API endpoints:

### Test Health Endpoint
```bash
curl http://localhost:8000/api/health
```

### Test Search Endpoint
```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "law of conservation of energy", "top_k": 5}'
```

### Test Playlist Processing
```bash
curl -X POST http://localhost:8000/api/process-playlist \
  -H "Content-Type: application/json" \
  -d '{"playlist_url": "YOUR_PLAYLIST_URL"}'
```

## API Documentation

Once the server is running, you can access interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Common Issues

### Server won't start
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check that `.env` file exists and has correct Pinecone credentials

### No search results
- Make sure you've processed a playlist first
- Verify that the playlist videos have captions/subtitles
- Check that embeddings were successfully stored in Pinecone

### Frontend can't connect to backend
- Verify the backend server is running
- Check that `API_BASE_URL` in `frontend/app.js` matches your server URL
- Check browser console for CORS errors

### Videos have no transcripts
- Not all YouTube videos have automatic captions
- Try a different playlist
- Check if the video has English subtitles available

## Expected Behavior

### Playlist Processing
- Should show progress in the backend console
- Should extract video information and transcripts
- Should create embeddings and store them in Pinecone
- Should return success message with number of videos and chunks processed

### Search
- Should return relevant video clips (not just videos)
- Each result should have:
  - Video title
  - Clip start and end times
  - Transcript text
  - Relevance score
  - Video URL

### Video Player
- Should load YouTube video
- Should show clip timeline
- Should allow jumping to clip start time
- Should auto-pause at clip end

## Performance Notes

- First playlist processing may take time (downloading transcripts, creating embeddings)
- Embedding model loads on first use (takes ~10-30 seconds)
- Search is fast once embeddings are stored
- Large playlists (100+ videos) may take 30+ minutes to process

## Next Steps

1. Process a small playlist first (5-10 videos) to test
2. Try different search queries
3. Test with different types of content
4. Experiment with chunk size and overlap settings in `backend/config.py`

