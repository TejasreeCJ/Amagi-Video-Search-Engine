
from neo4j import GraphDatabase
import os
from typing import List, Dict, Any

class Neo4jService:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self._create_constraints_and_indexes()

    def close(self):
        self.driver.close()

    def _create_constraints_and_indexes(self):
        with self.driver.session() as session:
            # Constraint for Video ID
            session.run("CREATE CONSTRAINT video_id_unique IF NOT EXISTS FOR (v:Video) REQUIRE v.id IS UNIQUE")
            
            # Vector Index for Chapter embeddings
            # Note: Syntax depends on Neo4j version. Assuming 5.x
            try:
                session.run("""
                CREATE VECTOR INDEX chapter_embeddings IF NOT EXISTS
                FOR (c:Chapter)
                ON (c.embedding)
                OPTIONS {indexConfig: {
                 `vector.dimensions`: 384,
                 `vector.similarity_function`: 'cosine'
                }}
                """)
            except Exception as e:
                print(f"Warning creating vector index: {e}")

            # Fulltext index for keyword search
            try:
                session.run("""
                CREATE FULLTEXT INDEX chapter_fulltext IF NOT EXISTS
                FOR (c:Chapter)
                ON EACH [c.title, c.description, c.transcript]
                """)
            except Exception as e:
                print(f"Warning creating fulltext index: {e}")

    def add_video_with_chapters(self, video_data: Dict, chapters: List[Dict], embeddings: List[List[float]]):
        with self.driver.session() as session:
            session.execute_write(self._create_video_graph, video_data, chapters, embeddings)

    def _create_video_graph(self, tx, video_data, chapters, embeddings):
        # Create Video Node
        tx.run("""
        MERGE (v:Video {id: $video_id})
        SET v.title = $title, v.url = $url
        """, video_id=video_data['video_id'], title=video_data['title'], url=video_data['url'])

        # Create Chapters and connect to Video
        for i, chapter in enumerate(chapters):
            embedding = embeddings[i]
            tx.run("""
            MATCH (v:Video {id: $video_id})
            CREATE (c:Chapter {
                title: $title,
                description: $description,
                start_time: $start,
                end_time: $end,
                transcript: $transcript,
                embedding: $embedding
            })
            CREATE (v)-[:HAS_CHAPTER]->(c)
            """, 
            video_id=video_data['video_id'],
            title=chapter['title'],
            description=chapter['description'],
            start=chapter['start'],
            end=chapter['end'],
            transcript=chapter.get('transcript_text', ''),
            embedding=embedding
            )

    def hybrid_search(self, query_text: str, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        with self.driver.session() as session:
            # Hybrid Search: Combine Vector Search and Fulltext Search
            # We use a subquery to perform both searches and then aggregate results
            results = session.run("""
            CALL {
                CALL db.index.vector.queryNodes('chapter_embeddings', $k, $embedding)
                YIELD node, score
                RETURN node, score as vectorScore, 0.0 as textScore
                UNION
                CALL db.index.fulltext.queryNodes('chapter_fulltext', $query_text)
                YIELD node, score
                RETURN node, 0.0 as vectorScore, score as textScore
            }
            WITH node, max(vectorScore) as vectorScore, max(textScore) as textScore
            // Normalize text score to [0, 1] range using x/(x+1)
            WITH node, vectorScore, textScore, (textScore / (textScore + 1.0)) as normalizedTextScore
            // Weighted sum: 80% Vector (Semantic), 20% Text (Keyword)
            WITH node, vectorScore, textScore, (vectorScore * 0.8) + (normalizedTextScore * 0.2) as finalScore
            ORDER BY finalScore DESC
            LIMIT $k
            MATCH (v:Video)-[:HAS_CHAPTER]->(node)
            RETURN v.title as video_title, v.url as video_url, 
                   node.title as chapter_title, node.description as chapter_description,
                   node.start_time as start, node.end_time as end,
                   finalScore as score
            """, k=top_k, embedding=query_embedding, query_text=query_text)
            
            # Add context buffer to center the relevant part
            buffer_seconds = 30
            processed_results = []
            
            for record in results:
                data = record.data()
                # Add buffer to start and end times
                data['start'] = max(0, data['start'] - buffer_seconds)
                data['end'] = data['end'] + buffer_seconds
                processed_results.append(data)
                
            return processed_results

    def get_related_videos(self, video_id: str) -> List[Dict]:
        """
        Suggest related videos based on shared concepts or similar chapters
        """
        with self.driver.session() as session:
            result = session.run("""
            MATCH (v1:Video {id: $video_id})-[:HAS_CHAPTER]->(c1:Chapter)
            MATCH (c1)-[r:SIMILAR_TO]-(c2:Chapter)<-[:HAS_CHAPTER]-(v2:Video)
            WHERE v1 <> v2
            RETURN v2.title as title, v2.id as id, count(r) as strength
            ORDER BY strength DESC
            LIMIT 5
            """, video_id=video_id)
            
            return [{'title': r['title'], 'id': r['id'], 'strength': r['strength']} for r in result]

