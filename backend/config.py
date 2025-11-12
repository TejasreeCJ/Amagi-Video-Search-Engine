import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "nptel-video-search")

# Model for embeddings - using a good multilingual model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunk size for transcript segmentation
CHUNK_SIZE = 500  # characters
CHUNK_OVERLAP = 100  # characters

# Parallel processing settings
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "5"))  # Number of parallel workers for video processing
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))  # Batch size for embedding generation
PINECONE_BATCH_SIZE = int(os.getenv("PINECONE_BATCH_SIZE", "100"))  # Batch size for Pinecone upserts

# Hybrid search settings
BM25_WEIGHT = float(os.getenv("BM25_WEIGHT", "0.4"))  # Weight for BM25 (keyword) search (0.0 to 1.0)
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT", "0.6"))  # Weight for semantic (vector) search (0.0 to 1.0)
BM25_INDEX_PATH = os.getenv("BM25_INDEX_PATH", "data/bm25_index.pkl")  # Path to store BM25 index

# Clip merging settings (for creating meaningful segments)
CLIP_MERGE_THRESHOLD = float(os.getenv("CLIP_MERGE_THRESHOLD", "30.0"))  # Merge clips within N seconds
CLIP_MIN_DURATION = float(os.getenv("CLIP_MIN_DURATION", "10.0"))  # Minimum clip duration (seconds)
CLIP_CONTEXT_BEFORE = float(os.getenv("CLIP_CONTEXT_BEFORE", "5.0"))  # Add N seconds before clip
CLIP_CONTEXT_AFTER = float(os.getenv("CLIP_CONTEXT_AFTER", "5.0"))  # Add N seconds after clip

# YouTube API settings
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

