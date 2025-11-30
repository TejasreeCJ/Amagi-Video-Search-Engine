"""
Test script to verify Neo4j connection
"""
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

def test_neo4j_connection():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    print(f"Attempting to connect to: {uri}")
    print(f"User: {user}")
    print(f"Password: {'*' * len(password) if password else 'Not set'}")

    if not uri or not user or not password:
        print("❌ Missing Neo4j credentials in .env file")
        print("Make sure NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD are set")
        return False

    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 'Hello, Neo4j!' as message")
            record = result.single()
            print(f"✅ Connected to Neo4j: {record['message']}")
        driver.close()
        return True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Neo4j connection...")
    test_neo4j_connection()
