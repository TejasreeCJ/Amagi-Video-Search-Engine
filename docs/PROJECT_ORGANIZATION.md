# 📋 Project Organization Guide

## New Folder Structure

The project has been reorganized into a clean, professional structure for better maintainability.

## 📁 Directory Overview

### Root Level
```
Amagi-Video-Search-Engine/
├── backend/           # All backend Python code
├── frontend/          # All frontend HTML/CSS/JS
├── docs/             # All documentation files
├── tests/            # All test scripts
├── scripts/          # Utility scripts
├── .env              # Environment configuration
├── .gitignore        # Git ignore rules
├── requirements.txt  # Python dependencies
├── run_server.py    # Main server entry point
└── README.md        # Main project README
```

---

## 🗂️ Detailed Breakdown

### 📂 `backend/` - Backend Services
**Purpose:** All Python backend code and services

**Files:**
- `config.py` - Configuration management
- `embedding_service.py` - Text embedding generation
- `knowledge_graph_service.py` - Knowledge graph generation (NEW)
- `main.py` - FastAPI application & API endpoints
- `pinecone_service.py` - Vector database operations
- `rag_service.py` - RAG-based search logic
- `youtube_scraper.py` - YouTube video/transcript extraction

**What it does:**
- Provides REST API endpoints
- Handles video processing
- Manages vector embeddings
- Performs semantic search

---

### 📂 `frontend/` - Web Interface
**Purpose:** User-facing web application

**Files:**
- `index.html` - Main search page
- `knowledge-graph.html` - Knowledge graph visualization (NEW)
- `app.js` - Main application logic
- `knowledge-graph.js` - Graph interaction code (NEW)
- `styles.css` - Main styling
- `graph-styles.css` - Graph-specific styles (NEW)

**What it does:**
- Provides web interface for search
- Displays video search results
- Visualizes knowledge graphs
- Handles video playback

---

### 📂 `docs/` - Documentation
**Purpose:** All project documentation and guides

**Files:**
- `START_HERE.md` - First-time user guide ⭐ START HERE
- `QUICKSTART.md` - Detailed setup instructions
- `QUICKSTART_KNOWLEDGE_GRAPH.md` - Knowledge graph quick start
- `KNOWLEDGE_GRAPH_README.md` - Complete knowledge graph docs
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `VIDEO_PLAYBACK_FIX.md` - Troubleshooting video issues
- `HOW_TO_TEST.md` - Testing guidelines
- `TESTING.md` - Testing strategies
- `PROJECT_SUMMARY.md` - Project overview
- `SOLUTIONS_NO_TRANSCRIPTS.md` - Handling videos without transcripts
- `DEBUG_PLAYLIST.md` - Debugging playlist issues
- `TEST_STEPS.txt` - Manual testing steps

**Navigation Guide:**
1. **New users?** → Read `START_HERE.md`
2. **Setting up?** → Read `QUICKSTART.md`
3. **Using knowledge graph?** → Read `KNOWLEDGE_GRAPH_README.md`
4. **Video playback issues?** → Read `VIDEO_PLAYBACK_FIX.md`
5. **Technical details?** → Read `IMPLEMENTATION_SUMMARY.md`

---

### 📂 `tests/` - Test Scripts
**Purpose:** All testing and verification scripts

**Files:**
- `test_setup.py` - Verify installation & configuration
- `test_knowledge_graph.py` - Test knowledge graph feature
- `test_playlist_url.py` - Test playlist processing
- `test_video_transcript.py` - Test transcript extraction
- `test_youtube_scraper.py` - Test YouTube scraper
- `check_playlist_transcripts.py` - Check which videos have transcripts

**How to run:**
```bash
# Test overall setup
python tests/test_setup.py

# Test knowledge graph
python tests/test_knowledge_graph.py

# Test playlist
python tests/test_playlist_url.py
```

---

### 📂 `scripts/` - Utility Scripts
**Purpose:** Helper scripts for setup and running

**Files:**
- `start_servers.bat` - One-click server startup (Windows) ⭐
- `setup_env.py` - Environment setup wizard
- `example_usage.py` - API usage examples

**How to use:**
```bash
# Windows: Double-click to start both servers
start_servers.bat

# Setup environment
python scripts/setup_env.py

# See API examples
python scripts/example_usage.py
```

---

## 🎯 Quick Access Guide

### "I want to..."

**...start the application**
→ Double-click `scripts/start_servers.bat` (Windows)
→ Or see `docs/START_HERE.md`

**...understand the project**
→ Read `README.md` in root
→ Then `docs/PROJECT_SUMMARY.md`

**...set up from scratch**
→ Follow `docs/QUICKSTART.md`

**...use knowledge graphs**
→ Read `docs/KNOWLEDGE_GRAPH_README.md`
→ Quick start: `docs/QUICKSTART_KNOWLEDGE_GRAPH.md`

**...fix video playback**
→ Read `docs/VIDEO_PLAYBACK_FIX.md`

**...run tests**
→ Check `docs/HOW_TO_TEST.md`
→ Run scripts in `tests/` folder

**...modify the backend**
→ Edit files in `backend/` folder
→ Main API: `backend/main.py`

**...modify the frontend**
→ Edit files in `frontend/` folder
→ Main page: `frontend/index.html`

---

## 📊 File Count Summary

- **Backend files:** 7 Python modules
- **Frontend files:** 6 web files
- **Documentation:** 12 markdown files
- **Tests:** 6 test scripts
- **Scripts:** 3 utility scripts

**Total organized files:** 34 files
**Total folders:** 5 folders

---

## 🔄 Migration Notes

### What Changed?

**Before:**
```
All files mixed in root directory (messy!)
```

**After:**
```
Clean separation:
- Code → backend/ & frontend/
- Docs → docs/
- Tests → tests/
- Scripts → scripts/
```

### Updated References

All documentation has been updated to reflect new paths:
- `test_setup.py` → `tests/test_setup.py`
- `setup_env.py` → `scripts/setup_env.py`
- `QUICKSTART.md` → `docs/QUICKSTART.md`
- etc.

### Backward Compatibility

The main entry points remain the same:
- ✅ `run_server.py` (still in root)
- ✅ `requirements.txt` (still in root)
- ✅ `.env` (still in root)
- ✅ `README.md` (still in root)

---

## 🎨 Benefits of New Structure

### ✅ Better Organization
- Clear separation of concerns
- Easy to find files
- Professional structure

### ✅ Easier Navigation
- Know where everything is
- Logical grouping
- Consistent naming

### ✅ Better Collaboration
- Standard project layout
- Easy onboarding for new developers
- Clear documentation hierarchy

### ✅ Maintainability
- Easier to update
- Better version control
- Scalable structure

---

## 🚀 Next Steps

1. **Familiarize yourself** with the new structure
2. **Update bookmarks** if you had any
3. **Use the quick scripts** in `scripts/`
4. **Check documentation** in `docs/` folder

---

## 💡 Tips

- **Always start with** `docs/START_HERE.md` for new users
- **Use** `scripts/start_servers.bat` for quick startup
- **Keep** `.env` file secure (contains API keys)
- **Run tests** from `tests/` folder before deploying
- **Update docs** when adding new features

---

**Your project is now professionally organized! 🎉**
