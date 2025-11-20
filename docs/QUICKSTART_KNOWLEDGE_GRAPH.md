# 🚀 Quick Start Guide - Knowledge Graph Feature

## Getting Started in 3 Steps

### Step 1: Ensure Backend is Running

```powershell
# Navigate to project folder (if not already there)
cd "C:\Users\Karthik Sagar P\OneDrive\Desktop\COLLEGE\amagi\Hackathon"

# Start the backend server
& "C:/Users/Karthik Sagar P/OneDrive/Desktop/COLLEGE/amagi/Hackathon/.venv/Scripts/python.exe" run_server.py
```

The server should start on `http://localhost:8000`

### Step 2: Open the Frontend

Open `frontend/index.html` in your web browser, or serve it:

```powershell
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080`

### Step 3: Generate Your First Knowledge Graph

1. Find a YouTube video with captions (educational videos work best)
   - Example: NPTEL lectures, Khan Academy, TED-Ed, etc.

2. In the main page, scroll to the **"🧠 Knowledge Graph Mind Map"** section

3. Paste the video URL

4. Click **"Generate Mind Map"**

5. Wait 10-30 seconds for processing

6. Explore your interactive knowledge graph!

## Example Videos to Try

Here are some good educational videos with captions:

1. **Short Tutorial** (5-10 min):
   - Any Khan Academy video
   - TED-Ed animations
   - Short lecture clips

2. **Full Lecture** (30-60 min):
   - NPTEL courses
   - MIT OpenCourseWare
   - Stanford lectures

## What You Can Do in the Graph

### Basic Interactions
- **Click a node**: See clip details in the sidebar
- **Double-click a node**: Play that video clip
- **Drag nodes**: Rearrange the graph
- **Mouse wheel**: Zoom in/out
- **Drag background**: Pan around

### Controls
- **Reset View**: Fit all nodes in view
- **Toggle Physics**: Enable/disable automatic layout
- **Export as Image**: Save the graph as PNG

### Understanding the Graph

**Node Colors:**
- 🔴 Red/Pink: Introduction section
- 🟦 Teal: Main content section
- 🟩 Light Teal: Conclusion section

**Edge Types:**
- **Solid green arrows** →: Sequential flow (this clip comes after that one)
- **Dashed blue arrows** ⤍: Related topics (these clips discuss similar concepts)

## Troubleshooting

### "Could not extract transcript from video"
**Solution:** The video doesn't have captions. Try:
- A different video with captions enabled
- NPTEL videos (they always have captions)
- Educational channels that provide subtitles

### Graph looks too cluttered
**Solutions:**
- Increase the minimum clip duration (30s → 60s)
- Use the zoom controls to focus on specific areas
- Toggle physics to let nodes spread out

### Processing takes too long
**Normal:** 10-30 seconds for most videos
**If longer:** Video might be very long or have issues
- Try a shorter video first
- Check browser console for errors

### Backend not responding
**Solutions:**
- Make sure the server is running (`python run_server.py`)
- Check that port 8000 is not blocked
- Look at the server terminal for error messages

## API Reference

If you want to call the API directly:

```bash
# Generate knowledge graph
POST http://localhost:8000/api/generate-knowledge-graph

# Request body:
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "min_clip_duration": 30.0
}

# Response: Graph data with nodes, edges, and video info
```

## Tips for Best Results

### ✅ DO:
- Use educational/tutorial videos
- Choose videos with clear topic sections
- Try videos 10-60 minutes long
- Use videos with good quality transcripts

### ❌ DON'T:
- Use music videos or entertainment content
- Use very short videos (<5 minutes)
- Use videos without captions
- Use vlogs or unstructured content

## Advanced Usage

### Adjust Minimum Clip Duration
- **Default**: 30 seconds
- **Shorter clips** (20s): More nodes, more detailed
- **Longer clips** (60s): Fewer nodes, higher level overview

### Direct Access to Knowledge Graph Page
Open `frontend/knowledge-graph.html` directly to skip the main page.

## Support & Documentation

- **Full Feature Documentation**: See `KNOWLEDGE_GRAPH_README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Main Project README**: See `README.md`

## Have Fun! 🎉

Explore the knowledge structure of educational videos in a whole new way. Perfect for:
- 📚 Studying and reviewing lectures
- 🎓 Understanding course structure
- 🔍 Finding specific topics quickly
- 📊 Visualizing content flow
- 🧠 Better comprehension of complex subjects

Happy learning! 🚀
