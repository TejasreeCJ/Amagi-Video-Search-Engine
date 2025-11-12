"""
YouTube playlist scraper to extract video information and transcripts
"""
import yt_dlp
import json
from typing import List, Dict, Optional
import re


class YouTubeScraper:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'writesubtitles': False,
            'writeautomaticsub': False,
        }

    def get_playlist_videos(self, playlist_url: str) -> List[Dict]:
        """
        Extract all video information from a YouTube playlist
        """
        ydl_opts = {
            **self.ydl_opts,
            'extract_flat': True,
            'playlistend': None,  # Get all videos
            'ignoreerrors': False,  # Don't ignore errors, we want to see them
        }
        
        videos = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                print(f"Extracting playlist information from: {playlist_url}")
                info = ydl.extract_info(playlist_url, download=False)
                
                if not info:
                    print("Error: No playlist information returned")
                    return videos
                
                print(f"Playlist title: {info.get('title', 'Unknown')}")
                print(f"Playlist ID: {info.get('id', 'Unknown')}")
                
                # Check if it's a playlist or a single video
                if 'entries' in info:
                    entries = info['entries']
                    print(f"Found {len(entries) if entries else 0} entries in playlist")
                    
                    if entries:
                        for i, entry in enumerate(entries):
                            if entry is None:
                                print(f"Warning: Entry {i} is None (might be unavailable)")
                                continue
                            
                            video_id = entry.get('id')
                            title = entry.get('title', 'Unknown')
                            
                            if not video_id:
                                print(f"Warning: Entry {i} has no video ID")
                                continue
                            
                            videos.append({
                                'video_id': video_id,
                                'title': title,
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                            })
                            print(f"  Added video {i+1}: {title}")
                    else:
                        print("Warning: Playlist entries list is empty")
                else:
                    # Might be a single video instead of a playlist
                    if info.get('id'):
                        print("Single video detected (not a playlist)")
                        videos.append({
                            'video_id': info.get('id'),
                            'title': info.get('title', 'Unknown'),
                            'url': playlist_url if 'watch?v=' in playlist_url else f"https://www.youtube.com/watch?v={info.get('id')}",
                        })
                    else:
                        print("Error: No entries found and no video ID")
                        
            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e)
                print(f"Download error: {error_msg}")
                if "Private video" in error_msg or "This video is private" in error_msg:
                    raise Exception("Playlist contains private videos. Please make the playlist public or unlisted.")
                elif "Video unavailable" in error_msg or "This video is unavailable" in error_msg:
                    raise Exception("Some videos in the playlist are unavailable.")
                elif "Sign in" in error_msg or "login" in error_msg.lower():
                    raise Exception("Playlist might require authentication. Please ensure the playlist is public.")
                else:
                    raise Exception(f"Failed to extract playlist: {error_msg}")
            except Exception as e:
                error_msg = str(e)
                print(f"Error extracting playlist: {error_msg}")
                raise Exception(f"Failed to extract playlist: {error_msg}")
        
        print(f"Total videos extracted: {len(videos)}")
        return videos

    def get_video_transcript(self, video_url: str) -> Optional[Dict]:
        """
        Extract transcript with timestamps from a YouTube video
        Returns: Dict with video info and transcript segments
        """
        ydl_opts = {
            **self.ydl_opts,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'subtitlesformat': 'vtt',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                video_id = info.get('id')
                title = info.get('title')
                description = info.get('description', '')
                duration = info.get('duration', 0)
                
                # Try to get automatic captions first, then manual subtitles
                subtitles = info.get('automatic_captions', {})
                if not subtitles or 'en' not in subtitles:
                    subtitles = info.get('subtitles', {})
                
                transcript_segments = []
                
                # Try English first, then any available language
                languages_to_try = ['en']
                if 'en' not in subtitles:
                    available_langs = list(subtitles.keys())[:3] if subtitles else []
                    if available_langs:
                        languages_to_try = available_langs
                        print(f"  English subtitles not available, trying: {languages_to_try}")
                    else:
                        print(f"  ⚠ No subtitles available for this video")
                        return {
                            'video_id': video_id,
                            'title': title,
                            'description': description,
                            'duration': duration,
                            'url': video_url,
                            'transcript': [],
                        }
                
                for lang in languages_to_try:
                    if lang in subtitles:
                        subtitle_url = None
                        # Prefer VTT format, fallback to other formats
                        preferred_formats = ['vtt', 'ttml', 'srv3', 'srv2', 'srv1']
                        for fmt in subtitles[lang]:
                            if fmt.get('ext') in preferred_formats:
                                subtitle_url = fmt.get('url')
                                if fmt.get('ext') == 'vtt':  # Prefer VTT
                                    break
                        
                        if subtitle_url:
                            try:
                                import requests
                                response = requests.get(subtitle_url, timeout=30)
                                if response.status_code == 200:
                                    transcript_segments = self._parse_vtt(response.text)
                                    if transcript_segments:
                                        print(f"  ✓ Successfully extracted {len(transcript_segments)} transcript segments ({lang})")
                                        break
                                    else:
                                        print(f"  ⚠ No transcript segments found in subtitle file ({lang})")
                                else:
                                    print(f"  ⚠ Failed to fetch subtitles: HTTP {response.status_code}")
                            except Exception as e:
                                print(f"  ⚠ Error fetching subtitles ({lang}): {e}")
                                continue
                        else:
                            print(f"  ⚠ No subtitle URL found for language: {lang}")
                
                if not transcript_segments:
                    print(f"  ✗ No transcript segments extracted for this video")
                
                return {
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'duration': duration,
                    'url': video_url,
                    'transcript': transcript_segments,
                }
        except Exception as e:
            print(f"Error extracting transcript from {video_url}: {e}")
            return None

    def _parse_vtt(self, vtt_content: str) -> List[Dict]:
        """
        Parse VTT subtitle format to extract text with timestamps
        """
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
                
                start_time = self._vtt_time_to_seconds(
                    timestamp_match.group(1), timestamp_match.group(2),
                    timestamp_match.group(3), timestamp_match.group(4)
                )
                end_time = self._vtt_time_to_seconds(
                    timestamp_match.group(5), timestamp_match.group(6),
                    timestamp_match.group(7), timestamp_match.group(8)
                )
                
                current_segment = {
                    'start': start_time,
                    'end': end_time,
                    'text': ''
                }
                current_text = []
            elif line and current_segment and not line.startswith('WEBVTT') and not line.startswith('<'):
                # Remove HTML tags and append text
                clean_text = re.sub(r'<[^>]+>', '', line)
                if clean_text:
                    current_text.append(clean_text)
        
        # Add last segment
        if current_segment and current_text:
            current_segment['text'] = ' '.join(current_text)
            segments.append(current_segment)
        
        return segments

    def _vtt_time_to_seconds(self, hours: str, minutes: str, seconds: str, milliseconds: str) -> float:
        """Convert VTT timestamp to seconds"""
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0

    def get_playlist_with_transcripts(self, playlist_url: str) -> List[Dict]:
        """
        Get all videos from playlist with their transcripts
        """
        videos = self.get_playlist_videos(playlist_url)
        
        if not videos:
            raise Exception("No videos found in playlist. Please check:\n"
                          "1. The playlist is public or unlisted\n"
                          "2. The playlist URL is correct\n"
                          "3. The playlist contains videos\n"
                          "4. You have internet connection")
        
        print(f"\nProcessing {len(videos)} videos for transcripts...")
        videos_with_transcripts = []
        
        for i, video in enumerate(videos, 1):
            print(f"\n[{i}/{len(videos)}] Processing: {video['title']}")
            video_data = self.get_video_transcript(video['url'])
            if video_data:
                if video_data['transcript']:
                    print(f"  ✓ Transcript found: {len(video_data['transcript'])} segments")
                    videos_with_transcripts.append(video_data)
                else:
                    print(f"  ✗ No transcript available for this video")
            else:
                print(f"  ✗ Failed to extract video data")
        
        print(f"\nSuccessfully processed {len(videos_with_transcripts)}/{len(videos)} videos with transcripts")
        return videos_with_transcripts

