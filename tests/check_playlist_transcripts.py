"""
Check which videos in a playlist have transcripts available
"""
import sys
from backend.youtube_scraper import YouTubeScraper

def check_playlist_transcripts(playlist_url):
    """Check which videos in the playlist have transcripts"""
    print("=" * 70)
    print("Checking Playlist for Videos with Transcripts")
    print("=" * 70)
    print(f"Playlist URL: {playlist_url}\n")
    
    scraper = YouTubeScraper()
    
    # Get all videos from playlist
    print("Step 1: Extracting videos from playlist...")
    videos = scraper.get_playlist_videos(playlist_url)
    
    if not videos:
        print("❌ No videos found in playlist")
        return
    
    print(f"✓ Found {len(videos)} videos in playlist\n")
    print("=" * 70)
    print("Step 2: Checking transcripts for each video...")
    print("=" * 70)
    
    videos_with_transcripts = []
    videos_without_transcripts = []
    
    for i, video in enumerate(videos, 1):
        print(f"\n[{i}/{len(videos)}] Checking: {video['title']}")
        print(f"    URL: {video['url']}")
        
        video_data = scraper.get_video_transcript(video['url'])
        
        if video_data and video_data['transcript']:
            segment_count = len(video_data['transcript'])
            videos_with_transcripts.append({
                'title': video['title'],
                'video_id': video['video_id'],
                'segments': segment_count
            })
            print(f"    ✓ HAS TRANSCRIPTS: {segment_count} segments")
        else:
            videos_without_transcripts.append({
                'title': video['title'],
                'video_id': video['video_id']
            })
            print(f"    ✗ NO TRANSCRIPTS")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total videos: {len(videos)}")
    print(f"Videos WITH transcripts: {len(videos_with_transcripts)}")
    print(f"Videos WITHOUT transcripts: {len(videos_without_transcripts)}")
    
    if videos_with_transcripts:
        print("\n✓ Videos WITH transcripts:")
        for video in videos_with_transcripts:
            print(f"  - {video['title']} ({video['segments']} segments)")
    
    if videos_without_transcripts:
        print("\n✗ Videos WITHOUT transcripts:")
        for video in videos_without_transcripts:
            print(f"  - {video['title']}")
    
    print("\n" + "=" * 70)
    if videos_with_transcripts:
        print(f"✓ {len(videos_with_transcripts)} video(s) can be processed")
        print("You can process the playlist, but only videos with transcripts will be indexed.")
    else:
        print("❌ No videos in this playlist have transcripts available")
        print("\nSOLUTIONS:")
        print("1. Use a different playlist that has videos with automatic captions")
        print("2. Enable automatic captions on the videos in YouTube Studio")
        print("3. Try an NPTEL playlist (they usually have captions):")
        print("   https://www.youtube.com/playlist?list=PLbMVogVj5nJQ2vsW_hmyvVfO4GYWaaPpO")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter playlist URL: ").strip()
    
    if not url:
        print("No URL provided")
        sys.exit(1)
    
    check_playlist_transcripts(url)

