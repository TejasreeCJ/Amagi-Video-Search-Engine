# Knowledge Graph Mind Map Feature

## Overview

This feature creates an **interactive knowledge graph/mind map** from educational YouTube videos. It analyzes video transcripts, identifies topics and concepts, creates logical clip boundaries, and visualizes the content structure as an interactive graph.

## Features

- 🧠 **Automatic Topic Detection**: Uses NLP to identify key topics and concepts in videos
- ✂️ **Intelligent Clip Segmentation**: Creates logical clips based on semantic boundaries
- 🔗 **Relationship Mapping**: Shows both sequential flow and topic-based relationships
- 🎨 **Interactive Visualization**: Explore the knowledge graph with zoom, pan, and click interactions
- 📊 **Hierarchical Structure**: Visualizes Introduction → Main Content → Conclusion
- 🎬 **Direct Video Playback**: Click on any clip to watch that specific segment

## How It Works

### Backend Processing

1. **Transcript Extraction**: Downloads and parses video transcripts with timestamps
2. **Topic Boundary Detection**: Uses semantic similarity to detect topic changes
3. **Clip Creation**: Segments video into logical clips (minimum 30 seconds by default)
4. **Topic Extraction**: Uses TF-IDF to extract key topics from each clip
5. **Graph Construction**: Builds nodes (clips) and edges (relationships) structure

### Frontend Visualization

- **Vis.js Network**: Interactive graph visualization library
- **Color-coded Nodes**: Different colors for Introduction, Main Content, Conclusion
- **Edge Types**:
  - Solid green arrows: Sequential flow (temporal order)
  - Dashed blue arrows: Related topics (semantic similarity)
- **Interactive Controls**: Physics simulation, zoom, pan, reset view

## Usage

### From Main Page

1. Open the main page (`index.html`)
2. Find the "🧠 Knowledge Graph Mind Map" section
3. Enter a YouTube video URL (must have captions/transcripts)
4. Click "Generate Mind Map"
5. Wait for processing (typically 10-30 seconds)
6. Explore the interactive graph!

### Direct Access

Open `knowledge-graph.html` directly and enter a video URL.

### Graph Interactions

- **Click on a node**: View clip details in the side panel
- **Double-click a node**: Play the video clip in a modal
- **Drag nodes**: Rearrange the graph layout
- **Mouse wheel**: Zoom in/out
- **Click and drag canvas**: Pan around the graph
- **Reset View button**: Fit all nodes in view
- **Physics toggle**: Enable/disable automatic node positioning
- **Export button**: Save graph as PNG image

## API Endpoint

### POST `/api/generate-knowledge-graph`

**Request Body:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "min_clip_duration": 30.0
}
```

**Response:**
```json
{
  "nodes": [
    {
      "id": "clip_0",
      "label": "Introduction to Physics",
      "clip_id": 0,
      "start_time": 0.0,
      "end_time": 45.5,
      "duration": 45.5,
      "topics": ["physics", "introduction", "mechanics"],
      "text": "Welcome to this lecture on physics...",
      "level": 0
    }
  ],
  "edges": [
    {
      "from": "clip_0",
      "to": "clip_1",
      "type": "sequential",
      "label": "continues to",
      "strength": 1.0
    }
  ],
  "clips": [...],
  "video_info": {
    "video_id": "VIDEO_ID",
    "title": "Video Title",
    "duration": 3600,
    "thumbnail": "https://img.youtube.com/vi/VIDEO_ID/maxresdefault.jpg"
  }
}
```

## Technical Architecture

### Backend (`backend/knowledge_graph_service.py`)

- **KnowledgeGraphService**: Main service class
  - `generate_knowledge_graph()`: Entry point for graph generation
  - `_create_logical_clips()`: Segments transcript into clips
  - `_detect_topic_boundaries()`: Uses embedding similarity to find topic changes
  - `_extract_topics_from_clips()`: TF-IDF based topic extraction
  - `_build_knowledge_graph()`: Constructs graph structure with nodes and edges

### Frontend

- **knowledge-graph.html**: Main visualization page
- **knowledge-graph.js**: Graph generation and interaction logic
- **graph-styles.css**: Styling for the graph interface

### Libraries Used

- **Backend**:
  - `sentence-transformers`: Semantic embeddings for boundary detection
  - `scikit-learn`: TF-IDF vectorization and cosine similarity
  - `networkx`: Graph data structures (optional, for future extensions)
  - `nltk`: Text processing utilities

- **Frontend**:
  - **Vis.js Network**: Graph visualization
  - **YouTube IFrame API**: Video playback

## Configuration

### Minimum Clip Duration

Adjust in the UI or API call (default: 30 seconds)
```json
{
  "min_clip_duration": 45.0
}
```

### Topic Boundary Threshold

In `knowledge_graph_service.py`, line ~118:
```python
if similarity < 0.7:  # Lower = more sensitive to topic changes
    boundaries[i] = True
```

### Topic Similarity Threshold

In `knowledge_graph_service.py`, line ~240:
```python
if similarity > 0.3:  # Higher = fewer cross-references
    edges.append(...)
```

## Limitations

1. **Requires Transcripts**: Videos must have captions/subtitles enabled
2. **Processing Time**: Longer videos take more time to process
3. **Topic Detection Accuracy**: Depends on transcript quality and content structure
4. **Language**: Currently optimized for English content

## Future Enhancements

- Multi-language support
- Custom topic modeling (e.g., LDA, BERT topics)
- Playlist-level knowledge graphs (multiple videos)
- Export to various formats (JSON, GraphML, etc.)
- Collaborative annotations on nodes
- AI-powered summaries for each clip
- Search within the knowledge graph

## Examples

### Good Video Types

- ✅ Educational lectures (NPTEL, Khan Academy, etc.)
- ✅ Tutorial series with clear sections
- ✅ Conference talks with distinct topics
- ✅ Documentaries with chaptered content

### Less Suitable Videos

- ❌ Music videos
- ❌ Vlogs without structure
- ❌ Videos without transcripts
- ❌ Live streams with chaotic content

## Troubleshooting

**Graph not generating?**
- Ensure video has captions/transcripts
- Check browser console for errors
- Verify backend server is running

**Clips too short/long?**
- Adjust `min_clip_duration` parameter
- Modify topic boundary threshold in code

**Graph too cluttered?**
- Increase topic similarity threshold
- Use physics simulation to spread nodes
- Zoom and pan to focus on specific areas

## License

Same as the main project.
