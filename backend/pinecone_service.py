"""
Pinecone service for vector storage and retrieval
"""
from pinecone import Pinecone, ServerlessSpec
from backend.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_ENVIRONMENT
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

    def upsert_embeddings(self, chunks: List[Dict], embeddings: List[List[float]]):
        """
        Store embeddings in Pinecone with metadata
        Note: Pinecone metadata values must be str, int, float, or bool
        """
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = str(uuid.uuid4())
            # Truncate text if too long (Pinecone has metadata size limits)
            text = chunk['text'][:1000] if len(chunk['text']) > 1000 else chunk['text']
            metadata = {
                'text': text,
                'start': float(chunk['start']),  # Ensure float type
                'end': float(chunk['end']),  # Ensure float type
                'video_id': str(chunk['video_id']),
                'video_title': str(chunk['video_title'])[:500],  # Limit title length
                'video_url': str(chunk['video_url']),
            }
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"Upserted batch {i // batch_size + 1}/{(len(vectors) + batch_size - 1) // batch_size}")
        
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
                'score': match.score,
                'text': match.metadata['text'],
                'start': match.metadata['start'],
                'end': match.metadata['end'],
                'video_id': match.metadata['video_id'],
                'video_title': match.metadata['video_title'],
                'video_url': match.metadata['video_url'],
            })
        
        return results

    def delete_all(self):
        """
        Delete all vectors from index (use with caution)
        """
        self.index.delete(delete_all=True)
        print("All vectors deleted from index")

