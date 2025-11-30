"""
FastAPI backend for video search engine
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

try:
    # Try absolute imports (when running from parent directory)
    from backend.youtube_scraper import YouTubeScraper
    from backend.embedding_service import EmbeddingService
    from backend.llm_service import LLMService
    from backend.neo4j_service import Neo4jService
    from backend.knowledge_graph_service import KnowledgeGraphService
except ImportError:
    # Fall back to relative imports (when running from backend directory)
    from youtube_scraper import YouTubeScraper
    from embedding_service import EmbeddingService
    from llm_service import LLMService
    from neo4j_service import Neo4jService
    from knowledge_graph_service import KnowledgeGraphService

app = FastAPI(title="NPTEL Video Search Engine")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy loading)
youtube_scraper = None
embedding_service = None
llm_service = None
neo4j_service = None
knowledge_graph_service = None

def get_youtube_scraper():
    global youtube_scraper
    if youtube_scraper is None:
        youtube_scraper = YouTubeScraper()
    return youtube_scraper

def get_embedding_service():
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
    return embedding_service

def get_llm_service():
    global llm_service
    if llm_service is None:
        try:
            llm_service = LLMService()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM service initialization failed: {str(e)}")
    return llm_service

def get_neo4j_service():
    global neo4j_service
    if neo4j_service is None:
        try:
            neo4j_service = Neo4jService()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Neo4j initialization failed: {str(e)}")
    return neo4j_service

def get_knowledge_graph_service():
    global knowledge_graph_service
    if knowledge_graph_service is None:
        try:
            neo4j = get_neo4j_service()
            knowledge_graph_service = KnowledgeGraphService(neo4j.driver)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Knowledge graph service initialization failed: {str(e)}")
    return knowledge_graph_service


# Request/Response models
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5


class PlaylistRequest(BaseModel):
    playlist_url: str


class SearchResponse(BaseModel):
    results: List[dict]
    query: str


@app.get("/")
async def root():
    return {"message": "NPTEL Video Search Engine API (Neo4j + LLM Edition)"}


@app.post("/api/process-playlist")
async def process_playlist(request: PlaylistRequest):
    """
    Process a YouTube playlist:
    1. Extract transcripts
    2. Generate chapters using LLM
    3. Create embeddings for chapters
    4. Store in Neo4j
    """
    try:
        scraper = get_youtube_scraper()
        emb_service = get_embedding_service()
        llm = get_llm_service()
        neo4j = get_neo4j_service()
        
        # Get videos with transcripts
        try:
            videos = scraper.get_playlist_with_transcripts(request.playlist_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        if not videos:
            raise HTTPException(status_code=404, detail="No videos with transcripts found.")
        
        processed_count = 0
        
        for video in videos:
            print(f"Processing video: {video["title"]}")
            
            # Generate chapters using LLM
            chapters = llm.generate_chapters(video["transcript"], video["duration"])
            
            if not chapters:
                print(f"Skipping {video["title"]} - No chapters generated")
                continue
                
            # Create embeddings for chapters (Title + Description)
            texts_to_embed = [f"{c["title"]}: {c["description"]}" for c in chapters]
            embeddings = emb_service.create_embeddings(texts_to_embed)
            
            # Store in Neo4j
            neo4j.add_video_with_chapters(video, chapters, embeddings.tolist())
            processed_count += 1
            
        return {
            "message": "Playlist processed successfully",
            "videos_processed": processed_count,
            "total_videos": len(videos)
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing playlist: {str(e)}")


@app.post("/api/search", response_model=SearchResponse)
async def search_videos(query: SearchQuery):
    """
    Search for video chapters matching the query
    """
    try:
        emb_service = get_embedding_service()
        neo4j = get_neo4j_service()
        
        # Create query embedding
        query_embedding = emb_service.create_embeddings([query.query])[0]
        
        # Search in Neo4j
        results = neo4j.hybrid_search(query.query, query_embedding.tolist(), query.top_k)
        
        return SearchResponse(results=results, query=query.query)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/related/{video_id}")
async def get_related(video_id: str):
    """
    Get related videos based on graph structure
    """
    try:
        neo4j = get_neo4j_service()
        related = neo4j.get_related_videos(video_id)
        return {"related_videos": related}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/knowledge-graph/build")
async def build_knowledge_graph(similarity_threshold: float = 0.7, max_connections: int = 5):
    """
    Build the knowledge graph by creating relationships between chapters.
    This should be run after processing playlists.
    """
    try:
        kg_service = get_knowledge_graph_service()
        kg_service.build_knowledge_graph(similarity_threshold, max_connections)
        stats = kg_service.get_graph_statistics()
        return {
            "message": "Knowledge graph built successfully",
            "statistics": stats
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-graph")
async def get_knowledge_graph(video_id: Optional[str] = None, limit: int = 500, auto_build: bool = True):
    """
    Get the knowledge graph structure for visualization.
    If video_id is provided, returns graph focused on that video.
    Otherwise returns the entire graph (up to limit).

    If auto_build=True (default), automatically builds the graph if it doesn't exist yet.
    """
    try:
        kg_service = get_knowledge_graph_service()
        graph_data = kg_service.get_knowledge_graph(video_id, limit, auto_build)
        return graph_data
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-graph/learning-path/{target_chapter_id}")
async def get_learning_path(target_chapter_id: str, start_chapter_id: Optional[str] = None):
    """
    Get the optimal learning path to reach a target chapter.
    If start_chapter_id is provided, finds path from start to target.
    Otherwise finds all prerequisites for the target.
    """
    try:
        kg_service = get_knowledge_graph_service()
        path = kg_service.get_learning_path(target_chapter_id, start_chapter_id)
        return {
            "target_chapter_id": target_chapter_id,
            "start_chapter_id": start_chapter_id,
            "path": path
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-graph/stats")
async def get_graph_stats():
    """
    Get statistics about the knowledge graph.
    """
    try:
        kg_service = get_knowledge_graph_service()
        stats = kg_service.get_graph_statistics()
        stats['is_built'] = kg_service.is_graph_built()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/knowledge-graph/videos")
async def get_all_videos():
    """
    Get list of all videos for filtering the knowledge graph.
    """
    try:
        kg_service = get_knowledge_graph_service()
        videos = kg_service.get_all_videos()
        return {"videos": videos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

