"""
Hybrid search service combining BM25 (keyword) and semantic (vector) search
Optimized for fast retrieval and accurate ranking
"""
from backend.bm25_service import BM25Service
from backend.pinecone_service import PineconeService
from backend.embedding_service import EmbeddingService
from backend.query_preprocessor import QueryPreprocessor
from backend.clip_merger import ClipMerger
from backend.config import BM25_WEIGHT, SEMANTIC_WEIGHT, BM25_INDEX_PATH
from typing import List, Dict
import numpy as np
from collections import defaultdict


class HybridSearchService:
    def __init__(self, bm25_weight: float = None, semantic_weight: float = None):
        """
        Initialize hybrid search service
        
        Args:
            bm25_weight: Weight for BM25 scores (0.0 to 1.0). If None, uses config value.
            semantic_weight: Weight for semantic scores (0.0 to 1.0). If None, uses config value.
            Note: Weights should sum to 1.0 for best results
        """
        self.bm25_service = BM25Service(index_path=BM25_INDEX_PATH)
        self.pinecone_service = PineconeService()
        self.embedding_service = EmbeddingService()
        self.query_preprocessor = QueryPreprocessor()  # Phase 4: Query preprocessing
        self.clip_merger = ClipMerger()  # Clip merging for meaningful segments
        
        # Use provided weights or config defaults
        bm25_w = bm25_weight if bm25_weight is not None else BM25_WEIGHT
        semantic_w = semantic_weight if semantic_weight is not None else SEMANTIC_WEIGHT
        
        # Normalize weights
        total_weight = bm25_w + semantic_w
        self.bm25_weight = bm25_w / total_weight if total_weight > 0 else 0.5
        self.semantic_weight = semantic_w / total_weight if total_weight > 0 else 0.5
        
        # Configuration for candidate retrieval
        self.candidate_multiplier = 3  # Retrieve 3x more candidates, then merge
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Perform hybrid search combining BM25 and semantic search
        Optimized for speed and accuracy
        
        Args:
            query: Search query string
            top_k: Number of final results to return
            
        Returns:
            List of result dictionaries with combined scores
        """
        if not query or not query.strip():
            return []
        
        # Phase 4: Preprocess query (expand abbreviations, add synonyms)
        preprocessed_query = self.query_preprocessor.preprocess(query)
        
        # Retrieve more candidates from each method for better merging
        candidate_k = max(top_k * self.candidate_multiplier, 20)
        
        # 1. BM25 search (keyword-based) - use preprocessed query
        bm25_results = []
        if self.bm25_service.is_indexed:
            try:
                bm25_results = self.bm25_service.search(preprocessed_query, top_k=candidate_k)
            except Exception as e:
                print(f"Warning: BM25 search failed: {e}")
        
        # 2. Semantic search (vector-based) - use original query for semantic understanding
        semantic_results = []
        try:
            # Use original query for semantic search (embeddings understand context better)
            query_embedding = self.embedding_service.create_embeddings([query])[0]
            semantic_results = self.pinecone_service.search(
                query_embedding=query_embedding.tolist(),
                top_k=candidate_k
            )
        except Exception as e:
            print(f"Warning: Semantic search failed: {e}")
        
        # 3. Merge and re-rank results (use original query for boosting)
        merged_results = self._merge_results(
            bm25_results=bm25_results,
            semantic_results=semantic_results,
            query=query  # Use original query for metadata boosting
        )
        
        # 4. Merge nearby/overlapping clips into meaningful segments
        # Build video durations dict for boundary checking
        video_durations = {}
        for result in merged_results:
            video_id = result.get('video_id', '')
            duration = result.get('video_duration', 0)
            if video_id and duration > 0:
                video_durations[video_id] = duration
        
        # Merge clips to create meaningful segments
        merged_clips = self.clip_merger.merge_clips(merged_results, video_durations)
        
        # 5. Return top_k results
        return merged_clips[:top_k]
    
    def _merge_results(self, bm25_results: List[Dict], semantic_results: List[Dict], query: str) -> List[Dict]:
        """
        Merge BM25 and semantic results with score normalization and combination
        Optimized for fast merging
        
        Args:
            bm25_results: Results from BM25 search
            semantic_results: Results from semantic search
            query: Original query (for potential boosting)
            
        Returns:
            Merged and re-ranked results
        """
        # Create lookup dictionaries for fast access
        # Use a composite key: (video_id, start, end) to identify unique clips
        result_map = {}
        
        # Normalize BM25 scores (0 to 1 range)
        bm25_scores = [r['score'] for r in bm25_results] if bm25_results else []
        if bm25_scores:
            max_bm25 = max(bm25_scores) if bm25_scores else 1.0
            min_bm25 = min(bm25_scores) if bm25_scores else 0.0
            bm25_range = max_bm25 - min_bm25 if max_bm25 > min_bm25 else 1.0
        
        # Process BM25 results
        for result in bm25_results:
            key = self._get_result_key(result)
            normalized_score = (result['score'] - min_bm25) / bm25_range if bm25_range > 0 else 0.0
            
            result_map[key] = {
                **result,
                'bm25_score': normalized_score,
                'semantic_score': 0.0,
                'combined_score': normalized_score * self.bm25_weight,
            }
        
        # Normalize semantic scores (already 0 to 1 for cosine similarity)
        # But we'll ensure they're properly normalized
        semantic_scores = [r['score'] for r in semantic_results] if semantic_results else []
        if semantic_scores:
            max_semantic = max(semantic_scores) if semantic_scores else 1.0
            min_semantic = min(semantic_scores) if semantic_scores else 0.0
            semantic_range = max_semantic - min_semantic if max_semantic > min_semantic else 1.0
        
        # Process semantic results and merge
        for result in semantic_results:
            key = self._get_result_key(result)
            normalized_score = (result['score'] - min_semantic) / semantic_range if semantic_range > 0 else result['score']
            
            if key in result_map:
                # Merge: combine scores
                result_map[key]['semantic_score'] = normalized_score
                result_map[key]['combined_score'] = (
                    result_map[key]['bm25_score'] * self.bm25_weight +
                    normalized_score * self.semantic_weight
                )
                # Update with semantic result data (prefer semantic for metadata)
                result_map[key].update({
                    'text': result.get('text', result_map[key].get('text', '')),
                    'video_id': result.get('video_id', result_map[key].get('video_id', '')),
                    'video_title': result.get('video_title', result_map[key].get('video_title', '')),
                    'video_url': result.get('video_url', result_map[key].get('video_url', '')),
                    'start': result.get('start', result_map[key].get('start', 0.0)),
                    'end': result.get('end', result_map[key].get('end', 0.0)),
                    'video_description': result.get('video_description', result_map[key].get('video_description', '')),
                    'video_duration': result.get('video_duration', result_map[key].get('video_duration', 0)),
                    'view_count': result.get('view_count', result_map[key].get('view_count', 0)),
                    'channel': result.get('channel', result_map[key].get('channel', '')),
                    'channel_id': result.get('channel_id', result_map[key].get('channel_id', '')),
                    'thumbnail': result.get('thumbnail', result_map[key].get('thumbnail', '')),
                    'like_count': result.get('like_count', result_map[key].get('like_count', 0)),
                })
            else:
                # New result from semantic search only
                result_map[key] = {
                    **result,
                    'bm25_score': 0.0,
                    'semantic_score': normalized_score,
                    'combined_score': normalized_score * self.semantic_weight,
                    'video_description': result.get('video_description', ''),
                    'video_duration': result.get('video_duration', 0),
                    'view_count': result.get('view_count', 0),
                    'channel': result.get('channel', ''),
                    'channel_id': result.get('channel_id', ''),
                    'thumbnail': result.get('thumbnail', ''),
                    'like_count': result.get('like_count', 0),
                }
        
        # Apply metadata boosting (Phase 2)
        query_lower = query.lower()
        query_terms = set(self._tokenize(query_lower))
        
        # Calculate max values for normalization
        view_counts = [r.get('view_count', 0) for r in result_map.values() if r.get('view_count', 0) > 0]
        max_views = max(view_counts) if view_counts else 1
        
        for key, result in result_map.items():
            boost = 1.0
            title = result.get('video_title', '').lower()
            description = result.get('video_description', '').lower()
            text = result.get('text', '').lower()
            
            # 1. Title boosting (strongest signal)
            title_matches = sum(1 for term in query_terms if term in title)
            if title_matches > 0:
                boost += 0.20 * title_matches  # 20% boost per matching term
            
            # 2. Description boosting
            desc_matches = sum(1 for term in query_terms if term in description)
            if desc_matches > 0:
                boost += 0.10 * desc_matches  # 10% boost per matching term
            
            # 3. Text start boosting (first 10 words)
            text_words = text.split()[:10]
            text_start = ' '.join(text_words).lower()
            text_matches = sum(1 for term in query_terms if term in text_start)
            if text_matches > 0:
                boost += 0.08 * text_matches  # 8% boost per matching term
            
            # 4. View count boosting (popularity signal)
            view_count = result.get('view_count', 0)
            if view_count > 0:
                # Normalize view count (0 to 1) and apply small boost
                view_normalized = min(view_count / max_views, 1.0)
                boost += 0.05 * view_normalized  # Up to 5% boost for popular videos
            
            result['combined_score'] *= boost
        
        # Convert to list and sort by combined score
        merged_list = list(result_map.values())
        merged_list.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # Rename combined_score to score for consistency
        for result in merged_list:
            result['score'] = result.pop('combined_score')
            # Remove internal scores (optional - keep for debugging)
            # result.pop('bm25_score', None)
            # result.pop('semantic_score', None)
        
        return merged_list
    
    def _get_result_key(self, result: Dict) -> tuple:
        """
        Generate a unique key for a result to identify duplicate clips
        Uses chunk_id if available, otherwise (video_id, start, end)
        """
        chunk_id = result.get('chunk_id')
        if chunk_id:
            return ('chunk_id', str(chunk_id))
        # Fallback to video_id + timestamps
        return (
            str(result.get('video_id', '')),
            round(float(result.get('start', 0.0)), 2),
            round(float(result.get('end', 0.0)), 2)
        )
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for query terms"""
        import re
        return re.findall(r'\b\w+\b', text.lower())

