# How to Test the Application

## Simple Method (Recommended)

### Step 1: Start the Backend Server

Open a terminal/command prompt and run:

```bash
python run_server.py
```

Wait until you see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Keep this terminal window open** - the server needs to keep running.

### Step 2: Open the Frontend

Since port 8080 is already in use on your system, simply open the HTML file directly:

1. Navigate to the `frontend` folder in Windows Explorer
2. Double-click on `index.html`
3. It should open in your default web browser

**OR** use a different port:

```bash
cd frontend
python -m http.server 3000
```

Then open `http://localhost:3000` in your browser.

### Step 3: Test the Application

1. **First, process a playlist:**
   - The playlist section might be hidden. If you don't see it, we can enable it.
   - Enter a YouTube playlist URL
   - Click "Process Playlist"
   - Wait for it to complete (this takes time)

2. **Then search:**
   - Enter a search query
   - Click "Search"
   - View results and click on them to watch videos

## Alternative: Use API Documentation

If you want to test the API directly:

1. Start the server: `python run_server.py`
2. Open your browser and go to: `http://localhost:8000/docs`
3. This shows an interactive API documentation where you can test endpoints

## Troubleshooting

### Frontend shows "Cannot connect to API"
- Make sure the backend server is running on port 8000
- Check the browser console (F12) for errors
- Verify `API_BASE_URL` in `frontend/app.js` is `http://localhost:8000`

### Port 8080 already in use
- Just open `index.html` directly (double-click it)
- Or use a different port: `python -m http.server 3000`

### CORS errors
- The backend has CORS enabled, but if you open the HTML file directly (file:// protocol), some browsers might block it
- Solution: Use a local server on a different port, or open from `http://localhost:3000`

