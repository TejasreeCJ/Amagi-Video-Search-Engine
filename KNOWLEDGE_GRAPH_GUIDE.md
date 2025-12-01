# Knowledge Graph Feature - User Guide

## Overview

The Knowledge Graph feature provides an **interactive visualization** of the relationships between different chapters across all processed videos. It helps students understand the learning progression and discover optimal pathways through the course material.

## What is the Knowledge Graph?

The knowledge graph is a **network visualization** where:
- **Nodes** represent individual chapters from videos
- **Edges** represent relationships between chapters (similarity, prerequisites, sequential flow)

This creates a map of how different concepts connect to each other, making it easier to:
1. Find prerequisite topics you should learn first
2. Discover related concepts across different videos
3. Understand the overall structure of the course material
4. Navigate through topics in a logical learning sequence

## Key Features

### 1. **Interactive Graph Visualization**
- **Force-Directed Layout**: Nodes naturally cluster based on their relationships
- **Hierarchical Layout**: Shows clear prerequisite relationships from top to bottom
- **Circular Layout**: Displays all nodes in a circular arrangement
- **Zoom & Pan**: Navigate large graphs easily
- **Node Highlighting**: Click nodes to see details and connections

### 2. **Multiple Relationship Types**

The graph creates 4 types of relationships between chapters:

| Relationship | Description | Color | Use Case |
|-------------|-------------|-------|----------|
| **NEXT_TOPIC** | Sequential chapters within the same video | Green | Follow the natural flow of a lecture |
| **SIMILAR_TO** | Chapters with high semantic similarity (>0.85) | Blue | Find alternative explanations of the same concept |
| **RELATES_TO** | Chapters with moderate similarity (0.7-0.85) | Orange | Discover related but distinct concepts |
| **PREREQUISITE_OF** | Earlier foundational concepts | Purple | Identify what to learn first |

### 3. **Learning Path Discovery**
- Select any chapter as your target learning goal
- The system automatically identifies all prerequisite topics
- Highlights the optimal learning sequence
- Shows the shortest path from basics to advanced topics

### 4. **Chapter Information Panel**
- Click any node to view:
  - Full chapter title and description
  - Timeline position in the video
  - All connected chapters
  - Actions: Play video, Show learning path

## How to Use

### Step 1: Process Playlists

Before using the knowledge graph, you need to process at least one YouTube playlist:

1. Go to the **Home** page
2. Enter a YouTube playlist URL
3. Click "Process Playlist"
4. Wait for the system to extract transcripts and generate chapters

### Step 2: Build the Knowledge Graph

After processing playlists:

1. Navigate to **🧠 Knowledge Graph** page
2. Click the **"🔨 Build Knowledge Graph"** button
3. Wait for the system to analyze all chapters and create relationships
4. The graph will automatically load once built

**Parameters:**
- **Similarity Threshold**: 0.7 (default) - Only creates connections between chapters with similarity ≥ 0.7
- **Max Connections**: 5 per chapter - Prevents overcrowding the graph

### Step 3: Explore the Graph

**Basic Navigation:**
- **Click and Drag**: Move nodes around
- **Scroll**: Zoom in/out
- **Click Node**: View chapter details in the info panel
- **Double-Click Node**: Play the video at that chapter (coming soon)

**Change Layout:**
- Use the "Layout" dropdown to switch between:
  - Force Directed (default)
  - Hierarchical
  - Circular

**Filter by Video:**
- Select "By Video" in the "Graph Scope" dropdown
- Choose a specific video to see only its chapters and related content

### Step 4: Find Learning Paths

To find the optimal learning path to a specific topic:

1. Click on the target chapter node
2. In the info panel, click **"🎯 Show Learning Path"**
3. The graph will highlight all prerequisite chapters
4. A popup shows the recommended sequence

## Understanding the Graph

### Node Sizing
- Node size represents importance (how many connections it has)
- Larger nodes are "hub" topics that connect many concepts

### Node Colors
- Colors indicate different topic clusters
- Chapters of similar colors are thematically related

### Edge Thickness
- Thicker edges = stronger similarity between chapters
- Thin edges = weaker but still meaningful connections

## Use Cases

### For Students Learning New Material

**Scenario**: You want to learn about "Newton's Second Law"

1. Search for "Newton's Second Law" in the search page
2. Note the chapter and video
3. Go to Knowledge Graph
4. Click on that chapter node
5. Click "Show Learning Path"
6. The system shows you should first learn:
   - Basic concepts of force
   - Newton's First Law
   - Then Newton's Second Law

### For Review and Exam Prep

**Scenario**: Reviewing for an exam on thermodynamics

1. Go to Knowledge Graph
2. Filter by the thermodynamics video
3. See all topics in the chapter at a glance
4. Click on weak areas to find related explanations in other videos

### For Course Overview

**Scenario**: Understanding the full course structure

1. Load the complete knowledge graph
2. Switch to "Hierarchical" layout
3. See foundational topics at the top
4. Advanced topics at the bottom
5. Understand the natural progression of the course

## Technical Details

### How Relationships Are Created

1. **Semantic Similarity**:
   - Uses 384-dimensional embeddings of chapter content
   - Computes cosine similarity between all chapter pairs
   - Creates relationships above the threshold (default: 0.7)

2. **Sequential Relationships**:
   - Automatically links consecutive chapters within the same video
   - Preserves the natural lecture flow

3. **Prerequisite Detection**:
   - Uses heuristics: earlier chapters with high similarity to later ones
   - Considers temporal ordering within playlists
   - Identifies foundational vs. advanced topics

### Graph Algorithms

- **Layout**: Barnes-Hut force simulation for optimal node positioning
- **Path Finding**: Dijkstra's shortest path algorithm
- **Clustering**: Community detection based on video grouping

## API Endpoints

For developers integrating with the knowledge graph:

### Build Graph
```http
POST /api/knowledge-graph/build?similarity_threshold=0.7&max_connections=5
```

### Get Graph Data
```http
GET /api/knowledge-graph?video_id={optional}&limit=100
```

### Get Learning Path
```http
GET /api/knowledge-graph/learning-path/{target_chapter_id}?start_chapter_id={optional}
```

### Get Statistics
```http
GET /api/knowledge-graph/stats
```

## Troubleshooting

### "No graph data available"
- **Cause**: No playlists have been processed yet
- **Solution**: Go to Home page and process at least one playlist

### "Failed to build knowledge graph"
- **Cause**: Database connection issue or insufficient data
- **Solution**:
  1. Check Neo4j is running
  2. Ensure at least 2+ videos have been processed
  3. Check backend console for errors

### Graph is too crowded
- **Cause**: Too many chapters or low similarity threshold
- **Solutions**:
  1. Increase similarity threshold to 0.75 or 0.8
  2. Reduce max_connections to 3
  3. Filter by specific video
  4. Use hierarchical layout

### Graph loads slowly
- **Cause**: Large number of nodes (100+)
- **Solutions**:
  1. Filter by video
  2. Reduce limit parameter
  3. Use hierarchical layout (no physics simulation)

## Best Practices

1. **Build graph incrementally**: Process a few playlists, build graph, then add more
2. **Experiment with layouts**: Different layouts reveal different insights
3. **Use learning paths**: Don't guess prerequisites - let the system find them
4. **Combine with search**: Use search to find specific topics, then explore graph for context
5. **Regular rebuilds**: Rebuild graph after processing new playlists

## Future Enhancements

Planned features:
- [ ] Video playback integration directly from graph
- [ ] Concept extraction and entity nodes
- [ ] User annotations and custom learning paths
- [ ] Export graph as image/PDF
- [ ] Graph analytics (centrality, clustering coefficients)
- [ ] Collaborative filtering (paths taken by successful students)

## Contributing

To improve the knowledge graph algorithm:

1. Modify `backend/knowledge_graph_service.py`
2. Adjust similarity thresholds, relationship types, or path-finding logic
3. Test with real course data
4. Submit improvements

## Questions?

For issues or feature requests, please check the main README or create an issue in the project repository.
