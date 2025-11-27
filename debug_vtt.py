import yt_dlp
import requests
import re

def debug_vtt(video_url):
    ydl_opts = {
        'quiet': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'subtitlesformat': 'vtt',
        'skip_download': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        
        subtitles = info.get('automatic_captions', {})
        if not subtitles or 'en' not in subtitles:
            subtitles = info.get('subtitles', {})
            
        if 'en' in subtitles:
            print("Available formats for 'en':")
            for fmt in subtitles['en']:
                print(f"  - {fmt.get('ext')} : {fmt.get('url')}")

            for fmt in subtitles['en']:
                if fmt.get('ext') == 'vtt':
                    url = fmt.get('url')
                    print(f"Downloading VTT from: {url}")
                    response = requests.get(url)
                    print("--- VTT Content Start ---")
                    print(response.text[:1000]) # Print first 1000 chars
                    print("--- VTT Content End ---")
                    
                    # Try parsing
                    segments = parse_vtt(response.text)
                    print(f"Parsed {len(segments)} segments")
                    return

def parse_vtt(vtt_content):
    segments = []
    lines = vtt_content.split('\n')
    
    current_segment = None
    current_text = []
    
    for line in lines:
        line = line.strip()
        
        # Check for timestamp line (format: 00:00:00.000 --> 00:00:00.000)
        timestamp_match = re.match(r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})\.(\d{3})', line)
        if timestamp_match:
            if current_segment and current_text:
                current_segment['text'] = ' '.join(current_text)
                segments.append(current_segment)
            
            # ... (skipping time conversion for brevity in debug)
            current_segment = {'text': ''}
            current_text = []
        elif line and current_segment and not line.startswith('WEBVTT') and not line.startswith('<'):
            clean_text = re.sub(r'<[^>]+>', '', line)
            if clean_text:
                current_text.append(clean_text)
    
    if current_segment and current_text:
        current_segment['text'] = ' '.join(current_text)
        segments.append(current_segment)
    
    return segments

if __name__ == "__main__":
    # Get first video from playlist
    playlist_url = "https://www.youtube.com/playlist?list=PLbRMhDVUMngfK1HrAqu6tnKEVHwC3ILuE"
    
    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        if 'entries' in info and info['entries']:
            first_video = info['entries'][0]
            video_url = f"https://www.youtube.com/watch?v={first_video['id']}"
            print(f"Testing with video: {video_url}")
            debug_vtt(video_url)
        else:
            print("Could not find videos in playlist")
