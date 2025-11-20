"""
Quick test script for knowledge graph feature
"""
import sys
from backend.knowledge_graph_service import KnowledgeGraphService

def test_knowledge_graph():
    print("Testing Knowledge Graph Service...")
    print("-" * 50)
    
    # Initialize service
    try:
        kg_service = KnowledgeGraphService()
        print("✓ Knowledge Graph Service initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize service: {e}")
        return False
    
    # Test with a sample video URL
    # You can replace this with any educational YouTube video URL that has captions
    test_video_url = "https://www.youtube.com/watch?v=kCc8FmEb1nY"  # Sample video
    
    print(f"\nTesting with video: {test_video_url}")
    print("Note: This video must have captions/transcripts enabled")
    print("Processing... (this may take 10-30 seconds)")
    
    try:
        graph_data = kg_service.generate_knowledge_graph(test_video_url, min_clip_duration=20.0)
        
        print("\n✓ Knowledge graph generated successfully!")
        print("\nGraph Statistics:")
        print(f"  - Total clips (nodes): {len(graph_data['nodes'])}")
        print(f"  - Total connections (edges): {len(graph_data['edges'])}")
        print(f"  - Video title: {graph_data['video_info']['title']}")
        print(f"  - Video duration: {graph_data['video_info']['duration']} seconds")
        
        # Show first few clips
        print("\nFirst 3 clips:")
        for i, node in enumerate(graph_data['nodes'][:3]):
            print(f"\n  Clip {i+1}: {node['label']}")
            print(f"    Time: {node['start_time']:.1f}s - {node['end_time']:.1f}s")
            print(f"    Topics: {', '.join(node['topics'][:3])}")
        
        # Show edge types
        sequential_edges = sum(1 for e in graph_data['edges'] if e['type'] == 'sequential')
        related_edges = sum(1 for e in graph_data['edges'] if e['type'] == 'related')
        
        print(f"\nEdge types:")
        print(f"  - Sequential (temporal flow): {sequential_edges}")
        print(f"  - Related (topic similarity): {related_edges}")
        
        print("\n" + "=" * 50)
        print("✓ All tests passed! Knowledge graph feature is working.")
        return True
        
    except ValueError as e:
        print(f"\n✗ ValueError: {e}")
        print("\nPossible reasons:")
        print("  - Video doesn't have captions/transcripts")
        print("  - Invalid video URL")
        print("  - Video is private or unavailable")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Knowledge Graph Feature Test")
    print("=" * 50)
    
    success = test_knowledge_graph()
    
    if success:
        print("\n✓ Knowledge graph feature is ready to use!")
        print("\nTo use the feature:")
        print("  1. Start the backend server: python run_server.py")
        print("  2. Open frontend/index.html in your browser")
        print("  3. Find the 'Knowledge Graph Mind Map' section")
        print("  4. Enter a YouTube video URL with captions")
        print("  5. Click 'Generate Mind Map'")
    else:
        print("\n✗ Knowledge graph feature needs attention")
        print("\nMake sure:")
        print("  - All dependencies are installed (spacy, scikit-learn, etc.)")
        print("  - Test with a video that has captions enabled")
        sys.exit(1)
