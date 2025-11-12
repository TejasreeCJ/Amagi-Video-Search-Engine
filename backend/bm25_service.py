"""
BM25 service for keyword-based search
Optimized for fast indexing and retrieval
"""
from rank_bm25 import BM25Okapi
from typing import List, Dict, Optional
import pickle
import os
import re
from pathlib import Path
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=UserWarning)  # Suppress rank-bm25 warnings


class BM25Service:
    def __init__(self, index_path: str = "data/bm25_index.pkl"):
        """
        Initialize BM25 service with optional persisted index
        """
        self.index_path = index_path
        self.bm25: Optional[BM25Okapi] = None
        self.chunk_ids: List[str] = []  # Maps index position to chunk ID
        self.chunk_metadata: Dict[str, Dict] = {}  # Stores metadata for each chunk
        self.is_indexed = False
        
        # Create data directory if it doesn't exist
        dir_path = os.path.dirname(index_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Try to load existing index
        self._load_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Fast tokenization optimized for search
        Converts to lowercase and splits on word boundaries
        """
        # Convert to lowercase and extract words
        text = text.lower()
        # Extract words (alphanumeric sequences)
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
    
    def build_index(self, chunks: List[Dict], chunk_ids: List[str]):
        """
        Build BM25 index from chunks
        Optimized for fast indexing
        
        Args:
            chunks: List of chunk dictionaries with 'text' field
            chunk_ids: List of unique IDs for each chunk (should match Pinecone vector IDs or be mappable)
        """
        if not chunks or not chunk_ids:
            raise ValueError("Chunks and chunk_ids cannot be empty")
        
        if len(chunks) != len(chunk_ids):
            raise ValueError("Chunks and chunk_ids must have the same length")
        
        print(f"\nBuilding BM25 index for {len(chunks)} chunks...")
        
        # Tokenize all texts in parallel (optimized)
        tokenized_corpus = []
        for i, chunk in enumerate(chunks):
            # Combine text with title for better keyword matching
            searchable_text = chunk.get('text', '')
            if chunk.get('video_title'):
                searchable_text = f"{chunk.get('video_title')} {searchable_text}"
            
            tokens = self._tokenize(searchable_text)
            tokenized_corpus.append(tokens)
            
            # Store metadata
            self.chunk_metadata[chunk_ids[i]] = {
                'text': chunk.get('text', ''),
                'video_id': chunk.get('video_id', ''),
                'video_title': chunk.get('video_title', ''),
                'video_url': chunk.get('video_url', ''),
                'start': chunk.get('start', 0.0),
                'end': chunk.get('end', 0.0),
                'video_description': chunk.get('video_description', ''),
                'video_duration': chunk.get('video_duration', 0),
                'view_count': chunk.get('view_count', 0),
                'channel': chunk.get('channel', ''),
                'channel_id': chunk.get('channel_id', ''),
                'thumbnail': chunk.get('thumbnail', ''),
                'like_count': chunk.get('like_count', 0),
            }
        
        # Build BM25 index
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.chunk_ids = chunk_ids
        self.is_indexed = True
        
        print(f"BM25 index built successfully")
        
        # Save index to disk
        self._save_index()
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """
        Search using BM25 and return top_k results
        Optimized for fast retrieval
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of result dictionaries with 'chunk_id', 'score', and metadata
        """
        if not self.is_indexed or self.bm25 is None:
            raise ValueError("BM25 index not built. Please build index first.")
        
        if not query or not query.strip():
            return []
        
        # Tokenize query
        query_tokens = self._tokenize(query)
        
        if not query_tokens:
            return []
        
        # Get BM25 scores (optimized - returns scores for all documents)
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top_k indices (using argpartition for efficiency)
        if top_k >= len(scores):
            top_indices = np.argsort(scores)[::-1]
        else:
            # Use argpartition for O(n) instead of O(n log n) for full sort
            top_indices = np.argpartition(scores, -top_k)[-top_k:]
            # Sort only the top_k results
            top_indices = top_indices[np.argsort(scores[top_indices])][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with positive scores
                chunk_id = self.chunk_ids[idx]
                metadata = self.chunk_metadata.get(chunk_id, {})
                results.append({
                    'chunk_id': chunk_id,
                    'score': float(scores[idx]),
                    'text': metadata.get('text', ''),
                    'video_id': metadata.get('video_id', ''),
                    'video_title': metadata.get('video_title', ''),
                    'video_url': metadata.get('video_url', ''),
                    'start': metadata.get('start', 0.0),
                    'end': metadata.get('end', 0.0),
                    'video_description': metadata.get('video_description', ''),
                    'video_duration': metadata.get('video_duration', 0),
                    'view_count': metadata.get('view_count', 0),
                    'channel': metadata.get('channel', ''),
                    'channel_id': metadata.get('channel_id', ''),
                    'thumbnail': metadata.get('thumbnail', ''),
                    'like_count': metadata.get('like_count', 0),
                })
        
        return results
    
    def _save_index(self):
        """Save BM25 index to disk for persistence"""
        try:
            index_data = {
                'bm25': self.bm25,
                'chunk_ids': self.chunk_ids,
                'chunk_metadata': self.chunk_metadata,
            }
            with open(self.index_path, 'wb') as f:
                pickle.dump(index_data, f)
            print(f"BM25 index saved to {self.index_path}")
        except Exception as e:
            print(f"Warning: Could not save BM25 index: {e}")
    
    def _load_index(self):
        """Load BM25 index from disk if it exists"""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'rb') as f:
                    index_data = pickle.load(f)
                self.bm25 = index_data.get('bm25')
                self.chunk_ids = index_data.get('chunk_ids', [])
                self.chunk_metadata = index_data.get('chunk_metadata', {})
                self.is_indexed = self.bm25 is not None
                if self.is_indexed:
                    print(f"BM25 index loaded from {self.index_path} ({len(self.chunk_ids)} chunks)")
            except Exception as e:
                print(f"Warning: Could not load BM25 index: {e}")
                self.is_indexed = False
    
    def clear_index(self):
        """Clear the BM25 index"""
        self.bm25 = None
        self.chunk_ids = []
        self.chunk_metadata = {}
        self.is_indexed = False
        if os.path.exists(self.index_path):
            try:
                os.remove(self.index_path)
                print(f"BM25 index file removed: {self.index_path}")
            except Exception as e:
                print(f"Warning: Could not remove BM25 index file: {e}")

