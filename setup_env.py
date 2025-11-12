"""
Setup script to create .env file
"""
import os

def create_env_file():
    env_content = """PINECONE_API_KEY=pcsk_2UHmn2_R99reTcQqpPpe5HXtNRXqvUdfPkivnpkWKai1pqLe2d4efJkC2XbWDjt41taMWr
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=semantic-search
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
    print("\nPlease edit .env and add your Pinecone API key:")
    print("1. Sign up at https://www.pinecone.io/")
    print("2. Create an index (dimension: 384, metric: cosine)")
    print("3. Copy your API key and environment")
    print("4. Update the .env file with your credentials")

if __name__ == "__main__":
    create_env_file()

