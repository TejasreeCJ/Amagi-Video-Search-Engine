"""
Test script to check if a specific video has transcripts
"""
import sys
from backend.youtube_scraper import YouTubeScraper

def test_video_transcript(video_url):
    """Test if a video has transcripts available"""
    print("=" * 60)
    print("Testing Video Transcript Extraction")
    print("=" * 60)
    print(f"Video URL: {video_url}\n")
    
    scraper = YouTubeScraper()
    video_data = scraper.get_video_transcript(video_url)
    
    if video_data:
        print(f"✓ Video Title: {video_data['title']}")
        print(f"✓ Video ID: {video_data['video_id']}")
        print(f"✓ Duration: {video_data['duration']} seconds")
        
        if video_data['transcript']:
            print(f"✓ Transcript found: {len(video_data['transcript'])} segments")
            print(f"\nFirst 3 transcript segments:")
            for i, segment in enumerate(video_data['transcript'][:3], 1):
                print(f"  {i}. [{segment['start']:.1f}s - {segment['end']:.1f}s] {segment['text'][:80]}...")
            return True
        else:
            print("✗ No transcript segments found")
            print("\nThis video does not have captions/subtitles available.")
            return False
    else:
        print("✗ Failed to extract video data")
        return False

if __name__ == "__main__":
    # Test with a video from the playlist
    test_url = "https://www.youtube.com/watch?v=nC3T4sHo9eQ"  # Lecture 19 from the playlist
    
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    success = test_video_transcript(test_url)
    
    if not success:
        print("\n" + "=" * 60)
        print("⚠ This video doesn't have transcripts available.")
        print("=" * 60)
        print("\nSolutions:")
        print("1. Check if the video has automatic captions on YouTube")
        print("2. Try a different video that you know has captions")
        print("3. The playlist might have videos without captions")
        sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("✓ Video has transcripts available!")
        print("=" * 60)
        sys.exit(0)

