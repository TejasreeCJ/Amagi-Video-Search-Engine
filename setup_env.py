"""
Setup script to create .env file
"""
import os

def create_env_file():
    env_content = """# Gemini API Key (Get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Neo4j Configuration (Get from https://neo4j.com/cloud/platform/aura-graph-database/)
# For AuraDB, use the URI format: neo4j+s://<your-instance-id>.databases.neo4j.io
NEO4J_URI=neo4j+s://your-instance-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password-here

WHISPER_ENABLED=true
WHISPER_MODEL_SIZE=tiny
WHISPER_LANGUAGE=en
"""
    
    env_path = '.env'
    
    if os.path.exists(env_path):
        response = input(".env file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f".env file created at {env_path}")
    print("\nPlease edit .env and add your API keys:")
    print("1. GEMINI_API_KEY: Get from https://makersuite.google.com/app/apikey")
    print("2. NEO4J_URI, USER, PASSWORD: Create a free instance at https://neo4j.com/cloud/platform/aura-graph-database/")

if __name__ == "__main__":
    create_env_file()

