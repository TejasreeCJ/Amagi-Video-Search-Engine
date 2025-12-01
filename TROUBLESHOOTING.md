# Troubleshooting Guide

## 404 Not Found Errors for Knowledge Graph Endpoints

### Problem
```
INFO: 127.0.0.1:54265 - "POST /api/knowledge-graph/build HTTP/1.1" 404 Not Found
INFO: 127.0.0.1:54820 - "GET /api/knowledge-graph/stats HTTP/1.1" 404 Not Found
INFO: 127.0.0.1:54820 - "GET /api/knowledge-graph?limit=200 HTTP/1.1" 404 Not Found
```

### Solution

The issue is with how the backend server is being started. You need to run it from the **project root directory**, not from the `backend` folder.

#### Option 1: Use the startup script (Recommended)

**For Windows:**
```cmd
start_backend.bat
```

**For Linux/Mac or Windows with Python:**
```bash
python start_backend.py
```

#### Option 2: Run manually from project root

```bash
# Make sure you're in the project root (Hackathon folder)
cd "c:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon"

# Run the server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Option 3: If running from backend folder

If you must run from the backend folder:
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Verify It's Working

1. Open your browser and go to: http://localhost:8000/docs
2. You should see the FastAPI interactive documentation
3. Scroll down and verify you see these endpoints:
   - `POST /api/knowledge-graph/build`
   - `GET /api/knowledge-graph`
   - `GET /api/knowledge-graph/learning-path/{target_chapter_id}`
   - `GET /api/knowledge-graph/stats`

## Auto-Build Feature

### Good News!

The knowledge graph now **auto-builds** when you first load the page. You don't need to manually click "Build Knowledge Graph" anymore!

### How It Works

1. When you open the Knowledge Graph page, it automatically:
   - Checks if relationships exist
   - If not, builds them automatically
   - Then displays the graph

2. The first time might take a minute or two depending on:
   - Number of processed videos
   - Number of chapters
   - Similarity calculations

3. After that, subsequent loads are instant (relationships are stored in Neo4j)

### When to Manually Rebuild

You should manually click "Build Knowledge Graph" when:
- You've processed new playlists
- You want to adjust the similarity threshold
- You want to change max connections per node

## Common Issues

### Issue: "No graph data available"

**Cause:** No playlists have been processed yet

**Solution:**
1. Go to the Home page (index.html)
2. Enter a YouTube playlist URL
3. Click "Process Playlist"
4. Wait for it to complete
5. Then go back to Knowledge Graph page

### Issue: Server won't start - "ModuleNotFoundError"

**Cause:** Running from wrong directory or missing dependencies

**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run from project root
cd "c:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon"
python start_backend.py
```

### Issue: Neo4j connection error

**Cause:** Neo4j database not running

**Solution:**
1. Start Neo4j Desktop or Neo4j service
2. Verify connection details in your `.env` file:
   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   ```

### Issue: "Building..." takes forever

**Cause:** Large number of chapters with complex similarity calculations

**Solutions:**
1. **Increase similarity threshold:** Use 0.75 or 0.8 instead of 0.7
2. **Reduce max connections:** Use 3 instead of 5
3. **Process fewer videos:** Start with 1-2 playlists first

### Issue: Graph is empty after building

**Cause:** Similarity threshold too high or chapters too dissimilar

**Solutions:**
1. Lower the similarity threshold to 0.6 or 0.65
2. Check console logs for errors
3. Verify chapters were created during playlist processing

### Issue: CORS errors in browser console

**Cause:** Frontend and backend on different origins

**Solution:**
- Backend already has CORS enabled for all origins
- Make sure backend is running on port 8000
- Clear browser cache and reload

## Checking Logs

### Backend Logs

When running the server, watch the console output:

**Good signs:**
```
Creating NEXT_TOPIC relationships...
Computing similarities for 50 chapters...
Processed 10/50 chapters...
Knowledge graph built successfully!
```

**Bad signs:**
```
Error: Neo4j connection failed
Error: No chapters found
Traceback...
```

### Frontend Logs

Open browser Developer Tools (F12) and check Console:

**Good signs:**
```
Knowledge Graph page loaded
Loaded graph data: {nodes: [...], edges: [...]}
Graph rendered with 50 nodes and 120 edges
```

**Bad signs:**
```
Error loading knowledge graph: Failed to fetch
404 Not Found
CORS error
```

## Performance Tips

### For Large Datasets (100+ videos)

1. **Use video filtering:**
   - Select "By Video" in Graph Scope
   - View one playlist at a time

2. **Adjust parameters:**
   ```
   similarity_threshold = 0.75  (higher = fewer connections)
   max_connections = 3          (lower = less crowded)
   ```

3. **Use hierarchical layout:**
   - Faster than force-directed
   - No physics simulation
   - Clearer for large graphs

### For Small Datasets (< 20 videos)

1. **Lower threshold for more connections:**
   ```
   similarity_threshold = 0.65
   max_connections = 7
   ```

2. **Use force-directed layout:**
   - More organic clustering
   - Better for exploration

## Database Queries for Debugging

If you have Neo4j Browser open, try these queries:

### Check if chapters exist:
```cypher
MATCH (c:Chapter) RETURN count(c) as total_chapters
```

### Check if relationships exist:
```cypher
MATCH ()-[r:SIMILAR_TO|RELATES_TO|NEXT_TOPIC|PREREQUISITE_OF]->()
RETURN type(r) as relationship_type, count(r) as count
```

### View sample graph:
```cypher
MATCH (c:Chapter)-[r]->(c2:Chapter)
RETURN c, r, c2
LIMIT 25
```

### Check video count:
```cypher
MATCH (v:Video) RETURN count(v) as total_videos
```

## Still Having Issues?

1. **Check all services are running:**
   - [ ] Neo4j database
   - [ ] Backend server (port 8000)
   - [ ] Frontend (open HTML file)

2. **Verify data exists:**
   - [ ] At least 1 playlist processed
   - [ ] Chapters created in Neo4j
   - [ ] Embeddings generated

3. **Check the logs:**
   - [ ] Backend console for errors
   - [ ] Browser console (F12) for frontend errors
   - [ ] Neo4j logs if database issues

4. **Try a fresh start:**
   ```bash
   # Stop all services
   # Clear Neo4j database (optional)
   # Restart Neo4j
   # Restart backend
   # Refresh browser
   ```

## Contact

If none of these solutions work, please provide:
1. Full error message from backend console
2. Browser console logs (F12 → Console tab)
3. Screenshot of the issue
4. What you were trying to do when it failed
