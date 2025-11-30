import os
from dotenv import load_dotenv

load_dotenv()

# Model for embeddings - using a good multilingual model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Chunk size for transcript segmentation
CHUNK_SIZE = 500  # characters
CHUNK_OVERLAP = 100  # characters

# YouTube API settings
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

# Whisper settings for transcript generation
WHISPER_ENABLED = os.getenv("WHISPER_ENABLED", "false").lower() == "true"
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "tiny")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")


