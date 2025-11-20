"""
Knowledge Graph Service for creating interactive mind maps from video transcripts
"""
import re
from typing import List, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict

from backend.youtube_scraper import YouTubeScraper
from backend.embedding_service import EmbeddingService


class KnowledgeGraphService:
    """
    Service to analyze video transcripts and create knowledge graphs
    with logical topic flow and clip boundaries
    """
    
    def __init__(self):
        self.youtube_scraper = YouTubeScraper()
        self.embedding_service = EmbeddingService()
        
    def generate_knowledge_graph(self, video_url: str, min_clip_duration: float = 30.0) -> Dict:
        """
        Generate a knowledge graph from a single video
        
        Args:
            video_url: YouTube video URL
            min_clip_duration: Minimum duration for a clip in seconds (0 for dynamic)
            
        Returns:
            Dictionary containing nodes, edges, and clips
        """
        # Get video transcript
        video_data = self.youtube_scraper.get_video_transcript(video_url)
        
        if not video_data or not video_data.get('transcript'):
            raise ValueError("Could not extract transcript from video")
        
        transcript_segments = video_data['transcript']
        
        # Calculate dynamic min duration if set to 0
        if min_clip_duration <= 0:
            # Calculate based on video length - aim for 10-20 clips
            total_duration = video_data.get('duration', 0)
            min_clip_duration = max(20.0, min(60.0, total_duration / 15))  # 20-60 seconds
        
        # Create logical clips based on topic boundaries
        clips = self._create_logical_clips(transcript_segments, min_clip_duration)
        
        # Extract topics/concepts from each clip
        topics = self._extract_topics_from_clips(clips)
        
        # Build knowledge graph
        graph_data = self._build_knowledge_graph(clips, topics)
        
        # Add video metadata
        graph_data['video_info'] = {
            'video_id': video_data.get('video_id'),
            'title': video_data.get('title', 'Unknown'),
            'duration': video_data.get('duration', 0),
            'thumbnail': f"https://img.youtube.com/vi/{video_data.get('video_id')}/maxresdefault.jpg"
        }
        
        return graph_data
    
    def _create_logical_clips(self, segments: List[Dict], min_duration: float) -> List[Dict]:
        """
        Create clips based on topic boundaries and logical flow
        Uses semantic similarity to detect topic changes with improved boundary detection
        """
        if not segments:
            return []
        
        # Extract text from segments
        texts = [seg['text'] for seg in segments]
        
        # Calculate semantic boundaries using improved algorithm
        boundaries = self._detect_topic_boundaries(texts, window_size=3)
        
        # Create clips based on boundaries with better merging logic
        clips = []
        current_clip_start = 0
        accumulated_duration = 0
        
        for i, is_boundary in enumerate(boundaries):
            if i == 0:
                continue
                
            # Calculate duration up to this point
            if i < len(segments):
                accumulated_duration = segments[i]['end'] - segments[current_clip_start]['start']
            
            # Create clip at boundary if minimum duration met or last segment
            should_create_clip = (is_boundary and accumulated_duration >= min_duration) or (i == len(boundaries) - 1)
            
            if should_create_clip:
                end_idx = i + 1 if i < len(segments) else len(segments)
                clip_segments = segments[current_clip_start:end_idx]
                
                if clip_segments:
                    start_time = clip_segments[0]['start']
                    end_time = clip_segments[-1]['end']
                    duration = end_time - start_time
                    clip_text = ' '.join([seg['text'] for seg in clip_segments])
                    
                    clips.append({
                        'clip_id': len(clips),
                        'start_time': start_time,
                        'end_time': end_time,
                        'duration': duration,
                        'text': clip_text,
                        'segments': clip_segments,
                        'segment_count': len(clip_segments)
                    })
                    
                    current_clip_start = end_idx
                    accumulated_duration = 0
        
        return clips
    
    def _detect_topic_boundaries(self, texts: List[str], window_size: int = 3) -> List[bool]:
        """
        Detect topic boundaries using improved semantic similarity algorithm
        Returns boolean list indicating boundary points
        """
        if len(texts) < 2:
            return [False] * len(texts)
        
        # Create embeddings for each text segment
        embeddings = []
        for text in texts:
            if text.strip():
                emb = self.embedding_service.create_embeddings([text])[0]
                embeddings.append(emb)
            else:
                embeddings.append([0] * 384)  # Zero vector for empty text
        
        embeddings = np.array(embeddings)
        
        # Calculate pairwise similarities
        boundaries = [False] * len(texts)
        
        # Use a dynamic threshold based on the distribution
        similarities = []
        for i in range(1, len(texts)):
            sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
            similarities.append(sim)
        
        if not similarities:
            return boundaries
        
        # Calculate threshold as mean - std (adaptive thresholding)
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)
        threshold = mean_sim - (0.5 * std_sim)  # More sensitive to changes
        
        # Detect boundaries with context window
        for i in range(window_size, len(texts) - window_size):
            # Compare similarity between before and after windows
            before_window = embeddings[max(0, i-window_size):i]
            after_window = embeddings[i:min(len(embeddings), i+window_size)]
            
            if len(before_window) == 0 or len(after_window) == 0:
                continue
            
            # Calculate average embeddings for each window
            before_avg = np.mean(before_window, axis=0)
            after_avg = np.mean(after_window, axis=0)
            
            # Calculate cosine similarity
            similarity = cosine_similarity([before_avg], [after_avg])[0][0]
            
            # Mark as boundary if similarity drops significantly
            if similarity < threshold:
                # Additional check: ensure consecutive segments are also different
                if i > 0 and i < len(embeddings) - 1:
                    prev_sim = cosine_similarity([embeddings[i-1]], [embeddings[i]])[0][0]
                    next_sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
                    
                    # Confirm boundary if current position shows transition
                    if prev_sim < mean_sim or next_sim < mean_sim:
                        boundaries[i] = True
        
        return boundaries
    
    def _extract_topics_from_clips(self, clips: List[Dict]) -> Dict[int, List[str]]:
        """
        Extract key topics/concepts from each clip using improved TF-IDF
        """
        if not clips:
            return {}
        
        # Extract text from clips
        clip_texts = [clip['text'] for clip in clips]
        
        # Use TF-IDF with better parameters for topic extraction
        vectorizer = TfidfVectorizer(
            max_features=20,  # More features for better selection
            stop_words='english',
            ngram_range=(1, 3),  # Unigrams to trigrams
            min_df=1,
            max_df=0.8,  # Exclude very common terms
            token_pattern=r'\b[a-zA-Z][a-zA-Z]+\b'  # Better word matching
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(clip_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            topics = {}
            for i, clip in enumerate(clips):
                # Get top keywords for this clip
                clip_tfidf = tfidf_matrix[i].toarray()[0]
                top_indices = clip_tfidf.argsort()[-8:][::-1]  # Top 8 keywords
                
                # Filter and format keywords
                clip_topics = []
                for idx in top_indices:
                    if clip_tfidf[idx] > 0:
                        keyword = feature_names[idx]
                        # Prefer longer, more descriptive phrases
                        if len(keyword.split()) > 1 or len(keyword) > 5:
                            clip_topics.append(keyword)
                
                # If we have few multi-word topics, add some single words
                if len(clip_topics) < 3:
                    for idx in top_indices:
                        if clip_tfidf[idx] > 0:
                            keyword = feature_names[idx]
                            if keyword not in clip_topics:
                                clip_topics.append(keyword)
                        if len(clip_topics) >= 5:
                            break
                
                topics[clip['clip_id']] = clip_topics[:5]  # Keep top 5
                
        except Exception as e:
            # Fallback: extract simple keywords with better frequency analysis
            topics = {}
            for clip in clips:
                # Extract words (at least 4 chars)
                words = re.findall(r'\b[a-zA-Z]{4,}\b', clip['text'].lower())
                # Remove common stop words
                common_words = {'that', 'this', 'with', 'from', 'have', 'will', 'your', 'they', 'their', 'about', 'into', 'than', 'some', 'what', 'when', 'where', 'which', 'these', 'those'}
                words = [w for w in words if w not in common_words]
                
                word_freq = defaultdict(int)
                for word in words:
                    word_freq[word] += 1
                
                # Get top 5 by frequency
                top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
                topics[clip['clip_id']] = [word for word, freq in top_words]
        
        return topics
    
    def _build_knowledge_graph(self, clips: List[Dict], topics: Dict[int, List[str]]) -> Dict:
        """
        Build a knowledge graph structure with nodes and edges
        """
        nodes = []
        edges = []
        
        # Create nodes for each clip
        for clip in clips:
            clip_id = clip['clip_id']
            clip_topics = topics.get(clip_id, [])
            
            # Create a summary title from topics
            title = self._create_clip_title(clip_topics, clip['text'])
            
            node = {
                'id': f"clip_{clip_id}",
                'label': title,
                'clip_id': clip_id,
                'start_time': clip['start_time'],
                'end_time': clip['end_time'],
                'duration': clip['duration'],
                'topics': clip_topics,
                'text': clip['text'][:200] + '...' if len(clip['text']) > 200 else clip['text'],
                'level': self._calculate_node_level(clip_id, len(clips))
            }
            nodes.append(node)
        
        # Create edges based on temporal flow and topic similarity
        for i in range(len(clips) - 1):
            # Sequential edge (temporal flow)
            edges.append({
                'from': f"clip_{i}",
                'to': f"clip_{i+1}",
                'type': 'sequential',
                'label': 'continues to',
                'strength': 1.0
            })
            
            # Check for topic relationships with non-adjacent clips
            for j in range(i + 2, min(i + 5, len(clips))):  # Look ahead 2-4 clips
                similarity = self._calculate_topic_similarity(
                    topics.get(i, []),
                    topics.get(j, [])
                )
                
                if similarity > 0.3:  # Threshold for topic relationship
                    edges.append({
                        'from': f"clip_{i}",
                        'to': f"clip_{j}",
                        'type': 'related',
                        'label': 'related topic',
                        'strength': similarity
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'clips': clips
        }
    
    def _create_clip_title(self, topics: List[str], text: str, max_length: int = 60) -> str:
        """
        Create a descriptive title for the clip from topics or text with better summarization
        """
        if topics and len(topics) > 0:
            # Clean and format topics
            clean_topics = []
            for topic in topics[:3]:  # Use top 3 topics
                # Remove common words and clean up
                topic = topic.strip().title()
                if len(topic) > 3 and topic.lower() not in ['the', 'and', 'for', 'with']:
                    clean_topics.append(topic)
            
            if clean_topics:
                title = ' • '.join(clean_topics)
                if len(title) <= max_length:
                    return title
                else:
                    # If too long, use fewer topics
                    title = ' • '.join(clean_topics[:2])
                    return title[:max_length-3] + '...' if len(title) > max_length else title
        
        # Fallback: extract key sentence from text
        sentences = re.split(r'[.!?]+', text.strip())
        
        # Find the most informative sentence (longest non-trivial one)
        best_sentence = ""
        for sentence in sentences:
            sentence = sentence.strip()
            # Skip very short or very long sentences
            if 20 < len(sentence) < 100:
                # Prefer sentences with capital letters (proper nouns, important terms)
                if sentence and len(sentence) > len(best_sentence):
                    best_sentence = sentence
        
        if best_sentence:
            title = best_sentence.strip()
        else:
            # Last resort: use first sentence or beginning of text
            title = sentences[0].strip() if sentences else text[:max_length]
        
        # Clean up and truncate
        title = ' '.join(title.split())  # Remove extra whitespace
        if len(title) > max_length:
            title = title[:max_length-3] + '...'
        
        return title.title() if title else "Untitled Clip"
    
    def _calculate_node_level(self, clip_id: int, total_clips: int) -> int:
        """
        Calculate hierarchical level for visualization
        """
        # Simple level calculation based on position
        if clip_id < total_clips * 0.25:
            return 0  # Introduction
        elif clip_id < total_clips * 0.75:
            return 1  # Main content
        else:
            return 2  # Conclusion
    
    def _calculate_topic_similarity(self, topics1: List[str], topics2: List[str]) -> float:
        """
        Calculate similarity between two sets of topics
        """
        if not topics1 or not topics2:
            return 0.0
        
        set1 = set(topics1)
        set2 = set(topics2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
