"""
Pinecone service for vector storage and retrieval
"""
from pinecone import Pinecone, ServerlessSpec
from backend.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_ENVIRONMENT, PINECONE_BATCH_SIZE
from typing import List, Dict, Optional
import uuid


class PineconeService:
    def __init__(self):
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not set in environment variables")
        
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index_name = PINECONE_INDEX_NAME
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """
        Create index if it doesn't exist
        """
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index: {self.index_name}")
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # Dimension for all-MiniLM-L6-v2 model
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region=PINECONE_ENVIRONMENT
                    )
                )
                print(f"Index {self.index_name} created successfully")
            except Exception as e:
                print(f"Error creating index: {e}")
                raise
        else:
            print(f"Index {self.index_name} already exists")
        
        self.index = self.pc.Index(self.index_name)
        print(f"Connected to index: {self.index_name}")

    def upsert_embeddings(self, chunks: List[Dict], embeddings: List[List[float]], chunk_ids: List[str] = None):
        """
        Store embeddings in Pinecone with metadata
        Note: Pinecone metadata values must be str, int, float, or bool
        
        Args:
            chunks: List of chunk dictionaries
            embeddings: List of embedding vectors
            chunk_ids: Optional list of chunk IDs. If not provided, UUIDs will be generated.
                      If provided, must match length of chunks.
        """
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Use provided chunk_id or generate UUID
            if chunk_ids and i < len(chunk_ids):
                vector_id = str(chunk_ids[i])
            else:
                vector_id = str(uuid.uuid4())
            
            # Truncate text if too long (Pinecone has metadata size limits)
            text = chunk['text'][:1000] if len(chunk['text']) > 1000 else chunk['text']
            description = str(chunk.get('video_description', ''))[:500]  # Limit description length
            
            metadata = {
                'text': text,
                'start': float(chunk['start']),  # Ensure float type
                'end': float(chunk['end']),  # Ensure float type
                'video_id': str(chunk['video_id']),
                'video_title': str(chunk['video_title'])[:500],  # Limit title length
                'video_url': str(chunk['video_url']),
                'video_description': description,
                'video_duration': float(chunk.get('video_duration', 0)),
                'view_count': int(chunk.get('view_count', 0)),
                'channel': str(chunk.get('channel', ''))[:200],
                'channel_id': str(chunk.get('channel_id', '')),
                'thumbnail': str(chunk.get('thumbnail', '')),
                'like_count': int(chunk.get('like_count', 0)),
            }
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })
        
        # Upsert in batches
        for i in range(0, len(vectors), PINECONE_BATCH_SIZE):
            batch = vectors[i:i + PINECONE_BATCH_SIZE]
            self.index.upsert(vectors=batch)
            batch_num = i // PINECONE_BATCH_SIZE + 1
            total_batches = (len(vectors) + PINECONE_BATCH_SIZE - 1) // PINECONE_BATCH_SIZE
            print(f"  Upserted batch {batch_num}/{total_batches} ({len(batch)} vectors)")
        
        print(f"Successfully upserted {len(vectors)} vectors")

    def search(self, query_embedding: List[float], top_k: int = 5, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar vectors in Pinecone
        """
        query_response = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter_dict
        )
        
        results = []
        for match in query_response.matches:
            results.append({
                'chunk_id': match.id,  # Vector ID (which is the chunk_id we set)
                'score': match.score,
                'text': match.metadata['text'],
                'start': match.metadata['start'],
                'end': match.metadata['end'],
                'video_id': match.metadata['video_id'],
                'video_title': match.metadata['video_title'],
                'video_url': match.metadata['video_url'],
                'video_description': match.metadata.get('video_description', ''),
                'video_duration': match.metadata.get('video_duration', 0),
                'view_count': match.metadata.get('view_count', 0),
                'channel': match.metadata.get('channel', ''),
                'channel_id': match.metadata.get('channel_id', ''),
                'thumbnail': match.metadata.get('thumbnail', ''),
                'like_count': match.metadata.get('like_count', 0),
            })
        
        return results

    def delete_all(self):
        """
        Delete all vectors from index (use with caution)
        """
        self.index.delete(delete_all=True)
        print("All vectors deleted from index")

