#!/usr/bin/env python
"""
Start the backend server for the NPTEL Video Search Engine
Run this from the project root directory
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now run uvicorn
import uvicorn

if __name__ == "__main__":
    print("Starting NPTEL Video Search Engine Backend...")
    print(f"Project root: {project_root}")
    print("Server will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop the server\n")

    # Use import string instead of app object for reload to work
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
