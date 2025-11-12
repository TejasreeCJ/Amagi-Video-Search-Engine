"""
Quick test script to check if a playlist URL is accessible
"""
import sys
import yt_dlp

def test_playlist_url(playlist_url):
    """Test if a playlist URL can be accessed"""
    print("=" * 60)
    print("Testing Playlist URL")
    print("=" * 60)
    print(f"URL: {playlist_url}\n")
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
        'extract_flat': True,
        'playlistend': 5,  # Just test first 5 videos
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Attempting to extract playlist information...")
            info = ydl.extract_info(playlist_url, download=False)
            
            if not info:
                print("❌ ERROR: No information returned")
                return False
            
            print(f"\n✓ Playlist Title: {info.get('title', 'Unknown')}")
            print(f"✓ Playlist ID: {info.get('id', 'Unknown')}")
            print(f"✓ Playlist Type: {info.get('_type', 'Unknown')}")
            
            if 'entries' in info:
                entries = info['entries']
                print(f"\n✓ Found {len(entries) if entries else 0} entries")
                
                if entries:
                    print("\nFirst few videos:")
                    for i, entry in enumerate(entries[:5], 1):
                        if entry:
                            print(f"  {i}. {entry.get('title', 'Unknown')} (ID: {entry.get('id', 'N/A')})")
                        else:
                            print(f"  {i}. [Entry is None - video might be unavailable]")
                else:
                    print("⚠ WARNING: Playlist entries list is empty")
                    return False
            else:
                # Might be a single video
                if info.get('id'):
                    print(f"\n✓ Single video detected: {info.get('title')}")
                    print("  Note: This is a video URL, not a playlist URL")
                else:
                    print("❌ ERROR: No entries found")
                    return False
            
            print("\n" + "=" * 60)
            print("✓ Playlist is accessible!")
            print("=" * 60)
            return True
            
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        print(f"\n❌ Download Error: {error_msg}")
        
        if "Private video" in error_msg:
            print("\n💡 Solution: Make sure the playlist is public or unlisted")
        elif "Video unavailable" in error_msg:
            print("\n💡 Solution: Some videos might be unavailable or deleted")
        elif "Sign in" in error_msg or "login" in error_msg.lower():
            print("\n💡 Solution: The playlist might require authentication")
        elif "This video is not available" in error_msg:
            print("\n💡 Solution: Videos might be region-restricted or deleted")
        else:
            print("\n💡 Try:")
            print("  1. Update yt-dlp: pip install --upgrade yt-dlp")
            print("  2. Check if the playlist is public")
            print("  3. Verify the URL is correct")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter playlist URL: ").strip()
    
    if not url:
        print("No URL provided")
        sys.exit(1)
    
    success = test_playlist_url(url)
    sys.exit(0 if success else 1)

