
from sentence_transformers import SentenceTransformer
print("Import successful")
try:
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    import traceback
    traceback.print_exc()
