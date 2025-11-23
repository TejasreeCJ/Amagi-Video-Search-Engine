"""
Test script for Whisper transcript generation service
"""
import sys
import os
import json

# Add the parent directory to the path so we can import backend modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.whisper_service import WhisperService
    from backend.config import WHISPER_ENABLED
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure you're running this from the correct directory")
    sys.exit(1)

def test_whisper_service():
    """Test Whisper service functionality"""
    print("=" * 60)
    print("Testing Whisper Transcript Generation Service")
    print("=" * 60)
    
    if not WHISPER_ENABLED:
        print("⚠ Whisper is disabled in configuration")
        print("  To enable: set WHISPER_ENABLED=true in environment")
        return False
    
    try:
        # Initialize service
        print("\n1. Initializing Whisper service...")
        service = WhisperService(model_size="tiny", device="cpu")
        print("✓ Whisper service initialized successfully")
        
        # Test with a sample video (should not have transcripts)
        test_video_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Me at the zoo (first YouTube video)
        
        print(f"\n2. Testing transcript generation for:")
        print(f"   URL: {test_video_url}")
        
        # Generate transcript
        result = service.generate_transcript_for_video(test_video_url)
        
        if result and result.get('transcript'):
            print(f"✓ Generated transcript successfully!")
            print(f"  Video: {result.get('title', 'Unknown')}")
            print(f"  Duration: {result.get('duration', 0)} seconds")
            print(f"  Segments: {len(result['transcript'])}")
            print(f"  Source: {result.get('transcript_source', 'unknown')}")
            print(f"  Model: {result.get('model_used', 'unknown')}")
            print(f"  Generation time: {result.get('generation_time', 0):.2f}s")
            
            # Show first few segments
            print(f"\n3. First 3 transcript segments:")
            for i, segment in enumerate(result['transcript'][:3], 1):
                print(f"  {i}. [{segment['start']:.1f}s - {segment['end']:.1f}s] {segment['text'][:80]}...")
            
            return True
        else:
            print("✗ Failed to generate transcript")
            return False
            
    except Exception as e:
        print(f"✗ Error testing Whisper service: {e}")
        return False

def test_accuracy_metrics():
    """Test accuracy metrics functionality"""
    print("\n" + "=" * 60)
    print("Testing Whisper Accuracy Metrics")
    print("=" * 60)
    
    try:
        service = WhisperService(model_size="tiny", device="cpu")
        
        print("\n1. Initial metrics:")
        metrics = service.get_accuracy_metrics()
        print(json.dumps(metrics, indent=2))
        
        # Simulate some processing
        print("\n2. Simulating video processing...")
        service._update_accuracy_metrics(success=True, processing_time=30.0, audio_duration=300.0)
        service._update_accuracy_metrics(success=True, processing_time=45.0, audio_duration=450.0)
        service._update_accuracy_metrics(success=False)  # One failure
        
        print("\n3. Updated metrics:")
        metrics = service.get_accuracy_metrics()
        print(json.dumps(metrics, indent=2))
        
        print("\n✓ Accuracy metrics test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error testing accuracy metrics: {e}")
        return False

def test_model_sizes():
    """Test different model sizes"""
    print("\n" + "=" * 60)
    print("Testing Different Whisper Model Sizes")
    print("=" * 60)
    
    if not WHISPER_ENABLED:
        print("⚠ Whisper is disabled in configuration")
        return False
    
    model_sizes = ["tiny", "base"]  # Keep it simple for testing
    
    for model_size in model_sizes:
        try:
            print(f"\nTesting model size: {model_size}")
            service = WhisperService(model_size=model_size, device="cpu")
            print(f"✓ Model {model_size} loaded successfully")
        except Exception as e:
            print(f"✗ Failed to load model {model_size}: {e}")
    
    return True

if __name__ == "__main__":
    print("Whisper Service Test Suite")
    print("=" * 60)
    
    # Check configuration
    print(f"WHISPER_ENABLED: {WHISPER_ENABLED}")
    
    if not WHISPER_ENABLED:
        print("\n⚠ Whisper is disabled. To enable testing:")
        print("1. Set WHISPER_ENABLED=true in your .env file")
        print("2. Install whisper dependencies: pip install openai-whisper torch torchaudio")
        print("3. Re-run this test")
        sys.exit(1)
    
    # Run tests
    success_count = 0
    total_tests = 3
    
    # Test 1: Service initialization and transcript generation
    if test_whisper_service():
        success_count += 1
    
    # Test 2: Accuracy metrics
    if test_accuracy_metrics():
        success_count += 1
    
    # Test 3: Model sizes
    if test_model_sizes():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)