
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import traceback

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

print(f"Connecting to {uri}...")

try:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print("Connection successful.")
    
    with driver.session() as session:
        # 1. Check Indexes
        print("\nChecking indexes...")
        result = session.run("SHOW INDEXES")
        indexes = [record['name'] for record in result]
        print(f"Found indexes: {indexes}")
        
        if 'chapter_embeddings' not in indexes:
            print("ERROR: 'chapter_embeddings' index is missing!")
        if 'chapter_fulltext' not in indexes:
            print("ERROR: 'chapter_fulltext' index is missing!")

        # 2. Test Hybrid Search Query
        print("\nTesting Hybrid Search Query...")
        query_text = "test"
        # Dummy 384-dim embedding
        query_embedding = [0.1] * 384 
        top_k = 5
        
        cypher_query = """
            CALL {
                CALL db.index.vector.queryNodes('chapter_embeddings', $k, $embedding)
                YIELD node, score
                RETURN node, score as vectorScore, 0.0 as textScore
                UNION
                CALL db.index.fulltext.queryNodes('chapter_fulltext', $query)
                YIELD node, score
                RETURN node, 0.0 as vectorScore, score as textScore
            }
            WITH node, max(vectorScore) as vectorScore, max(textScore) as textScore
            WITH node, vectorScore, textScore, (vectorScore + textScore) as finalScore
            ORDER BY finalScore DESC
            LIMIT $k
            MATCH (v:Video)-[:HAS_CHAPTER]->(node)
            RETURN v.title as video_title, finalScore as score
        """
        
        try:
            result = session.run(cypher_query, k=top_k, embedding=query_embedding, query=query_text)
            records = list(result)
            print(f"Query successful! Found {len(records)} results.")
        except Exception as e:
            print(f"Query failed!")
            print(e)

    driver.close()

except Exception as e:
    print(f"Connection failed: {e}")
    traceback.print_exc()
