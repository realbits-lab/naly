#!/usr/bin/env python3
"""
Repopulate database with correctly parsed ECMA-376 sections
"""

import psycopg2
from ecma_parser_fixed import EcmaParserFixed
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_database():
    """Clear existing data from the database"""
    logger.info("Clearing existing database data...")
    
    try:
        with psycopg2.connect(
            dbname="ecma376_docs",
            user="thomasjeon",
            host="localhost",
            port=5432
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ecma_sections;")
                cur.execute("ALTER SEQUENCE ecma_sections_id_seq RESTART WITH 1;")
                conn.commit()
                logger.info("Database cleared successfully!")
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        raise

def populate_database_with_fixed_data():
    """Populate database with correctly parsed sections"""
    logger.info("Parsing ECMA-376 with fixed parser...")
    
    # Parse the markdown file with the fixed parser
    parser = EcmaParserFixed('ecma-376.md')
    sections = parser.parse_file()
    
    logger.info(f"Parsed {len(sections)} sections")
    
    # Database connection
    db_config = {
        'dbname': 'ecma376_docs',
        'user': 'thomasjeon',
        'host': 'localhost',
        'port': 5432
    }
    
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
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cur:
                for i, section in enumerate(sections):
                    if i % 100 == 0:
                        logger.info(f"Processing section {i+1}/{len(sections)}")
                    
                    # Find parent ID if exists
                    parent_id = None
                    if section.parent_section and section.parent_section in section_id_map:
                        parent_id = section_id_map[section.parent_section]
                    
                    # Insert section (without embedding for now)
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
                        None  # No embedding for now
                    ))
                    
                    # Get the inserted ID and map it
                    section_id = cur.fetchone()[0]
                    section_id_map[section.full_section_number] = section_id
                
                conn.commit()
                logger.info(f"Successfully inserted {len(sections)} sections!")
                
    except Exception as e:
        logger.error(f"Error inserting sections: {e}")
        raise

def verify_bldchart_section():
    """Verify that the bldChart section is correctly stored"""
    logger.info("Verifying bldChart section...")
    
    try:
        with psycopg2.connect(
            dbname="ecma376_docs",
            user="thomasjeon",
            host="localhost",
            port=5432
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT full_section_number, title, description, section_type, depth
                    FROM ecma_sections 
                    WHERE full_section_number = '20.1.2.2.1'
                """)
                
                result = cur.fetchone()
                if result:
                    section_num, title, description, section_type, depth = result
                    logger.info(f"✅ Found bldChart section:")
                    logger.info(f"   Section: {section_num}")
                    logger.info(f"   Title: {title}")
                    logger.info(f"   Type: {section_type}")
                    logger.info(f"   Depth: {depth}")
                    logger.info(f"   Description: {description[:200]}...")
                    
                    # Verify the description starts correctly
                    if description.startswith("This element specifies how to build the animation"):
                        logger.info("✅ Description is correct!")
                    else:
                        logger.error("❌ Description is still incorrect!")
                else:
                    logger.error("❌ bldChart section not found!")
                    
    except Exception as e:
        logger.error(f"Error verifying section: {e}")
        raise

def main():
    """Main function to repopulate the database"""
    logger.info("🚀 Starting database repopulation with fixed parser...")
    
    try:
        # Step 1: Clear existing data
        clear_database()
        
        # Step 2: Populate with correctly parsed data
        populate_database_with_fixed_data()
        
        # Step 3: Verify the bldChart section
        verify_bldchart_section()
        
        logger.info("🎉 Database repopulation completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Repopulation failed: {e}")
        raise

if __name__ == "__main__":
    main()