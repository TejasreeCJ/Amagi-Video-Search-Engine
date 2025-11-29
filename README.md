# Amagi Video Search Engine (Neo4j + LLM Edition)

A powerful video search engine that allows you to search inside YouTube playlists (like NPTEL lectures) using **Hybrid Search** (Vector Semantic + Keyword) and **LLM-powered Chaptering**.

This project has been migrated from Pinecone to **Neo4j** to leverage Graph relationships and Hybrid Search capabilities.

## 🚀 Features

- **🧠 Hybrid Search**: Combines **Vector Similarity** (80%) and **Keyword Search** (20%) for highly accurate results.
- **🤖 AI Chaptering**: Uses **Google Gemini 2.0** to intelligently segment videos into meaningful chapters with titles and summaries.
- **🕸️ Graph Database**: Stores videos, chapters, and their relationships in **Neo4j**, enabling complex queries and "related video" recommendations.
- **⏱️ Variable Clip Length**: Clips are dynamically sized based on the content topic, not arbitrary fixed chunks.
- **🛡️ Robust Processing**: Handles API rate limits (Gemini) with automatic retries and fallback mechanisms.
- **⚡ Developer Friendly**: Includes PowerShell scripts for one-click startup and shutdown.

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Database**: Neo4j (Graph + Vector Index + Fulltext Index)
- **LLM**: Google Gemini (2.0 Pro / Flash) for content understanding
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (Local, fast, free)
- **Frontend**: Vanilla JS + HTML/CSS (Lightweight)

## 🛠️ Prerequisites

1.  **Python 3.10+** installed.
2.  **Neo4j Database**:
    *   **Option A (Recommended)**: Install [Neo4j Desktop](https://neo4j.com/download/) locally.
    *   **Option B**: Use [Neo4j Aura](https://neo4j.com/cloud/aura/) (Free Cloud Tier).
    *   *Note: Ensure the APOC plugin is enabled if using Desktop (though core features use standard Cypher).*
3.  **Google Gemini API Key**: Get one for free at [Google AI Studio](https://aistudio.google.com/).

## ⚙️ Installation & Setup

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd Amagi-Video-Search-Engine
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file in the root directory (or edit the existing one):
    ```ini
    # Neo4j Configuration
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=your_password

    # Google Gemini API (for Chapter Generation)
    GEMINI_API_KEY=your_gemini_api_key

    # Optional: YouTube API (if using official API instead of scraper)
    YOUTUBE_API_KEY=your_youtube_key
    ```

## ▶️ Running the Application

We provide a PowerShell script to automate the startup process (Windows).

### Option 1: One-Click Run (Recommended)
Run the development script from the parent directory or root:
powershell
.\dev.ps1

This script will:

Kill any existing processes on ports 8000 (Backend) and 3000 (Frontend).
Start the FastAPI Backend.
Start the Frontend Server.
Automatically open your browser to http://localhost:3000.

###Option 2: Manual Run
If you prefer running services separately:

Terminal 1 (Backend):
python run_server.py

Terminal 2 (Frontend):
cd frontend
python -m http.server 3000

Then open http://localhost:3000 in your browser.

📖 Usage Guide
Process a Playlist:

Paste a YouTube Playlist URL (e.g., an NPTEL course).
Click "Process Playlist".
What happens? The backend downloads transcripts, sends them to Gemini to generate chapters, creates embeddings, and stores everything in Neo4j.
Search:

Type a query like "What is the law of conservation of energy?" or "Explain rigid body equilibrium".
The system performs a Hybrid Search (matching meaning + keywords).
Results show the exact video chapter, a summary, and a direct link to the timestamp.
Watch:

Clicking a result opens the video starting 30 seconds before the relevant segment for context.

🔧 Troubleshooting
Neo4j Connection Error: Ensure Neo4j is running and the NEO4J_URI in .env matches your instance (usually bolt://localhost:7687).
Gemini Quota Exceeded: The system has built-in retries. If it fails, it falls back to using raw transcripts. You can try switching models in llm_service.py.
Search Returns 500 Error: Check the backend terminal for the traceback. It usually indicates a database query issue.


