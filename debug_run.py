import uvicorn
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        print("Starting uvicorn...")
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=False, # Disable reload for debugging
            log_level="debug"
        )
    except Exception as e:
        print(f"Error running uvicorn: {e}")
