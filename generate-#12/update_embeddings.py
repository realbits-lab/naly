#!/usr/bin/env python3
"""
Update Embeddings for ECMA-376 Sections
Regenerates embeddings for sections that have updated descriptions
"""

import json
import logging
import psycopg2
from sentence_transformers import SentenceTransformer
from database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_embeddings_for_sections():
    """Update embeddings for all level 5 sections with descriptions"""
    
    logger.info("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Model loaded successfully!")
    
    db = DatabaseManager()
    
    with psycopg2.connect(**db.db_config) as conn:
        with conn.cursor() as cur:
            # Get all level 5 sections with descriptions
            cur.execute('''
                SELECT id, full_section_number, title, description
                FROM ecma_sections 
                WHERE depth = 5 AND description IS NOT NULL AND LENGTH(description) > 10
                ORDER BY full_section_number
            ''')
            
            sections = cur.fetchall()
            logger.info(f"Found {len(sections)} level 5 sections to update embeddings")
            
            updated_count = 0
            batch_size = 10
            
            # Process in batches for efficiency
            for i in range(0, len(sections), batch_size):
                batch = sections[i:i + batch_size]
                
                # Prepare texts for embedding generation
                texts = []
                section_ids = []
                
                for section_id, section_number, title, description in batch:
                    # Combine title and description for embedding
                    combined_text = f"{title}. {description}"
                    texts.append(combined_text)
                    section_ids.append(section_id)
                
                # Generate embeddings for the batch
                logger.info(f"Generating embeddings for batch {i//batch_size + 1}/{(len(sections)-1)//batch_size + 1}")
                embeddings = model.encode(texts)
                
                # Update database with new embeddings
                for j, (section_id, embedding) in enumerate(zip(section_ids, embeddings)):
                    embedding_json = json.dumps(embedding.tolist())
                    
                    cur.execute('''
                        UPDATE ecma_sections 
                        SET embedding_vector = %s
                        WHERE id = %s
                    ''', (embedding_json, section_id))
                    
                    updated_count += 1
                    
                    # Log progress for every 10 updates
                    if updated_count % 10 == 0:
                        logger.info(f"Updated embeddings for {updated_count}/{len(sections)} sections")
                
                conn.commit()
            
            logger.info(f"✅ Successfully updated embeddings for {updated_count} level 5 sections")
            
            # Update statistics
            cur.execute('''
                SELECT COUNT(*) as total_with_embeddings
                FROM ecma_sections 
                WHERE embedding_vector IS NOT NULL
            ''')
            
            total_with_embeddings = cur.fetchone()[0]
            logger.info(f"Total sections with embeddings: {total_with_embeddings}")

def test_semantic_search():
    """Test semantic search with updated embeddings"""
    logger.info("Testing semantic search with updated embeddings...")
    
    db = DatabaseManager()
    
    test_queries = [
        "alpha transparency",
        "blue color modulation", 
        "chart animation build",
        "accent color theme",
        "font properties"
    ]
    
    for query in test_queries:
        logger.info(f"Searching for: '{query}'")
        try:
            results = db.search_sections(query, limit=3)
            if results:
                for i, result in enumerate(results, 1):
                    logger.info(f"  {i}. [{result['similarity']:.3f}] {result['full_section_number']} - {result['title']}")
            else:
                logger.info(f"  No results found for '{query}'")
        except Exception as e:
            logger.error(f"  Error searching for '{query}': {e}")

if __name__ == "__main__":
    update_embeddings_for_sections()
    test_semantic_search()