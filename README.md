# Amagi Video Search Engine

A powerful web application to search for specific video clips in YouTube playlists using AI-powered speech-to-text, semantic search, and Knowledge Graphs.

## 🚀 Features

- 🔍 **Intelligent Search**: Search for specific topics, concepts, or questions within video content.
- 🧠 **Knowledge Graph**: Uses **Neo4j** to store video chapters and their relationships, enabling semantic understanding.
- 🤖 **AI-Powered Chapters**: Automatically generates structured chapters with titles and summaries using **Google Gemini**.
- 🎙️ **Whisper Integration**: Automatically generates transcripts for videos without subtitles using **OpenAI Whisper**.
- 📊 **Vector Search**: Uses **Neo4j Vector Index** for fast and accurate semantic retrieval.
- 📹 **Precise Clip Retrieval**: Jump directly to the exact moment a topic is discussed.

## 🏗️ Architecture

### Backend
- **FastAPI**: High-performance REST API.
- **Neo4j AuraDB**: Cloud-native Graph Database (stores both graph structure and vector embeddings).
- **Google Gemini**: LLM for chapter generation and summarization.
- **OpenAI Whisper**: Fallback speech-to-text engine for videos without captions.
- **Sentence Transformers**: Generates embeddings for semantic search.
- **yt-dlp**: Robust YouTube media extraction tool.

### Frontend
- **HTML/CSS/JavaScript**: Clean, responsive interface.
- **YouTube IFrame API**: Embedded player with precise timestamp control.

## 🛠️ Quick Start

### Prerequisites
1. **Python 3.8+**
2. **Neo4j AuraDB Account** (Free tier available at [Neo4j Aura](https://neo4j.com/cloud/platform/aura-graph-database/))
3. **Google Gemini API Key** (Get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone -b whisper-and-chapter-generation https://github.com/TejasreeCJ/Amagi-Video-Search-Engine.git
   cd Amagi-Video-Search-Engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   Run the setup script to create your `.env` file:
   ```bash
   python setup_env.py
   ```
   Then edit the `.env` file with your credentials:
   - `NEO4J_URI`: Your AuraDB connection URI (e.g., `neo4j+s://...`)
   - `NEO4J_PASSWORD`: Your database password
   - `GEMINI_API_KEY`: Your Google Gemini API key

4. **Test Connection**
   Verify everything is set up correctly:
   ```bash
   python test_setup.py
   ```

5. **Run the Server**
   ```bash
   python run_server.py
   ```

6. **Use the App**
   Open `frontend/index.html` in your browser.

## 💡 Usage

1. **Process a Playlist**: Paste a YouTube playlist URL. The system will:
   - Download or generate transcripts (using Whisper if needed).
   - Use Gemini to segment videos into logical chapters.
   - Generate embeddings and store them in Neo4j.
2. **Search**: Type a query like "explain quantum entanglement".
3. **Watch**: Click a result to jump to that exact moment in the video.

## 🔧 Configuration Options

You can tweak settings in `.env`:
- `WHISPER_ENABLED=true`: Enable/disable automatic transcription.
- `WHISPER_MODEL_SIZE=tiny`: Choose model size (`tiny`, `base`, `small`, `medium`, `large`).
