"""
RAG service for query processing and retrieval
Now uses hybrid search (BM25 + semantic) for better results
"""
from backend.hybrid_search_service import HybridSearchService
from typing import List, Dict


class RAGService:
    def __init__(self):
        self.hybrid_search = HybridSearchService()

    def search_video_clips(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for video clips matching the query using hybrid search (BM25 + semantic)
        """
        # Use hybrid search for better retrieval
        results = self.hybrid_search.search(query, top_k=top_k)
        
        # Format results with clip information (including new metadata)
        clips = []
        for result in results:
            clips.append({
                'video_id': result['video_id'],
                'video_title': result['video_title'],
                'video_url': result['video_url'],
                'clip_start': result['start'],
                'clip_end': result['end'],
                'transcript': result['text'],
                'relevance_score': result['score'],
                'video_description': result.get('video_description', ''),
                'video_duration': result.get('video_duration', 0),
                'view_count': result.get('view_count', 0),
                'channel': result.get('channel', ''),
                'channel_id': result.get('channel_id', ''),
                'thumbnail': result.get('thumbnail', ''),
                'like_count': result.get('like_count', 0),
            })
        
        return clips

    def get_clip_context(self, clip: Dict, context_seconds: float = 5.0) -> Dict:
        """
        Get expanded context around a clip (expand start/end times)
        """
        clip_start = max(0, clip['clip_start'] - context_seconds)
        clip_end = clip['clip_end'] + context_seconds
        
        return {
            **clip,
            'clip_start_expanded': clip_start,
            'clip_end_expanded': clip_end,
        }

