"""
Clip merging service to create meaningful video segments
Groups nearby/overlapping clips and expands boundaries for better context
"""
from typing import List, Dict
from collections import defaultdict
from backend.config import CLIP_MERGE_THRESHOLD, CLIP_MIN_DURATION, CLIP_CONTEXT_BEFORE, CLIP_CONTEXT_AFTER


class ClipMerger:
    def __init__(self, 
                 merge_threshold: float = None,  # Merge clips within N seconds
                 min_clip_duration: float = None,  # Minimum clip duration
                 context_before: float = None,  # Add N seconds before
                 context_after: float = None):  # Add N seconds after
        """
        Initialize clip merger
        
        Args:
            merge_threshold: Maximum gap (seconds) between clips to merge them
            min_clip_duration: Minimum duration for a clip (will expand if needed)
            context_before: Seconds to add before clip start
            context_after: Seconds to add after clip end
        """
        self.merge_threshold = merge_threshold if merge_threshold is not None else CLIP_MERGE_THRESHOLD
        self.min_clip_duration = min_clip_duration if min_clip_duration is not None else CLIP_MIN_DURATION
        self.context_before = context_before if context_before is not None else CLIP_CONTEXT_BEFORE
        self.context_after = context_after if context_after is not None else CLIP_CONTEXT_AFTER
    
    def merge_clips(self, results: List[Dict], video_durations: Dict[str, float] = None) -> List[Dict]:
        """
        Merge nearby/overlapping clips into meaningful segments
        
        Args:
            results: List of search result dictionaries with start/end times
            video_durations: Optional dict mapping video_id to video duration
            
        Returns:
            List of merged clip dictionaries
        """
        if not results:
            return []
        
        # Group results by video_id
        video_groups = defaultdict(list)
        for result in results:
            video_id = result.get('video_id', '')
            video_groups[video_id].append(result)
        
        merged_clips = []
        
        # Process each video's clips
        for video_id, clips in video_groups.items():
            # Sort clips by start time
            clips.sort(key=lambda x: x.get('start', 0))
            
            # Merge clips for this video
            video_merged = self._merge_video_clips(clips, video_id, video_durations)
            merged_clips.extend(video_merged)
        
        # Apply penalties and re-score clips
        for clip in merged_clips:
            video_id = clip.get('video_id', '')
            video_duration = video_durations.get(video_id, 0) if video_durations else 0
            clip['score'] = self._adjust_score_for_position(clip, video_duration)
        
        # Sort all merged clips by adjusted score (highest first)
        merged_clips.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return merged_clips
    
    def _merge_video_clips(self, clips: List[Dict], video_id: str, video_durations: Dict = None) -> List[Dict]:
        """
        Merge clips from a single video
        """
        if not clips:
            return []
        
        video_duration = video_durations.get(video_id, 0) if video_durations else 0
        
        # Start with first clip
        merged = []
        current_clip = clips[0].copy()
        
        # Combine text from all clips
        combined_texts = [current_clip.get('text', '')]
        combined_scores = [current_clip.get('score', 0)]
        
        for next_clip in clips[1:]:
            current_end = current_clip.get('end', 0)
            next_start = next_clip.get('start', 0)
            gap = next_start - current_end
            
            # If clips are close enough, merge them
            if gap <= self.merge_threshold:
                # Extend current clip to include next clip
                current_clip['end'] = max(current_end, next_clip.get('end', 0))
                
                # Combine texts (avoid duplicates)
                next_text = next_clip.get('text', '')
                if next_text and next_text not in combined_texts:
                    combined_texts.append(next_text)
                
                # Track scores (use max or average)
                combined_scores.append(next_clip.get('score', 0))
                
                # Update metadata from next clip if better (preserve all metadata)
                if next_clip.get('score', 0) > current_clip.get('score', 0):
                    # Keep higher scoring clip's metadata, but preserve all fields
                    for key in ['video_title', 'video_url', 'video_description', 'channel', 'thumbnail', 
                               'view_count', 'like_count', 'channel_id']:
                        if key in next_clip and next_clip[key]:
                            current_clip[key] = next_clip[key]
            else:
                # Clips are too far apart, finalize current clip and start new one
                current_clip = self._finalize_clip(current_clip, combined_texts, combined_scores, video_duration)
                merged.append(current_clip)
                
                # Start new clip
                current_clip = next_clip.copy()
                combined_texts = [current_clip.get('text', '')]
                combined_scores = [current_clip.get('score', 0)]
        
        # Finalize last clip
        current_clip = self._finalize_clip(current_clip, combined_texts, combined_scores, video_duration)
        merged.append(current_clip)
        
        return merged
    
    def _finalize_clip(self, clip: Dict, texts: List[str], scores: List[float], video_duration: float) -> Dict:
        """
        Finalize a clip: expand boundaries, ensure minimum duration, combine text
        """
        start = clip.get('start', 0)
        end = clip.get('end', 0)
        original_start = start
        original_end = end
        
        # Add context before and after
        start = max(0, start - self.context_before)
        if video_duration > 0:
            end = min(video_duration, end + self.context_after)
        else:
            end = end + self.context_after
        
        # Ensure minimum duration
        clip_duration = end - start
        if clip_duration < self.min_clip_duration:
            # Expand equally on both sides, but prefer expanding backward
            # (earlier content is usually more valuable than later)
            expansion_needed = (self.min_clip_duration - clip_duration) / 2
            
            # Try to expand backward first (60% backward, 40% forward)
            backward_expansion = expansion_needed * 1.2
            forward_expansion = expansion_needed * 0.8
            
            start = max(0, start - backward_expansion)
            if video_duration > 0:
                end = min(video_duration, end + forward_expansion)
            else:
                end = end + forward_expansion
            
            # If we hit video start boundary, expand forward more
            if start == 0 and end - start < self.min_clip_duration:
                additional_forward = self.min_clip_duration - (end - start)
                if video_duration > 0:
                    end = min(video_duration, end + additional_forward)
                else:
                    end = end + additional_forward
        
        # Combine texts intelligently
        # Remove duplicates and very short texts
        unique_texts = []
        seen = set()
        for text in texts:
            text_lower = text.lower().strip()
            if text_lower and text_lower not in seen and len(text_lower) > 10:
                seen.add(text_lower)
                unique_texts.append(text)
        
        # Combine texts (limit total length)
        # Prefer longer, more informative texts
        unique_texts.sort(key=len, reverse=True)  # Sort by length (longest first)
        combined_text = ' '.join(unique_texts[:3])  # Take first 3 unique texts
        if len(combined_text) > 500:
            combined_text = combined_text[:500] + '...'
        
        # Penalize clips with conclusion-like text patterns
        text_lower = combined_text.lower()
        conclusion_patterns = [
            'hope you have understood',
            'hope you understood',
            'that\'s all',
            'thank you for watching',
            'see you in the next',
            'in the next video',
            'subscribe',
            'like and subscribe',
            'this is how',
            'this is the end',
            'conclusion',
            'summary',
            'wrap up',
            'wrap-up'
        ]
        
        # If text looks like conclusion, reduce score
        if any(pattern in text_lower for pattern in conclusion_patterns):
            clip['_is_conclusion'] = True
        else:
            clip['_is_conclusion'] = False
        
        # Calculate average score
        avg_score = sum(scores) / len(scores) if scores else clip.get('score', 0)
        
        # Update clip boundaries and text
        clip['start'] = start
        clip['end'] = end
        clip['text'] = combined_text if combined_text else clip.get('text', '')
        clip['score'] = avg_score
        
        # Store original boundaries for reference (optional, for debugging)
        # clip['original_start'] = original_start
        # clip['original_end'] = original_end
        
        # Ensure all metadata fields are preserved
        # (video_id, video_title, video_url, etc. should already be in clip)
        
        return clip
    
    def _adjust_score_for_position(self, clip: Dict, video_duration: float) -> float:
        """
        Adjust clip score based on its position in the video
        Penalizes clips from the end (conclusions) and very beginning (intros)
        Prefers clips from the middle/early-middle where actual content is
        """
        if video_duration <= 0:
            return clip.get('score', 0)
        
        start = clip.get('start', 0)
        end = clip.get('end', 0)
        clip_midpoint = (start + end) / 2
        
        # Calculate position as percentage (0.0 = start, 1.0 = end)
        position_ratio = clip_midpoint / video_duration
        
        original_score = clip.get('score', 0)
        
        # Heavy penalty if clip is marked as conclusion based on text
        is_conclusion = clip.get('_is_conclusion', False)
        if is_conclusion:
            original_score = original_score * 0.3  # Reduce by 70%
        
        # Penalize clips from the last 15% of video (conclusions/wrap-ups)
        if position_ratio > 0.85:
            # Heavy penalty for conclusion clips
            penalty = 0.6  # Reduce score by 60%
            adjusted_score = original_score * (1 - penalty)
        # Slight penalty for last 25% (might be conclusions)
        elif position_ratio > 0.75:
            penalty = 0.3  # Reduce score by 30%
            adjusted_score = original_score * (1 - penalty)
        # Slight penalty for very beginning (0-5%) - might be intro/outline
        elif position_ratio < 0.05:
            penalty = 0.15  # Reduce score by 15%
            adjusted_score = original_score * (1 - penalty)
        # Boost clips from 5% to 75% (content-rich middle section)
        elif 0.05 <= position_ratio <= 0.75:
            boost = 0.15  # Boost score by 15%
            adjusted_score = original_score * (1 + boost)
        else:
            adjusted_score = original_score
        
        return max(0, adjusted_score)  # Ensure non-negative

