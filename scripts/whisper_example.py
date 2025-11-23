#!/usr/bin/env python3
"""
Example script demonstrating Whisper transcript generation functionality
"""
import sys
import os
import json

# Add the parent directory to the path so we can import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.whisper_service import get_whisper_service
    from backend.config import WHISPER_ENABLED
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure you're running this from the correct directory")
    sys.exit(1)

def main():
    print("Whisper Transcript Generation Example")
    print("=" * 50)
    
    # Check if Whisper is enabled
    if not WHISPER_ENABLED:
        print("⚠ Whisper is disabled in configuration")
        print("  To enable: set WHISPER_ENABLED=true in your .env file")
        print("  Then install dependencies: pip install openai-whisper torch torchaudio")
        return
    
    # Test video URL (should not have transcripts for proper testing)
    test_video_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Me at the zoo (first YouTube video)
    
    try:
        # Get Whisper service
        print("Initializing Whisper service...")
        whisper_service = get_whisper_service()
        
        if not whisper_service:
            print("✗ Failed to initialize Whisper service")
            return
        
        print("✓ Whisper service initialized successfully")
        print(f"  Model: {whisper_service.model_size}")
        print(f"  Device: {whisper_service.device}")
        
        # Generate transcript
        print(f"\nGenerating transcript for: {test_video_url}")
        print("This may take a few minutes...")
        
        result = whisper_service.generate_transcript_for_video(test_video_url)
        
        if result:
            print("\n✓ Transcript generated successfully!")
            print(f"  Video Title: {result.get('title', 'Unknown')}")
            print(f"  Duration: {result.get('duration', 0)} seconds")
            print(f"  Segments: {len(result.get('transcript', []))}")
            print(f"  Source: {result.get('transcript_source', 'unknown')}")
            print(f"  Model Used: {result.get('model_used', 'unknown')}")
            print(f"  Generation Time: {result.get('generation_time', 0):.2f} seconds")
            
            # Show first few segments
            transcript = result.get('transcript', [])
            if transcript:
                print(f"\nFirst 3 transcript segments:")
                for i, segment in enumerate(transcript[:3], 1):
                    print(f"  {i}. [{segment['start']:.1f}s - {segment['end']:.1f}s] {segment['text'][:80]}...")
            
            # Show accuracy metrics
            print(f"\nAccuracy Metrics:")
            metrics = whisper_service.get_accuracy_metrics()
            print(json.dumps(metrics, indent=2))
            
        else:
            print("✗ Failed to generate transcript")
    
    except KeyboardInterrupt:
        print("\n⚠ Generation cancelled by user")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()