
import google.generativeai as genai
import os
from typing import List, Dict
import json
import time

class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        
        genai.configure(api_key=api_key)
        # Use a model that is available in the user's account
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_chapters(self, transcript_segments: List[Dict], video_duration: float) -> List[Dict]:
        """
        Generate chapters from transcript using sliding window approach
        """
        window_size_seconds = 300  # 5 minutes
        overlap_seconds = 60       # 1 minute
        
        windows = self._create_windows(transcript_segments, window_size_seconds, overlap_seconds)
        chapters = []
        
        print(f"Processing {len(windows)} windows for chapter generation...")
        
        for i, window in enumerate(windows):
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    window_text = " ".join([seg['text'] for seg in window['segments']])
                    start_time = window['start']
                    end_time = window['end']
                    
                    prompt = f"""
                    Analyze the following video transcript segment (from {start_time}s to {end_time}s) and identify the main topic or chapter.
                    
                    Transcript:
                    {window_text}
                    
                    Return a JSON object with the following fields:
                    - title: A concise and descriptive title for this section.
                    - description: A detailed summary of what is discussed in this section.
                    - key_concepts: A list of key concepts or terms mentioned.
                    - start_time: The specific start time (in seconds) where this topic actually begins within the segment.
                    - end_time: The specific end time (in seconds) where this topic ends within the segment.
                    
                    Only return the JSON object, no other text.
                    """
                    
                    response = self.model.generate_content(prompt)
                    
                    # Parse JSON response
                    try:
                        text = response.text.strip()
                        # Handle potential markdown code blocks
                        if text.startswith("```json"):
                            text = text[7:-3]
                        elif text.startswith("```"):
                            text = text[3:-3]
                            
                        data = json.loads(text)
                        
                        # Validate and use LLM provided timestamps if reasonable
                        chapter_start = data.get('start_time', start_time)
                        chapter_end = data.get('end_time', end_time)
                        
                        # Ensure timestamps are within the window bounds (with some buffer)
                        if chapter_start < start_time or chapter_start > end_time:
                            chapter_start = start_time
                        if chapter_end < start_time or chapter_end > end_time:
                            chapter_end = end_time
                            
                        chapters.append({
                            'start': chapter_start,
                            'end': chapter_end,
                            'title': data.get('title', 'Untitled Chapter'),
                            'description': data.get('description', ''),
                            'key_concepts': data.get('key_concepts', []),
                            'transcript_text': window_text
                        })
                        print(f"  Generated chapter: {data.get('title')} ({chapter_end - chapter_start:.1f}s)")
                        
                    except json.JSONDecodeError:
                        print(f"  Failed to parse JSON from LLM response for window {i}")
                        # Don't retry for JSON errors, likely model output issue
                        pass
                        
                    # Success, break retry loop
                    break
                    
                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "Quota exceeded" in error_str:
                        print(f"  Quota exceeded for window {i}. Using fallback (Raw Transcript).")
                        # Fallback: Create a chapter using the raw transcript
                        # Use first 80 chars of transcript as title
                        fallback_title = window_text[:80].strip() + "..." if len(window_text) > 80 else window_text
                        
                        chapters.append({
                            'start': start_time,
                            'end': end_time,
                            'title': fallback_title,
                            'description': window_text[:1000], # Use transcript as description
                            'key_concepts': [],
                            'transcript_text': window_text
                        })
                        break # Stop retrying and move to next window
                    else:
                        print(f"  Error generating chapter for window {i}: {e}")
                        break
            
            # Rate limiting between successful requests
            # Gemini Free Tier is ~15 RPM (1 request every 4 seconds)
            time.sleep(4)
                
        return self._refine_chapters(chapters)

    def _create_windows(self, segments: List[Dict], window_size: float, overlap: float) -> List[Dict]:
        windows = []
        if not segments:
            return windows
            
        current_start = segments[0]['start']
        video_end = segments[-1]['end']
        
        while current_start < video_end:
            current_end = current_start + window_size
            
            # Find segments that fall into this window
            window_segments = []
            for seg in segments:
                # If segment overlaps with window
                if (seg['start'] >= current_start and seg['start'] < current_end) or \
                   (seg['end'] > current_start and seg['end'] <= current_end) or \
                   (seg['start'] <= current_start and seg['end'] >= current_end):
                    window_segments.append(seg)
            
            if window_segments:
                windows.append({
                    'start': current_start,
                    'end': min(current_end, video_end),
                    'segments': window_segments
                })
            
            current_start += (window_size - overlap)
            
        return windows

    def _refine_chapters(self, chapters: List[Dict]) -> List[Dict]:
        """
        Merge overlapping or similar chapters if needed.
        For now, we just return the raw chapters from windows.
        In a production system, we might want to use LLM to merge them.
        """
        return chapters
