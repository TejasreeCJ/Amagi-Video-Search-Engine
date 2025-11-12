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

# YouTube API settings
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

