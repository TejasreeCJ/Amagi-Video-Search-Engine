# 🧠 Knowledge Graph Mind Map Feature - Implementation Summary

## What We Built

We've successfully implemented an **Interactive Knowledge Graph/Mind Map** feature for the Amagi Video Search Engine. This feature transforms educational YouTube videos into visual, interactive mind maps that show the logical flow and relationships between different topics and concepts.

## ✨ Key Features

### 1. **Intelligent Video Analysis**
   - Automatically downloads and processes video transcripts
   - Detects topic boundaries using semantic similarity
   - Creates logical clips with meaningful duration
   - Extracts key topics from each clip using TF-IDF

### 2. **Interactive Visualization**
   - Beautiful, interactive graph using Vis.js
   - Color-coded nodes by section (Introduction, Main Content, Conclusion)
   - Two types of connections:
     - **Sequential edges** (green solid): Temporal flow
     - **Related edges** (blue dashed): Topic similarity
   - Click nodes to see details
   - Double-click to play video clips
   - Physics simulation for automatic layout
   - Export graph as image

### 3. **User-Friendly Interface**
   - Simple input: Just paste a YouTube video URL
   - Adjustable minimum clip duration
   - Side panel with video information and controls
   - Detailed clip information on click
   - Integrated video player for watching clips

## 📁 Files Created/Modified

### Backend Files
1. **`backend/knowledge_graph_service.py`** (NEW)
   - Main service for graph generation
   - Topic detection and clip segmentation
   - Graph structure building

2. **`backend/main.py`** (MODIFIED)
   - Added `/api/generate-knowledge-graph` endpoint
   - Integrated KnowledgeGraphService

### Frontend Files
3. **`frontend/knowledge-graph.html`** (NEW)
   - Interactive graph visualization page
   - Sidebar controls and video info
   - Modal for video playback

4. **`frontend/knowledge-graph.js`** (NEW)
   - Graph generation logic
   - Vis.js network configuration
   - User interaction handlers

5. **`frontend/graph-styles.css`** (NEW)
   - Complete styling for knowledge graph page
   - Responsive design
   - Animations and transitions

6. **`frontend/index.html`** (MODIFIED)
   - Added "Knowledge Graph Mind Map" section
   - Input for video URL and launch button

7. **`frontend/app.js`** (MODIFIED)
   - Added `openKnowledgeGraph()` function
   - Event handlers for new section

8. **`frontend/styles.css`** (MODIFIED)
   - Styling for knowledge graph section on main page

### Documentation & Testing
9. **`KNOWLEDGE_GRAPH_README.md`** (NEW)
   - Comprehensive feature documentation
   - Usage instructions
   - API documentation
   - Troubleshooting guide

10. **`test_knowledge_graph.py`** (NEW)
    - Test script for the feature
    - Verifies functionality
    - Shows sample output

11. **`requirements.txt`** (MODIFIED)
    - Added: spacy, networkx, scikit-learn, nltk

## 🔧 Technical Implementation

### Backend Algorithm

```
1. Extract Video Transcript
   ↓
2. Detect Topic Boundaries
   - Calculate embeddings for each segment
   - Compare similarity between windows
   - Mark low-similarity points as boundaries
   ↓
3. Create Logical Clips
   - Group segments based on boundaries
   - Ensure minimum duration
   - Extract clip text and metadata
   ↓
4. Extract Topics
   - Apply TF-IDF vectorization
   - Get top keywords per clip
   ↓
5. Build Graph Structure
   - Create nodes (clips with metadata)
   - Create edges (sequential + related)
   - Calculate hierarchical levels
   ↓
6. Return Graph Data (JSON)
```

### Frontend Rendering

```
1. User Enters Video URL
   ↓
2. Send Request to Backend API
   ↓
3. Receive Graph Data
   ↓
4. Initialize Vis.js Network
   - Configure nodes (color, size, labels)
   - Configure edges (type, color, arrows)
   - Set up hierarchical layout
   ↓
5. Render Interactive Graph
   ↓
6. Handle User Interactions
   - Click: Show clip details
   - Double-click: Play video
   - Drag: Rearrange layout
   - Controls: Reset, physics, export
```

## 🎯 How to Use

### For Users

1. **Start the backend server:**
   ```powershell
   & "C:/Users/Karthik Sagar P/OneDrive/Desktop/COLLEGE/amagi/Hackathon/.venv/Scripts/python.exe" run_server.py
   ```

2. **Open the frontend:**
   - Open `frontend/index.html` in your browser

3. **Generate a knowledge graph:**
   - Scroll to "🧠 Knowledge Graph Mind Map" section
   - Paste a YouTube video URL (must have captions)
   - Click "Generate Mind Map"
   - Wait for processing (10-30 seconds)
   - Explore the interactive graph!

### For Developers

**Test the feature:**
```powershell
& "C:/Users/Karthik Sagar P/OneDrive/Desktop/COLLEGE/amagi/Hackathon/.venv/Scripts/python.exe" test_knowledge_graph.py
```

**API Usage:**
```bash
POST http://localhost:8000/api/generate-knowledge-graph
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "min_clip_duration": 30.0
}
```

## 🎨 Visual Design

### Color Scheme
- **Introduction clips**: Red/Pink (#FF6B6B)
- **Main content clips**: Teal (#4ECDC4)
- **Conclusion clips**: Light Teal (#95E1D3)
- **Sequential edges**: Green (#4CAF50)
- **Related edges**: Blue (#2196F3)

### Layout
- Hierarchical layout (left to right)
- Automatic physics-based positioning
- Responsive design for different screen sizes

## 📊 Example Output

For a typical educational video:
- **15-30 clips** created from a 30-minute video
- **14-29 sequential edges** (clip connections)
- **5-15 related edges** (topic cross-references)
- **3 hierarchical levels** (Introduction, Main, Conclusion)

## 🚀 Benefits

1. **Better Content Understanding**: Visual overview of video structure
2. **Faster Navigation**: Jump directly to relevant sections
3. **Topic Discovery**: See related concepts across the video
4. **Study Aid**: Great for reviewing educational content
5. **Content Creation**: Helps educators see content flow

## 🔮 Future Enhancements

Potential improvements (mentioned in README):
- Multi-language support
- Playlist-level graphs (multiple videos)
- Custom topic modeling
- Collaborative annotations
- AI-powered summaries
- Search within graph
- Different visualization styles

## ✅ Current Status

**All features implemented and working!**

- ✅ Backend service created
- ✅ API endpoint added
- ✅ Frontend visualization complete
- ✅ Integration with main UI done
- ✅ Styling and UX polished
- ✅ Documentation written
- ✅ Test script created

## 🎉 Success!

You now have a fully functional **Interactive Knowledge Graph Mind Map** feature integrated into your Amagi Video Search Engine. The feature provides a unique way to visualize and navigate educational video content, making it easier to understand the structure and flow of complex topics.

**Next Steps:**
1. Test with various educational videos
2. Gather user feedback
3. Fine-tune parameters (clip duration, topic thresholds)
4. Consider implementing some of the future enhancements
5. Share your awesome project! 🚀
