"""
Whisper-based transcript generation service for videos without subtitles
"""
import os
import tempfile
import whisper
from typing import Dict, List, Optional, Tuple
import yt_dlp
import time
from pathlib import Path
import logging
from datetime import timedelta
from backend.config import WHISPER_MODEL_SIZE, WHISPER_ENABLED

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhisperService:
    """
    Service for generating transcripts using OpenAI Whisper when YouTube subtitles are not available
    """
    
    def __init__(self, model_size: str = "tiny", device: str = "cpu"):
        """
        Initialize Whisper service
        
        Args:
            model_size: Size of Whisper model ('tiny', 'base', 'small', 'medium', 'large')
            device: Device to use ('cpu', 'cuda')
        """
        self.model_size = model_size
        self.device = device
        self.model = None
        self.accuracy_metrics = {
            'total_videos_processed': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_processing_time': 0.0,
            'total_audio_duration_processed': 0.0
        }
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            start_time = time.time()
            
            # Use the specified model size
            # For production, you can switch to larger models:
            # model_sizes = {
            #     'tiny': 'openai/whisper-tiny',      # ~39 MB, fastest, lowest accuracy
            #     'base': 'openai/whisper-base',      # ~74 MB
            #     'small': 'openai/whisper-small',    # ~244 MB
            #     'medium': 'openai/whisper-medium',  # ~769 MB
            #     'large': 'openai/whisper-large'     # ~1550 MB, slowest, highest accuracy
            # }
            model_sizes = {
                'tiny': 'tiny',      # Using built-in tiny model for now
                'base': 'base',      # Commented options for larger models
                'small': 'small',    # Uncomment these for better accuracy
                'medium': 'medium',  # at the cost of speed and memory
                'large': 'large'
            }
            
            model_name = model_sizes.get(self.model_size, 'tiny')
            self.model = whisper.load_model(model_name, device=self.device)
            
            load_time = time.time() - start_time
            logger.info(f"Whisper model '{model_name}' loaded successfully in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise Exception(f"Failed to initialize Whisper service: {e}")
    
    def generate_transcript_for_video(self, video_url: str, video_id: str = None) -> Optional[Dict]:
        """
        Generate transcript for a video using Whisper
        
        Args:
            video_url: YouTube video URL
            video_id: Optional video ID for reference
            
        Returns:
            Dict with video info and generated transcript segments, or None if failed
        """
        if not WHISPER_ENABLED:
            logger.info("Whisper service is disabled in configuration")
            return None
            
        try:
            print(f"🤖 WHISPER: Starting transcript generation for video")
            print(f"   📹 Video: {video_url}")
            print(f"   🧠 Model: {self.model_size}")
            
            start_time = time.time()
            
            # Extract video info
            print(f"📋 WHISPER: Extracting video information...")
            video_info = self._extract_video_info(video_url)
            if not video_info:
                print(f"❌ WHISPER: Failed to extract video information")
                logger.error(f"Failed to extract video info from: {video_url}")
                return None
            
            print(f"✅ WHISPER: Video info extracted")
            print(f"   📝 Title: {video_info.get('title', 'Unknown')[:50]}...")
            print(f"   ⏱️ Duration: {video_info.get('duration', 0)} seconds")
            
            # Download audio
            print(f"⬇️ WHISPER: Downloading audio from video...")
            audio_path = self._download_audio(video_url)
            if not audio_path:
                print(f"❌ WHISPER: Failed to download audio")
                logger.error(f"Failed to download audio from: {video_url}")
                return None
            
            print(f"✅ WHISPER: Audio downloaded successfully")
            
            try:
                # Generate transcript using Whisper
                print(f"🎤 WHISPER: Starting AI transcription...")
                print(f"   ⏳ This may take several minutes depending on video length...")
                
                transcript_segments = self._transcribe_audio(audio_path)
                
                if not transcript_segments:
                    print(f"❌ WHISPER: No transcript segments generated")
                    logger.warning(f"No transcript segments generated for video: {video_url}")
                    return None
                
                processing_time = time.time() - start_time
                audio_duration = video_info.get('duration', 0)
                
                # Update accuracy metrics
                self._update_accuracy_metrics(
                    success=True,
                    processing_time=processing_time,
                    audio_duration=audio_duration
                )
                
                print(f"✅ WHISPER: Transcript generation completed!")
                print(f"   📊 Generated: {len(transcript_segments)} transcript segments")
                print(f"   ⏱️ Processing time: {processing_time:.2f} seconds")
                print(f"   📈 Success rate: {audio_duration/processing_time:.1f}x real-time")
                
                return {
                    'video_id': video_info.get('id'),
                    'title': video_info.get('title'),
                    'description': video_info.get('description', ''),
                    'duration': video_info.get('duration', 0),
                    'url': video_url,
                    'transcript': transcript_segments,
                    'transcript_source': 'whisper',
                    'model_used': self.model_size,
                    'generation_time': processing_time
                }
                
            finally:
                # Clean up downloaded audio file
                print(f"🧹 WHISPER: Cleaning up temporary files...")
                self._cleanup_audio_file(audio_path)
                print(f"✅ WHISPER: Cleanup completed")
                
        except Exception as e:
            logger.error(f"Error generating transcript for {video_url}: {e}")
            
            # Update accuracy metrics for failure
            self._update_accuracy_metrics(success=False)
            return None
    
    def _extract_video_info(self, video_url: str) -> Optional[Dict]:
        """Extract basic video information"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                return {
                    'id': info.get('id'),
                    'title': info.get('title'),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'url': video_url
                }
                
        except Exception as e:
            logger.error(f"Error extracting video info: {e}")
            return None
    
    def _download_audio(self, video_url: str) -> Optional[str]:
        """Download audio from video URL"""
        try:
            # Create temporary directory for audio file
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, "audio.%(ext)s")
            
            print(f"   📁 Temporary directory: {temp_dir}")
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': audio_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            print(f"   🔄 Downloading audio stream...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            # Find the downloaded file
            audio_files = list(Path(temp_dir).glob("audio.*"))
            if audio_files:
                file_size = os.path.getsize(str(audio_files[0])) / (1024*1024)  # Size in MB
                print(f"   📦 Audio file: {audio_files[0].name} ({file_size:.1f} MB)")
                return str(audio_files[0])
            else:
                print(f"   ❌ No audio file found after download")
                logger.error("No audio file downloaded")
                return None
                
        except Exception as e:
            print(f"   ❌ Audio download failed: {e}")
            logger.error(f"Error downloading audio: {e}")
            return None
    
    def _transcribe_audio(self, audio_path: str) -> List[Dict]:
        """Transcribe audio file using Whisper"""
        try:
            file_size = os.path.getsize(audio_path) / (1024*1024)  # Size in MB
            print(f"   🔍 Processing audio file ({file_size:.1f} MB)")
            print(f"   🧠 Using {self.model_size} model for transcription")
            
            start_time = time.time()
            
            # Transcribe with timestamps
            print(f"   🎯 Running Whisper AI transcription...")
            result = self.model.transcribe(
                audio_path,
                verbose=True,
                word_timestamps=True,
                language='en'  # You can make this configurable
            )
            
            transcription_time = time.time() - start_time
            
            # Convert Whisper result to our format
            segments = []
            
            if 'segments' in result:
                for segment in result['segments']:
                    segments.append({
                        'start': segment['start'],
                        'end': segment['end'],
                        'text': segment['text'].strip()
                    })
            
            print(f"   ✅ Transcription completed in {transcription_time:.1f}s")
            print(f"   📄 Generated {len(segments)} text segments")
            
            if segments:
                # Show sample of first segment
                first_segment = segments[0]
                print(f"   💬 Sample text: '{first_segment['text'][:60]}...'")
            
            logger.info(f"Transcription completed: {len(segments)} segments")
            return segments
            
        except Exception as e:
            print(f"   ❌ Transcription failed: {e}")
            logger.error(f"Error transcribing audio: {e}")
            return []
    
    def _cleanup_audio_file(self, audio_path: str):
        """Clean up downloaded audio file"""
        try:
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                # Remove parent directory if it's empty
                parent_dir = os.path.dirname(audio_path)
                if os.path.exists(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                logger.info(f"Cleaned up audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Failed to clean up audio file {audio_path}: {e}")
    
    def _update_accuracy_metrics(self, success: bool, processing_time: float = 0.0, audio_duration: float = 0.0):
        """Update accuracy metrics"""
        self.accuracy_metrics['total_videos_processed'] += 1
        
        if success:
            self.accuracy_metrics['successful_generations'] += 1
            self.accuracy_metrics['average_processing_time'] = (
                (self.accuracy_metrics['average_processing_time'] * 
                 (self.accuracy_metrics['successful_generations'] - 1) + processing_time) /
                self.accuracy_metrics['successful_generations']
            )
            self.accuracy_metrics['total_audio_duration_processed'] += audio_duration
        else:
            self.accuracy_metrics['failed_generations'] += 1
    
    def get_accuracy_metrics(self) -> Dict:
        """Get current accuracy metrics"""
        metrics = self.accuracy_metrics.copy()
        
        # Calculate success rate
        if metrics['total_videos_processed'] > 0:
            metrics['success_rate'] = (
                metrics['successful_generations'] / metrics['total_videos_processed']
            ) * 100
        else:
            metrics['success_rate'] = 0.0
        
        # Calculate average processing time per minute of audio
        if metrics['total_audio_duration_processed'] > 0:
            metrics['average_processing_time_per_minute'] = (
                metrics['average_processing_time'] / (metrics['total_audio_duration_processed'] / 60)
            )
        else:
            metrics['average_processing_time_per_minute'] = 0.0
        
        return metrics
    
    def reset_metrics(self):
        """Reset accuracy metrics"""
        self.accuracy_metrics = {
            'total_videos_processed': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_processing_time': 0.0,
            'total_audio_duration_processed': 0.0
        }
        logger.info("Accuracy metrics reset")


# Global instance for use throughout the application
_whisper_service = None

def get_whisper_service() -> WhisperService:
    """Get or create global Whisper service instance"""
    global _whisper_service
    if _whisper_service is None:
        try:
            _whisper_service = WhisperService(
                model_size=WHISPER_MODEL_SIZE,
                device="cpu"  # Can be made configurable
            )
        except Exception as e:
            logger.error(f"Failed to initialize Whisper service: {e}")
            _whisper_service = None
    
    return _whisper_service