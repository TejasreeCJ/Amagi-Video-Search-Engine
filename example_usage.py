"""
Example script showing how to use the video search engine programmatically
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def process_playlist(playlist_url: str):
    """Process a YouTube playlist and store embeddings"""
    print(f"Processing playlist: {playlist_url}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/process-playlist",
        json={"playlist_url": playlist_url}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Successfully processed playlist")
        print(f"  Videos processed: {result['videos_processed']}")
        print(f"  Chunks created: {result['chunks_created']}")
        return result
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.text}")
        return None

def search_videos(query: str, top_k: int = 5):
    """Search for video clips matching a query"""
    print(f"\nSearching for: '{query}'")
    
    response = requests.post(
        f"{API_BASE_URL}/api/search",
        json={"query": query, "top_k": top_k}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Found {len(result['clips'])} clips")
        
        for i, clip in enumerate(result['clips'], 1):
            print(f"\n  Clip {i}:")
            print(f"    Video: {clip['video_title']}")
            print(f"    Time: {clip['clip_start']:.1f}s - {clip['clip_end']:.1f}s")
            print(f"    Relevance: {clip['relevance_score']:.3f}")
            print(f"    Transcript: {clip['transcript'][:100]}...")
            print(f"    URL: {clip['video_url']}")
        
        return result
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"  {response.text}")
        return None

def health_check():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health")
        if response.status_code == 200:
            print("✓ API is healthy")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running.")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Video Search Engine - Example Usage")
    print("=" * 50)
    
    # Check if API is running
    if not health_check():
        print("\nPlease start the server first:")
        print("  python run_server.py")
        exit(1)
    
    # Example 1: Process a playlist
    print("\n" + "=" * 50)
    print("Example 1: Process a Playlist")
    print("=" * 50)
    
    playlist_url = input("\nEnter a YouTube playlist URL (or press Enter to skip): ").strip()
    if playlist_url:
        process_playlist(playlist_url)
    
    # Example 2: Search for clips
    print("\n" + "=" * 50)
    print("Example 2: Search for Video Clips")
    print("=" * 50)
    
    query = input("\nEnter a search query (or press Enter to use default): ").strip()
    if not query:
        query = "law of conservation of energy"
    
    search_videos(query)
    
    print("\n" + "=" * 50)
    print("Example complete!")
    print("=" * 50)

