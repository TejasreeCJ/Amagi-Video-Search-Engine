"""
Test script to verify setup and dependencies
"""
import sys
import importlib

def test_imports():
    """Test if all required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'dotenv',
        'yt_dlp',
        'sentence_transformers',
        'pydantic',
        'numpy',
        'requests',
        'neo4j',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle package name differences
            if package == 'dotenv':
                importlib.import_module('dotenv')
            elif package == 'yt_dlp':
                importlib.import_module('yt_dlp')
            elif package == 'sentence_transformers':
                importlib.import_module('sentence_transformers')
            else:
                importlib.import_module(package)
            print(f"✓ {package} is installed")
        except ImportError as e:
            print(f"✗ {package} is NOT installed")
            missing_packages.append(package)
        except Exception as e:
            print(f"✗ {package} error: {e}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Install them using: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All required packages are installed!")
        return True

def test_env_file():
    """Test if .env file exists and has required variables"""
    import os
    from pathlib import Path
    
    env_path = Path('.env')
    if not env_path.exists():
        print("\n✗ .env file not found")
        print("Create it using: python setup_env.py")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['NEO4J_URI', 'NEO4J_USER', 'NEO4J_PASSWORD', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or 'your_' in value:
            print(f"✗ {var} is not set in .env file")
            missing_vars.append(var)
        else:
            print(f"✓ {var} is set")
    
    if missing_vars:
        print(f"\nMissing environment variables: {', '.join(missing_vars)}")
        print("Update your .env file with the correct values")
        return False
    else:
        print("\n✓ All required environment variables are set!")
        return True

def test_neo4j_connection():
    """Test Neo4j connection"""
    try:
        from backend.neo4j_service import Neo4jService
        print(f"\nTesting Neo4j connection...")
        neo4j = Neo4jService()
        neo4j.close()
        print(f"✓ Connected to Neo4j")
        return True
    except Exception as e:
        print(f"\n✗ Neo4j connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Testing NPTEL Video Search Engine Setup")
    print("=" * 50)
    
    print("\n1. Testing Python packages...")
    packages_ok = test_imports()
    
    print("\n2. Testing environment configuration...")
    env_ok = test_env_file()
    
    if packages_ok and env_ok:
        print("\n3. Testing Neo4j connection...")
        neo4j_ok = test_neo4j_connection()
        
        if packages_ok and env_ok and neo4j_ok:
            print("\n" + "=" * 50)
            print("✓ All tests passed! Setup is complete.")
            print("=" * 50)
            print("\nYou can now run the server using:")
            print("  python run_server.py")
            sys.exit(0)
        else:
            print("\n" + "=" * 50)
            print("✗ Some tests failed. Please fix the issues above.")
            print("=" * 50)
            sys.exit(1)
    else:
        print("\n" + "=" * 50)
        print("✗ Setup incomplete. Please fix the issues above.")
        print("=" * 50)
        sys.exit(1)

