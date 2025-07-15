#!/usr/bin/env python3
"""
Database Manager for ECMA-376 Documentation
Handles embedding generation and database operations
"""

import json
import logging
import psycopg2
from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path

from ecma_parser import EcmaParser, Section

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database operations and embedding generation for ECMA-376 sections"""
    
    def __init__(self, db_name: str = "ecma376_docs", 
                 db_user: str = "thomasjeon", 
                 db_host: str = "localhost", 
                 db_port: int = 5432):
        """Initialize database connection and embedding model"""
        self.db_config = {
            'dbname': db_name,
            'user': db_user,
            'host': db_host,
            'port': db_port
        }
        
        # Initialize embedding model
        logger.info("Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully!")
        
        # Test database connection
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test database connection"""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT version();")
                    version = cur.fetchone()[0]
                    logger.info(f"Connected to PostgreSQL: {version}")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for given text"""
        if not text or not text.strip():
            # Return zero vector for empty text
            return [0.0] * 384  # all-MiniLM-L6-v2 has 384 dimensions
        
        # Combine title and description for better semantic representation
        embedding = self.embedding_model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
    
    def create_embedding_text(self, section: Section) -> str:
        """Create text for embedding generation by combining title and description"""
        parts = []
        
        if section.title:
            parts.append(section.title)
        
        if section.description:
            # Limit description length to avoid extremely long embeddings
            desc = section.description[:1000] if len(section.description) > 1000 else section.description
            parts.append(desc)
        
        return ". ".join(parts)
    
    def insert_sections(self, sections: List[Section]) -> None:
        """Insert sections into database with embeddings"""
        logger.info(f"Inserting {len(sections)} sections into database...")
        
        insert_query = """
        INSERT INTO ecma_sections (
            level1, level2, level3, level4, level5,
            full_section_number, title, description,
            page_reference, section_type, depth, 
            parent_id, embedding_vector
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s
        ) RETURNING id;
        """
        
        # Create a mapping of section numbers to database IDs for parent relationships
        section_id_map = {}
        
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    for i, section in enumerate(sections):
                        if i % 100 == 0:
                            logger.info(f"Processing section {i+1}/{len(sections)}")
                        
                        # Generate embedding
                        embedding_text = self.create_embedding_text(section)
                        embedding_vector = self.generate_embedding(embedding_text)
                        embedding_json = json.dumps(embedding_vector)
                        
                        # Find parent ID if exists
                        parent_id = None
                        if section.parent_section and section.parent_section in section_id_map:
                            parent_id = section_id_map[section.parent_section]
                        
                        # Insert section
                        cur.execute(insert_query, (
                            section.level1,
                            section.level2,
                            section.level3,
                            section.level4,
                            section.level5,
                            section.full_section_number,
                            section.title,
                            section.description,
                            section.page_reference,
                            section.section_type,
                            section.depth,
                            parent_id,
                            embedding_json
                        ))
                        
                        # Get the inserted ID and map it
                        section_id = cur.fetchone()[0]
                        section_id_map[section.full_section_number] = section_id
                    
                    conn.commit()
                    logger.info(f"Successfully inserted {len(sections)} sections!")
                    
        except Exception as e:
            logger.error(f"Error inserting sections: {e}")
            raise
    
    def search_sections(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search sections using semantic similarity"""
        logger.info(f"Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        query_embedding_json = json.dumps(query_embedding)
        
        # Use cosine similarity for semantic search
        search_query = """
        WITH query_embedding AS (
            SELECT %s::text as embedding_vector
        ),
        similarities AS (
            SELECT 
                s.id, s.full_section_number, s.title, s.description,
                s.level1, s.level2, s.level3, s.level4, s.level5,
                s.depth, s.section_type, s.page_reference,
                -- Calculate cosine similarity
                (
                    SELECT SUM(a.value * b.value) / 
                    (SQRT(SUM(a.value * a.value)) * SQRT(SUM(b.value * b.value)))
                    FROM (
                        SELECT unnest(
                            ARRAY(SELECT json_array_elements_text(s.embedding_vector::json))::float[]
                        ) as value
                    ) a,
                    (
                        SELECT unnest(
                            ARRAY(SELECT json_array_elements_text(q.embedding_vector::json))::float[]
                        ) as value
                        FROM query_embedding q
                    ) b
                ) AS similarity
            FROM ecma_sections s
            CROSS JOIN query_embedding q
            WHERE s.embedding_vector IS NOT NULL
        )
        SELECT * FROM similarities
        WHERE similarity > 0.3  -- Minimum similarity threshold
        ORDER BY similarity DESC
        LIMIT %s;
        """
        
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute(search_query, (query_embedding_json, limit))
                    results = cur.fetchall()
                    
                    # Convert to dictionaries
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in results]
                    
        except Exception as e:
            logger.error(f"Error searching sections: {e}")
            raise
    
    def get_section_hierarchy(self, section_number: str) -> List[Dict[str, Any]]:
        """Get the full hierarchy path for a section"""
        query = """
        SELECT * FROM get_section_path(
            (SELECT id FROM ecma_sections WHERE full_section_number = %s)
        );
        """
        
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (section_number,))
                    results = cur.fetchall()
                    
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in results]
                    
        except Exception as e:
            logger.error(f"Error getting section hierarchy: {e}")
            raise
    
    def get_section_children(self, section_number: str) -> List[Dict[str, Any]]:
        """Get all children of a section"""
        query = """
        SELECT * FROM get_section_children(
            (SELECT id FROM ecma_sections WHERE full_section_number = %s)
        );
        """
        
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (section_number,))
                    results = cur.fetchall()
                    
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in results]
                    
        except Exception as e:
            logger.error(f"Error getting section children: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        stats_query = """
        SELECT 
            COUNT(*) as total_sections,
            COUNT(DISTINCT level1) as level1_count,
            COUNT(DISTINCT level2) as level2_count,
            COUNT(DISTINCT level3) as level3_count,
            COUNT(DISTINCT level4) as level4_count,
            COUNT(DISTINCT level5) as level5_count,
            COUNT(CASE WHEN embedding_vector IS NOT NULL THEN 1 END) as sections_with_embeddings
        FROM ecma_sections;
        """
        
        depth_query = """
        SELECT depth, COUNT(*) as count
        FROM ecma_sections
        GROUP BY depth
        ORDER BY depth;
        """
        
        type_query = """
        SELECT section_type, COUNT(*) as count
        FROM ecma_sections
        GROUP BY section_type
        ORDER BY count DESC;
        """
        
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    # Get general stats
                    cur.execute(stats_query)
                    stats = dict(zip([desc[0] for desc in cur.description], cur.fetchone()))
                    
                    # Get depth distribution
                    cur.execute(depth_query)
                    depth_dist = {row[0]: row[1] for row in cur.fetchall()}
                    
                    # Get type distribution
                    cur.execute(type_query)
                    type_dist = {row[0]: row[1] for row in cur.fetchall()}
                    
                    return {
                        'general': stats,
                        'depth_distribution': depth_dist,
                        'type_distribution': type_dist
                    }
                    
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise

def main():
    """Main function for testing database operations"""
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Parse the markdown file
    parser = EcmaParser('ecma-376.md')
    sections = parser.parse_file()
    
    # Insert sections into database
    db_manager.insert_sections(sections)
    
    # Print statistics
    stats = db_manager.get_statistics()
    print(f"\n=== Database Statistics ===")
    print(f"Total sections: {stats['general']['total_sections']}")
    print(f"Sections with embeddings: {stats['general']['sections_with_embeddings']}")
    
    print(f"\nDepth distribution:")
    for depth, count in stats['depth_distribution'].items():
        print(f"  Level {depth}: {count}")
    
    print(f"\nType distribution:")
    for section_type, count in stats['type_distribution'].items():
        print(f"  {section_type}: {count}")
    
    # Test search functionality
    print(f"\n=== Testing Search ===")
    search_results = db_manager.search_sections("drawing chart", limit=5)
    for result in search_results:
        print(f"Score: {result['similarity']:.3f} | {result['full_section_number']} - {result['title']}")

if __name__ == "__main__":
    main()