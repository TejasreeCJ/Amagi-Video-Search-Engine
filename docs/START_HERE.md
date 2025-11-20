# 🚀 SUPER QUICK START - Knowledge Graph

## The Easiest Way to Run This Project

### ⚡ One-Click Start (Windows)

Just **double-click** this file:
```
start_servers.bat
```

That's it! 🎉

The script will:
1. ✅ Start the backend server (port 8000)
2. ✅ Start the frontend server (port 8080)
3. ✅ Open the app in your browser automatically

---

## 🎯 What You'll See

Two terminal windows will open:
- **Backend Server** (black window) - Keep this open
- **Frontend Server** (black window) - Keep this open

Your browser will open to: `http://localhost:8080/index.html`

---

## 🎬 How to Use Knowledge Graph

1. **Scroll to the pink section**: "🧠 Knowledge Graph Mind Map"

2. **Paste a YouTube video URL** (must have captions)
   - Example: Any NPTEL lecture, Khan Academy video, etc.

3. **Click "Generate Mind Map"**

4. **Wait 10-30 seconds** for processing

5. **Explore the graph!**
   - Click nodes: See clip details
   - Double-click nodes: Play video clip
   - Drag: Rearrange layout
   - Mouse wheel: Zoom
   - Drag background: Pan

---

## 🛑 When You're Done

Close both terminal windows (Backend Server & Frontend Server)

---

## 📝 Manual Start (If batch file doesn't work)

### Terminal 1: Start Backend
```powershell
cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon"
& ".venv\Scripts\python.exe" run_server.py
```

### Terminal 2: Start Frontend  
```powershell
cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon\frontend"
python -m http.server 8080
```

### Then Open Browser
```
http://localhost:8080/index.html
```

---

## ❓ Troubleshooting

**Videos not playing?**
- Make sure you're accessing via `http://localhost:8080` (not file://)
- See `VIDEO_PLAYBACK_FIX.md` for detailed solutions

**Port already in use?**
- Close other programs using ports 8000 or 8080
- Or change the ports in the batch file

**Backend error?**
- Make sure virtual environment is activated
- Check if all packages are installed

---

## 📚 More Documentation

- `VIDEO_PLAYBACK_FIX.md` - Fix video playback issues
- `KNOWLEDGE_GRAPH_README.md` - Full feature documentation
- `QUICKSTART_KNOWLEDGE_GRAPH.md` - Detailed usage guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details

---

**Happy exploring! 🎓✨**
