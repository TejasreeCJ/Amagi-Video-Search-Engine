from backend.llm_service import LLMService
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_llm():
    print("Initializing LLM Service...")
    try:
        llm = LLMService()
        print("LLM Service initialized.")
        
        import google.generativeai as genai
        print("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
                
    except Exception as e:
        print(f"Failed to initialize LLM Service: {e}")
        return

    # Dummy transcript
    transcript = [
        {'start': 0.0, 'duration': 5.0, 'end': 5.0, 'text': "Hello and welcome to this lecture on Physics."},
        {'start': 5.0, 'duration': 5.0, 'end': 10.0, 'text': "Today we will discuss Newton's laws of motion."},
        {'start': 10.0, 'duration': 5.0, 'end': 15.0, 'text': "First law states that an object remains at rest or in uniform motion unless acted upon by a force."},
        {'start': 15.0, 'duration': 5.0, 'end': 20.0, 'text': "This is also known as the law of inertia."},
        {'start': 20.0, 'duration': 5.0, 'end': 25.0, 'text': "Let's look at some examples of inertia in daily life."},
    ]
    
    video_duration = 30.0
    
    print("\nTesting generate_chapters...")
    try:
        chapters = llm.generate_chapters(transcript, video_duration)
        print(f"\nGenerated {len(chapters)} chapters.")
        for i, chapter in enumerate(chapters):
            print(f"Chapter {i+1}: {chapter['title']} ({chapter['start']}s - {chapter['end']}s)")
            print(f"  Description: {chapter['description']}")
    except Exception as e:
        print(f"Error during generation: {e}")

if __name__ == "__main__":
    test_llm()
