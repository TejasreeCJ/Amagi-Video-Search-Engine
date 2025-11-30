"""
FastAPI backend for video search engine
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from backend.youtube_scraper import YouTubeScraper
from backend.embedding_service import EmbeddingService
from backend.llm_service import LLMService
from backend.neo4j_service import Neo4jService
from backend.whisper_service import get_whisper_service
from backend.config import WHISPER_ENABLED

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
    1. Extract transcripts (fallback to Whisper if unavailable)
    2. Generate chapters using LLM
    3. Create embeddings for chapters
    4. Store in Neo4j
    """
    try:
        scraper = get_youtube_scraper()
        emb_service = get_embedding_service()
        llm = get_llm_service()
        neo4j = get_neo4j_service()
       
        # Get videos (assuming scraper returns all videos, with 'transcript' as None if unavailable)
        # If scraper only returns videos with transcripts, modify scraper to return all videos
        try:
            videos = scraper.get_playlist_videos(request.playlist_url)  # Note: May need to adjust scraper method name to get all videos
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
       
        if not videos:
            raise HTTPException(status_code=404, detail="No videos found in playlist.")
       
        processed_count = 0
        whisper_fallback_count = 0
       
        for video in videos:
            print(f"Processing video: {video["title"]}")
           
            # Ensure video has required keys; fallback to Whisper if no transcript
            if "transcript" not in video or not video["transcript"]:
                if WHISPER_ENABLED:
                    print(f"🔄 No transcript available, falling back to Whisper for {video['title']}")
                    whisper_service = get_whisper_service()
                    if whisper_service:
                        try:
                            whisper_result = whisper_service.generate_transcript_for_video(video["url"], video.get("id"))
                            if whisper_result and whisper_result["transcript"]:
                                video["transcript"] = whisper_result["transcript"]
                                video["duration"] = whisper_result["duration"]
                                video["title"] = whisper_result["title"]  # Update with extracted title if better
                                video["description"] = whisper_result["description"]
                                whisper_fallback_count += 1
                                print(f"✅ Whisper fallback successful for {video['title']}")
                            else:
                                print(f"❌ Whisper fallback failed for {video['title']}")
                                continue  # Skip if Whisper also fails
                        except Exception as whisper_e:
                            print(f"❌ Whisper error for {video['title']}: {whisper_e}")
                            continue  # Skip on Whisper error
                    else:
                        print("❌ Whisper service unavailable")
                        continue
                else:
                    print(f"⏭️ Skipping {video['title']} - No transcript and Whisper disabled")
                    continue
           
            # Now proceed with transcript (either original or Whisper-generated)
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
            "total_videos": len(videos),
            "whisper_fallbacks": whisper_fallback_count
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)