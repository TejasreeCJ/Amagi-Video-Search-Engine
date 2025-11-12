"""
Service for creating vector embeddings from transcripts
"""
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
from typing import List, Dict
import numpy as np


class EmbeddingService:
    def __init__(self):
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        print("Embedding model loaded successfully")

    def create_chunks(self, transcript_segments: List[Dict]) -> List[Dict]:
        """
        Create overlapping chunks from transcript segments for better context
        """
        chunks = []
        
        for segment in transcript_segments:
            text = segment['text']
            start = segment['start']
            end = segment['end']
            
            # If segment is short, use it as is
            if len(text) <= CHUNK_SIZE:
                chunks.append({
                    'text': text,
                    'start': start,
                    'end': end,
                    'video_id': segment.get('video_id'),
                    'video_title': segment.get('video_title'),
                    'video_url': segment.get('video_url'),
                })
            else:
                # Split long segments into chunks
                words = text.split()
                current_chunk = []
                current_length = 0
                chunk_start = start
                
                for i, word in enumerate(words):
                    current_chunk.append(word)
                    current_length += len(word) + 1
                    
                    if current_length >= CHUNK_SIZE:
                        chunk_text = ' '.join(current_chunk)
                        # Estimate chunk end time
                        chunk_end = start + (end - start) * (i + 1) / len(words)
                        
                        chunks.append({
                            'text': chunk_text,
                            'start': chunk_start,
                            'end': chunk_end,
                            'video_id': segment.get('video_id'),
                            'video_title': segment.get('video_title'),
                            'video_url': segment.get('video_url'),
                        })
                        
                        # Overlap: keep last few words for context
                        overlap_words = int(CHUNK_OVERLAP / 10)  # Approximate word count
                        current_chunk = current_chunk[-overlap_words:] if overlap_words > 0 else []
                        current_length = sum(len(w) + 1 for w in current_chunk)
                        chunk_start = chunk_end
                
                # Add remaining words
                if current_chunk:
                    chunks.append({
                        'text': ' '.join(current_chunk),
                        'start': chunk_start,
                        'end': end,
                        'video_id': segment.get('video_id'),
                        'video_title': segment.get('video_title'),
                        'video_url': segment.get('video_url'),
                    })
        
        return chunks

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of texts
        """
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings

    def prepare_transcript_for_embedding(self, video_data: Dict) -> List[Dict]:
        """
        Prepare transcript segments with video metadata for embedding
        """
        chunks = []
        for segment in video_data['transcript']:
            segment_with_metadata = {
                **segment,
                'video_id': video_data['video_id'],
                'video_title': video_data['title'],
                'video_url': video_data['url'],
            }
            chunks.append(segment_with_metadata)
        
        # Create overlapping chunks for better context
        return self.create_chunks(chunks)

