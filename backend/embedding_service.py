"""
Service for creating vector embeddings from transcripts
"""
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_BATCH_SIZE
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

    def create_embeddings(self, texts: List[str], batch_size: int = None) -> np.ndarray:
        """
        Create embeddings for a list of texts
        Processes in batches to optimize memory usage and speed
        """
        if not texts:
            return np.array([])
        
        if batch_size is None:
            batch_size = EMBEDDING_BATCH_SIZE
        
        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1
            print(f"  Creating embeddings: batch {batch_num}/{total_batches} ({len(batch)} texts)")
            batch_embeddings = self.model.encode(batch, show_progress_bar=False, convert_to_numpy=True)
            all_embeddings.append(batch_embeddings)
        
        return np.vstack(all_embeddings)

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
                'video_description': video_data.get('description', ''),
                'video_duration': video_data.get('duration', 0),
                'view_count': video_data.get('view_count', 0),
                'channel': video_data.get('channel', ''),
                'channel_id': video_data.get('channel_id', ''),
                'thumbnail': video_data.get('thumbnail', ''),
                'like_count': video_data.get('like_count', 0),
            }
            chunks.append(segment_with_metadata)
        
        # Create overlapping chunks for better context
        return self.create_chunks(chunks)

