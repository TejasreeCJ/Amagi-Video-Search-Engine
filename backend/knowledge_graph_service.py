
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import numpy as np
from scipy.spatial.distance import cosine
import os

class KnowledgeGraphService:
    def __init__(self, neo4j_driver=None):
        if neo4j_driver:
            self.driver = neo4j_driver
        else:
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if hasattr(self, 'driver'):
            self.driver.close()

    def build_knowledge_graph(self, similarity_threshold: float = 0.75, max_connections: int = 3):
        """
        Build knowledge graph by creating relationships between chapters based on:
        1. Semantic similarity (SIMILAR_TO)
        2. Temporal ordering within videos (NEXT_TOPIC)
        3. Cross-video concept bridges (RELATES_TO)
        """
        with self.driver.session() as session:
            # Step 1: Create NEXT_TOPIC relationships within same video
            print("Creating NEXT_TOPIC relationships...")
            session.run("""
            MATCH (v:Video)-[:HAS_CHAPTER]->(c1:Chapter)
            MATCH (v)-[:HAS_CHAPTER]->(c2:Chapter)
            WHERE c1.start_time < c2.start_time
            WITH v, c1, c2
            ORDER BY c1.start_time, c2.start_time
            WITH c1, collect(c2)[0] as nextChapter
            WHERE nextChapter IS NOT NULL
            MERGE (c1)-[r:NEXT_TOPIC]->(nextChapter)
            SET r.type = 'sequential'
            """)

            # Step 2: Get all chapters with embeddings
            print("Fetching chapters for similarity analysis...")
            chapters = self._get_all_chapters(session)

            if len(chapters) < 2:
                print("Not enough chapters to build relationships.")
                return

            # Step 3: Compute similarities and create relationships
            print(f"Computing similarities for {len(chapters)} chapters...")
            relationships_created = self._create_similarity_relationships(
                session,
                chapters,
                similarity_threshold,
                max_connections
            )

            # Step 4: Identify prerequisite relationships using heuristics
            print("Identifying prerequisite relationships...")
            self._create_prerequisite_relationships(session)

            print(f"Knowledge graph built successfully!")
            print(f"  - {relationships_created} similarity-based relationships created")

    def _get_all_chapters(self, session) -> List[Dict]:
        """Fetch all chapters with their embeddings and metadata"""
        result = session.run("""
        MATCH (v:Video)-[:HAS_CHAPTER]->(c:Chapter)
        WHERE c.embedding IS NOT NULL
        RETURN id(c) as chapter_id,
               c.title as title,
               c.description as description,
               c.embedding as embedding,
               c.start_time as start_time,
               c.end_time as end_time,
               v.id as video_id,
               v.title as video_title
        ORDER BY v.id, c.start_time
        """)

        chapters = []
        for record in result:
            chapters.append({
                'chapter_id': record['chapter_id'],
                'title': record['title'],
                'description': record['description'],
                'embedding': record['embedding'],
                'start_time': record['start_time'],
                'end_time': record['end_time'],
                'video_id': record['video_id'],
                'video_title': record['video_title']
            })

        return chapters

    def _create_similarity_relationships(self, session, chapters: List[Dict],
                                        threshold: float, max_connections: int) -> int:
        """
        Create SIMILAR_TO and RELATES_TO relationships based on cosine similarity
        """
        relationships_created = 0

        # Compute similarity matrix
        for i, chapter1 in enumerate(chapters):
            similarities = []

            for j, chapter2 in enumerate(chapters):
                if i == j:
                    continue

                # Skip if same video (already have NEXT_TOPIC)
                if chapter1['video_id'] == chapter2['video_id']:
                    continue

                # Compute cosine similarity
                emb1 = np.array(chapter1['embedding'])
                emb2 = np.array(chapter2['embedding'])

                similarity = 1 - cosine(emb1, emb2)

                if similarity >= threshold:
                    similarities.append({
                        'chapter2_id': chapter2['chapter_id'],
                        'similarity': similarity
                    })

            # Sort by similarity and take top max_connections
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            top_similar = similarities[:max_connections]

            # Create relationships in Neo4j
            for sim in top_similar:
                # High similarity (>0.85) = SIMILAR_TO, else RELATES_TO
                rel_type = "SIMILAR_TO" if sim['similarity'] > 0.85 else "RELATES_TO"

                session.run(f"""
                MATCH (c1:Chapter), (c2:Chapter)
                WHERE id(c1) = $id1 AND id(c2) = $id2
                MERGE (c1)-[r:{rel_type}]->(c2)
                SET r.similarity = $similarity
                """, id1=chapter1['chapter_id'], id2=sim['chapter2_id'],
                     similarity=sim['similarity'])

                relationships_created += 1

            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(chapters)} chapters...")

        return relationships_created

    def _create_prerequisite_relationships(self, session):
        """
        Create PREREQUISITE_OF relationships using heuristics:
        - Earlier chapters in a playlist are often prerequisites for later ones
        - Chapters with high similarity where one appears earlier in the learning sequence
        """
        session.run("""
        MATCH (v:Video)-[:HAS_CHAPTER]->(c1:Chapter)
        MATCH (v)-[:HAS_CHAPTER]->(c2:Chapter)
        WHERE c1.start_time < c2.start_time
        WITH c1, c2, c1.start_time as t1, c2.start_time as t2
        WHERE (t2 - t1) > 600
        WITH c1, c2
        LIMIT 1000
        MATCH (c1)-[r:SIMILAR_TO|RELATES_TO]-(c2)
        WHERE r.similarity > 0.75
        MERGE (c1)-[p:PREREQUISITE_OF]->(c2)
        SET p.confidence = r.similarity
        """)

    def is_graph_built(self) -> bool:
        """Check if knowledge graph relationships exist"""
        with self.driver.session() as session:
            result = session.run("""
            MATCH ()-[r:SIMILAR_TO|RELATES_TO|PREREQUISITE_OF]->()
            RETURN count(r) as count
            LIMIT 1
            """)
            record = result.single()
            return record['count'] > 0 if record else False

    def get_knowledge_graph(self, video_id: Optional[str] = None,
                           limit: int = 100, auto_build: bool = False) -> Dict[str, Any]:
        """
        Get the knowledge graph structure for visualization
        Returns nodes and edges in a format suitable for D3.js/Vis.js

        If auto_build is True and graph hasn't been built, builds it automatically
        """
        # Auto-build if requested and not already built
        if auto_build and not self.is_graph_built():
            print("Knowledge graph not built yet. Building automatically...")
            self.build_knowledge_graph()

        with self.driver.session() as session:
            # Build the query based on whether video_id is provided
            if video_id:
                # Get graph for specific video and its related chapters
                query = """
                MATCH (v:Video {id: $video_id})-[:HAS_CHAPTER]->(c:Chapter)
                OPTIONAL MATCH (c)-[r:SIMILAR_TO|RELATES_TO|NEXT_TOPIC|PREREQUISITE_OF]-(c2:Chapter)
                RETURN c, r, c2
                LIMIT $limit
                """
                params = {'video_id': video_id, 'limit': limit}
            else:
                # Get entire knowledge graph - get chapters first, then relationships
                query = """
                MATCH (v:Video)-[:HAS_CHAPTER]->(c:Chapter)
                WITH c, v
                ORDER BY v.id, c.start_time
                LIMIT $limit
                OPTIONAL MATCH (c)-[r:SIMILAR_TO|RELATES_TO|NEXT_TOPIC|PREREQUISITE_OF]-(c2:Chapter)
                OPTIONAL MATCH (v2:Video)-[:HAS_CHAPTER]->(c2)
                OPTIONAL MATCH (v_orig:Video)-[:HAS_CHAPTER]->(c)
                RETURN c, r, c2, v_orig as v, v2
                """
                params = {'limit': limit}

            result = session.run(query, params)

            # Process results into nodes and edges
            nodes_dict = {}
            edges = []

            for record in result:
                c1 = record['c']
                r = record.get('r')
                c2 = record.get('c2')
                v1 = record.get('v')
                v2 = record.get('v2')

                # Add first chapter as node
                c1_id = c1.element_id
                if c1_id not in nodes_dict:
                    nodes_dict[c1_id] = {
                        'id': c1_id,
                        'label': c1['title'],
                        'title': c1['title'],
                        'description': c1['description'],
                        'start_time': c1['start_time'],
                        'end_time': c1['end_time'],
                        'video_id': v1['id'] if v1 else None,
                        'video_url': v1['url'] if v1 else None,
                        'video_title': v1['title'] if v1 else None
                    }

                # Add relationship and second chapter if exists
                if r and c2:
                    c2_id = c2.element_id
                    if c2_id not in nodes_dict:
                        nodes_dict[c2_id] = {
                            'id': c2_id,
                            'label': c2['title'],
                            'title': c2['title'],
                            'description': c2['description'],
                            'start_time': c2['start_time'],
                            'end_time': c2['end_time'],
                            'video_id': v2['id'] if v2 else None,
                            'video_url': v2['url'] if v2 else None,
                            'video_title': v2['title'] if v2 else None
                        }

                    # Add edge - get similarity from relationship properties
                    similarity = r.get('similarity', 0.0)
                    edges.append({
                        'from': c1_id,
                        'to': c2_id,
                        'type': r.type,
                        'similarity': float(similarity) if similarity else 0.0
                    })

            nodes = list(nodes_dict.values())

            # Add cluster information using community detection (simplified - by video)
            nodes = self._add_cluster_info(session, nodes)

            return {
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'total_nodes': len(nodes),
                    'total_edges': len(edges)
                }
            }

    def _add_cluster_info(self, session, nodes: List[Dict]) -> List[Dict]:
        """Add cluster/community information to nodes"""
        # Get video grouping for each chapter
        result = session.run("""
        MATCH (v:Video)-[:HAS_CHAPTER]->(c:Chapter)
        RETURN id(c) as chapter_id, v.id as video_id, v.title as video_title
        """)

        video_map = {}
        for record in result:
            video_map[record['chapter_id']] = {
                'video_id': record['video_id'],
                'video_title': record['video_title']
            }

        # Assign cluster based on video
        video_to_cluster = {}
        cluster_id = 0

        for node in nodes:
            # Try to get video info (node id might be element_id)
            chapter_id = node['id']

            # We need to map back - for now use a simple heuristic
            # In production, you'd want to include video_id in the node data
            node['group'] = 0  # Default cluster

        return nodes

    def get_learning_path(self, target_chapter_id: str,
                         start_chapter_id: Optional[str] = None) -> List[Dict]:
        """
        Get optimal learning path to reach target chapter.
        Uses shortest path algorithm considering PREREQUISITE_OF and SIMILAR_TO relationships.
        """
        with self.driver.session() as session:
            if start_chapter_id:
                # Find path from start to target
                query = """
                MATCH (start:Chapter), (target:Chapter)
                WHERE elementId(start) = $start_id AND elementId(target) = $target_id
                MATCH path = shortestPath((start)-[r:PREREQUISITE_OF|SIMILAR_TO|NEXT_TOPIC*..10]-(target))
                RETURN [node in nodes(path) | {
                    id: elementId(node),
                    title: node.title,
                    description: node.description,
                    start_time: node.start_time,
                    end_time: node.end_time
                }] as path_nodes,
                [rel in relationships(path) | type(rel)] as path_types
                """
                params = {'start_id': start_chapter_id, 'target_id': target_chapter_id}
            else:
                # Find prerequisites leading to target
                query = """
                MATCH (target:Chapter)
                WHERE elementId(target) = $target_id
                OPTIONAL MATCH path = (prereq:Chapter)-[:PREREQUISITE_OF*..5]->(target)
                WITH target, collect(distinct prereq) as prerequisites
                WITH target,
                     [node in prerequisites | {
                         id: elementId(node),
                         title: node.title,
                         description: node.description,
                         start_time: node.start_time,
                         end_time: node.end_time
                     }] as prereq_list
                RETURN prereq_list + [{
                    id: elementId(target),
                    title: target.title,
                    description: target.description,
                    start_time: target.start_time,
                    end_time: target.end_time
                }] as path_nodes
                """
                params = {'target_id': target_chapter_id}

            result = session.run(query, params)
            record = result.single()

            if record and record['path_nodes']:
                path_nodes = record['path_nodes']
                return path_nodes if isinstance(path_nodes, list) else []

            return []

    def get_all_videos(self) -> List[Dict[str, str]]:
        """Get list of all videos in the database"""
        with self.driver.session() as session:
            result = session.run("""
            MATCH (v:Video)
            RETURN v.id as id, v.title as title
            ORDER BY v.title
            """)
            return [{'id': record['id'], 'title': record['title']} for record in result]

    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        with self.driver.session() as session:
            stats = {}

            # Total chapters
            result = session.run("MATCH (c:Chapter) RETURN count(c) as count")
            stats['total_chapters'] = result.single()['count']

            # Total videos
            result = session.run("MATCH (v:Video) RETURN count(v) as count")
            stats['total_videos'] = result.single()['count']

            # Relationship counts by type
            result = session.run("""
            MATCH ()-[r]->()
            RETURN type(r) as rel_type, count(r) as count
            """)
            stats['relationships'] = {record['rel_type']: record['count'] for record in result}

            # Average connections per chapter
            result = session.run("""
            MATCH (c:Chapter)
            OPTIONAL MATCH (c)-[r:SIMILAR_TO|RELATES_TO]->()
            WITH c, count(r) as connections
            RETURN avg(connections) as avg_connections
            """)
            stats['avg_connections'] = result.single()['avg_connections'] or 0

            return stats
