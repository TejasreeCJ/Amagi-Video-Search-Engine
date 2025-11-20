"""
Test script for YouTube scraper
"""
from backend.youtube_scraper import YouTubeScraper

def test_single_video():
    """Test transcript extraction from a single video"""
    scraper = YouTubeScraper()
    
    # Test with a video that should have captions
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with your test video
    
    print("Testing single video transcript extraction...")
    print(f"Video URL: {test_url}")
    
    video_data = scraper.get_video_transcript(test_url)
    
    if video_data:
        print(f"\n✓ Successfully extracted transcript")
        print(f"Video ID: {video_data['video_id']}")
        print(f"Title: {video_data['title']}")
        print(f"Duration: {video_data['duration']} seconds")
        print(f"Transcript segments: {len(video_data['transcript'])}")
        
        if video_data['transcript']:
            print(f"\nFirst 3 segments:")
            for i, segment in enumerate(video_data['transcript'][:3]):
                print(f"  {i+1}. [{segment['start']:.2f}s - {segment['end']:.2f}s] {segment['text'][:100]}...")
        else:
            print("\n✗ No transcript segments found")
    else:
        print("\n✗ Failed to extract transcript")

def test_playlist():
    """Test playlist extraction"""
    scraper = YouTubeScraper()
    
    # Test with a playlist
    test_playlist = input("Enter YouTube playlist URL (or press Enter to skip): ").strip()
    
    if not test_playlist:
        print("Skipping playlist test")
        return
    
    print(f"\nTesting playlist extraction...")
    print(f"Playlist URL: {test_playlist}")
    
    videos = scraper.get_playlist_videos(test_playlist)
    
    if videos:
        print(f"\n✓ Found {len(videos)} videos in playlist")
        print(f"\nFirst 5 videos:")
        for i, video in enumerate(videos[:5]):
            print(f"  {i+1}. {video['title']}")
            print(f"     URL: {video['url']}")
    else:
        print("\n✗ No videos found in playlist")

if __name__ == "__main__":
    print("=" * 50)
    print("YouTube Scraper Test")
    print("=" * 50)
    
    print("\n1. Testing single video...")
    test_url = input("Enter a YouTube video URL (or press Enter to use default): ").strip()
    if test_url:
        scraper = YouTubeScraper()
        video_data = scraper.get_video_transcript(test_url)
        if video_data:
            print(f"\n✓ Successfully extracted transcript from: {video_data['title']}")
            print(f"  Segments: {len(video_data['transcript'])}")
        else:
            print("\n✗ Failed to extract transcript")
    
    print("\n2. Testing playlist extraction...")
    test_playlist()

