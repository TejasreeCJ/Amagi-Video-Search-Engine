"""
FastAPI backend for video search engine
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from backend.youtube_scraper import YouTubeScraper
from backend.embedding_service import EmbeddingService
from backend.pinecone_service import PineconeService
from backend.rag_service import RAGService
from backend.knowledge_graph_service import KnowledgeGraphService
from backend.whisper_service import get_whisper_service

app = FastAPI(title="NPTEL Video Search Engine")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy loading to handle missing credentials)
youtube_scraper = None
embedding_service = None
pinecone_service = None
rag_service = None
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

def get_pinecone_service():
    global pinecone_service
    if pinecone_service is None:
        try:
            pinecone_service = PineconeService()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pinecone initialization failed: {str(e)}")
    return pinecone_service

def get_rag_service():
    global rag_service
    if rag_service is None:
        try:
            rag_service = RAGService()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RAG service initialization failed: {str(e)}")
    return rag_service


def get_knowledge_graph_service():
    global knowledge_graph_service
    if knowledge_graph_service is None:
        try:
            knowledge_graph_service = KnowledgeGraphService()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Knowledge graph service initialization failed: {str(e)}")
    return knowledge_graph_service


# Request/Response models
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5


class PlaylistRequest(BaseModel):
    playlist_url: str


class VideoRequest(BaseModel):
    video_url: str
    min_clip_duration: Optional[float] = 30.0


class SearchResponse(BaseModel):
    clips: List[dict]
    query: str


@app.get("/")
async def root():
    return {"message": "NPTEL Video Search Engine API"}


@app.post("/api/process-playlist")
async def process_playlist(request: PlaylistRequest):
    """
    Process a YouTube playlist and store embeddings in Pinecone
    """
    try:
        scraper = get_youtube_scraper()
        emb_service = get_embedding_service()
        pc_service = get_pinecone_service()
        
        # Get videos with transcripts
        try:
            videos = scraper.get_playlist_with_transcripts(request.playlist_url)
        except Exception as e:
            error_msg = str(e)
            raise HTTPException(
                status_code=400, 
                detail=error_msg if error_msg else "Failed to extract playlist. Please check the playlist URL and ensure it's public."
            )
        
        if not videos:
            # Get playlist info for better error message
            try:
                scraper_temp = get_youtube_scraper()
                all_videos = scraper_temp.get_playlist_videos(request.playlist_url)
                video_count = len(all_videos) if all_videos else 0
                
                if video_count > 0:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"No videos with transcripts found in playlist.\n\n"
                               f"Found {video_count} video(s) in playlist, but none have captions/subtitles available.\n\n"
                               "SOLUTIONS:\n"
                               "1. Enable Whisper AI transcript generation (see docs/WHISPER_SETUP_GUIDE.md)\n"
                               "2. The videos don't have automatic captions enabled\n"
                               "3. Try a different playlist with videos that have captions\n"
                               "4. Enable automatic captions in YouTube Studio for these videos\n"
                               "5. Try an NPTEL playlist (they usually have captions)\n\n"
                               "Run this to check which videos have transcripts:\n"
                               "python check_playlist_transcripts.py \"YOUR_PLAYLIST_URL\""
                    )
                else:
                    raise HTTPException(
                        status_code=404, 
                        detail="No videos found in playlist. Please ensure:\n"
                               "1. The playlist is public or unlisted\n"
                               "2. The playlist URL is correct\n"
                               "3. The playlist contains videos"
                    )
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(
                    status_code=404, 
                    detail="No videos with transcripts found in playlist. Please ensure:\n"
                           "1. The playlist is public or unlisted\n"
                           "2. Videos have automatic captions or subtitles enabled\n"
                           "3. The playlist URL is correct"
                )
        
        # Process each video
        all_chunks = []
        for video in videos:
            chunks = emb_service.prepare_transcript_for_embedding(video)
            all_chunks.extend(chunks)
        
        if not all_chunks:
            raise HTTPException(
                status_code=404,
                detail="No transcript chunks created. Videos might not have sufficient transcript data."
            )
        
        # Create embeddings
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = emb_service.create_embeddings(texts)
        
        # Store in Pinecone
        pc_service.upsert_embeddings(all_chunks, embeddings.tolist())
        
        return {
            "message": "Playlist processed successfully",
            "videos_processed": len(videos),
            "chunks_created": len(all_chunks)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing playlist: {str(e)}")


@app.post("/api/search", response_model=SearchResponse)
async def search_videos(query: SearchQuery):
    """
    Search for video clips matching the query
    """
    try:
        rag = get_rag_service()
        clips = rag.search_video_clips(query.query, query.top_k)
        return SearchResponse(clips=clips, query=query.query)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


@app.post("/api/generate-knowledge-graph")
async def generate_knowledge_graph(request: VideoRequest):
    """
    Generate an interactive knowledge graph from a video's transcript
    """
    try:
        kg_service = get_knowledge_graph_service()
        graph_data = kg_service.generate_knowledge_graph(
            request.video_url, 
            request.min_clip_duration
        )
        return graph_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating knowledge graph: {str(e)}")


@app.get("/api/whisper-metrics")
async def get_whisper_metrics():
    """
    Get Whisper accuracy metrics and performance statistics
    """
    try:
        whisper_service = get_whisper_service()
        if whisper_service:
            metrics = whisper_service.get_accuracy_metrics()
            return metrics
        else:
            return {
                "error": "Whisper service not available",
                "total_videos_processed": 0,
                "successful_generations": 0,
                "failed_generations": 0,
                "success_rate": 0.0,
                "average_processing_time": 0.0,
                "total_audio_duration_processed": 0.0,
                "average_processing_time_per_minute": 0.0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving Whisper metrics: {str(e)}")


@app.post("/api/reset-whisper-metrics")
async def reset_whisper_metrics():
    """
    Reset Whisper accuracy metrics
    """
    try:
        whisper_service = get_whisper_service()
        if whisper_service:
            whisper_service.reset_metrics()
            return {"message": "Whisper metrics reset successfully"}
        else:
            raise HTTPException(status_code=503, detail="Whisper service not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting Whisper metrics: {str(e)}")


@app.post("/api/generate-transcript")
async def generate_transcript(request: VideoRequest):
    """
    Generate transcript for a single video using Whisper
    """
    try:
        whisper_service = get_whisper_service()
        if not whisper_service:
            raise HTTPException(status_code=503, detail="Whisper service not available")
        
        result = whisper_service.generate_transcript_for_video(request.video_url)
        
        if result:
            return result
        else:
            raise HTTPException(status_code=404, detail="Failed to generate transcript")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating transcript: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

