
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to: {uri}")
print(f"User: {user}")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("Connection successful!")
    
    with driver.session() as session:
        result = session.run("RETURN 1 as n")
        print(f"Query result: {result.single()['n']}")
        
    driver.close()
except Exception as e:
    print(f"Connection failed: {e}")
    
    if "neo4j://" in uri:
        print("\nTrying with bolt:// scheme...")
        bolt_uri = uri.replace("neo4j://", "bolt://")
        try:
            driver = GraphDatabase.driver(bolt_uri, auth=(user, password))
            driver.verify_connectivity()
            print(f"Connection successful with {bolt_uri}!")
            driver.close()
        except Exception as e2:
            print(f"Connection failed with bolt://: {e2}")
