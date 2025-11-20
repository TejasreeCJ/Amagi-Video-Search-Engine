# 🔧 Troubleshooting: Video Playback Issues

## Problem: "www.youtube.com's server IP address could not be found"

This error occurs when trying to play videos in the knowledge graph. Here are the solutions:

---

## ✅ **Solution 1: Use a Local Web Server (RECOMMENDED)**

YouTube's embedded player requires the page to be served via HTTP/HTTPS, not opened directly as a file.

### Option A: Python HTTP Server (Easiest)

```powershell
# Navigate to frontend folder
cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon\frontend"

# Start a simple HTTP server
python -m http.server 8080
```

Then open in your browser:
```
http://localhost:8080/knowledge-graph.html
```

### Option B: Use Live Server Extension (VS Code)

1. Install "Live Server" extension in VS Code
2. Right-click on `knowledge-graph.html`
3. Select "Open with Live Server"

### Option C: Node.js HTTP Server

```powershell
# Install http-server globally (one time)
npm install -g http-server

# Navigate to frontend folder
cd frontend

# Start server
http-server -p 8080
```

Then open: `http://localhost:8080/knowledge-graph.html`

---

## ✅ **Solution 2: Open Videos on YouTube Directly**

The code has been updated to automatically detect if you're running from `file://` protocol and will offer to open clips directly on YouTube.

**How it works:**
1. Click on a clip or double-click a node
2. You'll see a confirmation dialog
3. Click "OK" to open the video on YouTube at the correct timestamp
4. The video will play in a new tab

**Advantages:**
- Works without web server
- No CORS issues
- Full YouTube features available

**Disadvantages:**
- Opens in new tab instead of embedded player
- Less seamless experience

---

## ✅ **Solution 3: Serve Through Backend Server**

You can also serve the frontend through the FastAPI backend:

### Step 1: Modify backend to serve static files

Add this to `backend/main.py`:

```python
from fastapi.staticfiles import StaticFiles

# After app initialization
app.mount("/static", StaticFiles(directory="frontend"), name="static")
```

### Step 2: Access via backend URL

```
http://localhost:8000/static/knowledge-graph.html
```

---

## 🎯 **Quick Fix Comparison**

| Solution | Ease | Video Quality | Notes |
|----------|------|---------------|-------|
| Python HTTP Server | ⭐⭐⭐⭐⭐ | Embedded | Best for development |
| VS Code Live Server | ⭐⭐⭐⭐⭐ | Embedded | If using VS Code |
| Open on YouTube | ⭐⭐⭐ | Full YT | No server needed |
| FastAPI Static | ⭐⭐⭐ | Embedded | All in one server |

---

## 📝 **Step-by-Step: Recommended Setup**

### For Windows (Your Setup)

1. **Open PowerShell in the frontend folder:**
   ```powershell
   cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon\frontend"
   ```

2. **Start Python HTTP server:**
   ```powershell
   python -m http.server 8080
   ```

3. **Keep this terminal open** (don't close it)

4. **Open your browser and go to:**
   ```
   http://localhost:8080/knowledge-graph.html
   ```

5. **Now videos will play!** 🎉

---

## 🚀 **Complete Workflow**

### Terminal 1: Backend Server
```powershell
cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon"
& ".venv\Scripts\python.exe" run_server.py
```
Leave this running on port 8000

### Terminal 2: Frontend Server
```powershell
cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon\frontend"
python -m http.server 8080
```
Leave this running on port 8080

### Access the Application
- Main page: `http://localhost:8080/index.html`
- Knowledge Graph: `http://localhost:8080/knowledge-graph.html`

---

## ❓ **Why Does This Happen?**

### Technical Explanation

1. **CORS (Cross-Origin Resource Sharing)**
   - YouTube's IFrame API has security restrictions
   - It won't load content from `file://` protocol
   - Requires HTTP/HTTPS protocol

2. **Same-Origin Policy**
   - Browsers block certain API features on file:// URLs
   - YouTube API needs proper domain context

3. **CSP (Content Security Policy)**
   - YouTube enforces strict security policies
   - Embedded players need valid HTTP origins

---

## 🔍 **Verify It's Working**

After setting up the HTTP server:

1. ✅ Notice at top should disappear (if served via HTTP)
2. ✅ Click on a node in the graph
3. ✅ Double-click to play
4. ✅ Video modal should appear with working player
5. ✅ Video should start at the correct timestamp

---

## 🆘 **Still Having Issues?**

### Check Browser Console
Press `F12` → Console tab → Look for errors

### Common Additional Issues:

**Problem:** "Mixed Content" error
- **Solution:** Ensure both backend and frontend use same protocol (both HTTP)

**Problem:** Port already in use
- **Solution:** Change port: `python -m http.server 8081`

**Problem:** Cannot access localhost
- **Solution:** Check Windows Firewall settings

**Problem:** Backend not responding
- **Solution:** Verify backend server is running on port 8000

---

## 💡 **Pro Tips**

### 1. Use Different Ports
- Backend: 8000
- Frontend: 8080
- This avoids conflicts

### 2. Bookmark URLs
- Main: `http://localhost:8080/index.html`
- Graph: `http://localhost:8080/knowledge-graph.html`

### 3. Keep Terminals Open
- Don't close the terminal windows
- Minimize them instead

### 4. Production Deployment
For production, use:
- Nginx or Apache for static files
- Reverse proxy for backend
- Proper SSL certificates

---

## 🎉 **Success Checklist**

- [ ] Backend server running (port 8000)
- [ ] Frontend served via HTTP server (port 8080)
- [ ] Access via `http://localhost:8080`
- [ ] Knowledge graph loads
- [ ] Clicking nodes shows details
- [ ] Double-clicking plays video
- [ ] Video player appears and works

Once all checked, you're good to go! 🚀

---

## 📞 **Quick Reference Commands**

```powershell
# Start backend
cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon"
& ".venv\Scripts\python.exe" run_server.py

# Start frontend (new terminal)
cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon\frontend"
python -m http.server 8080

# Access
# Browser: http://localhost:8080/index.html
```

---

**Now you're ready to explore knowledge graphs with working video playback!** 🎬✨
