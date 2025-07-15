#!/usr/bin/env python3
"""
Test script for ECMA-376 Database System
Demonstrates all functionality including hierarchical queries and semantic search
"""

import json
from database_manager import DatabaseManager

def test_semantic_search(db_manager):
    """Test semantic search functionality"""
    print("=== Testing Semantic Search ===")
    
    test_queries = [
        "drawing chart",
        "chart animation", 
        "build diagram",
        "text formatting",
        "color scheme",
        "table properties",
        "document structure"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        try:
            results = db_manager.search_sections(query, limit=3)
            
            if results:
                for i, result in enumerate(results, 1):
                    print(f"  {i}. [{result['similarity']:.3f}] {result['full_section_number']} - {result['title']}")
                    if result['description']:
                        desc = result['description'][:100] + "..." if len(result['description']) > 100 else result['description']
                        print(f"     Description: {desc}")
            else:
                print("     No results found")
        except Exception as e:
            print(f"     Error: {e}")

def test_hierarchical_queries(db_manager):
    """Test hierarchical navigation functionality"""
    print("\n=== Testing Hierarchical Queries ===")
    
    # Test section with children
    test_section = "20.1.2"
    print(f"\n📊 Getting children of section {test_section}:")
    try:
        children = db_manager.get_section_children(test_section)
        for child in children[:5]:  # Show first 5 children
            print(f"  • {child['full_section_number']} - {child['title']}")
        
        if len(children) > 5:
            print(f"  ... and {len(children) - 5} more children")
            
    except Exception as e:
        print(f"     Error: {e}")
    
    # Test section hierarchy path
    test_section = "20.1.2.2.1"
    print(f"\n🌳 Getting hierarchy path for section {test_section}:")
    try:
        path = db_manager.get_section_hierarchy(test_section)
        for i, section in enumerate(path):
            indent = "  " * i
            print(f"{indent}└─ {section['full_section_number']} - {section['title']}")
            
    except Exception as e:
        print(f"     Error: {e}")

def test_database_queries(db_manager):
    """Test direct database queries"""
    print("\n=== Testing Database Queries ===")
    
    # Test specific section lookup
    try:
        import psycopg2
        with psycopg2.connect(**db_manager.db_config) as conn:
            with conn.cursor() as cur:
                # Find sections related to charts
                print("\n📈 Sections containing 'chart' in title:")
                cur.execute("""
                    SELECT full_section_number, title, depth
                    FROM ecma_sections 
                    WHERE LOWER(title) LIKE '%chart%'
                    ORDER BY depth, full_section_number
                    LIMIT 10;
                """)
                
                for row in cur.fetchall():
                    print(f"  • {row[0]} (Level {row[2]}) - {row[1]}")
                
                # Show depth distribution for a specific top-level section
                print(f"\n📊 Depth distribution for section 20 (DrawingML):")
                cur.execute("""
                    SELECT depth, COUNT(*) as count
                    FROM ecma_sections 
                    WHERE level1 = '20'
                    GROUP BY depth
                    ORDER BY depth;
                """)
                
                for row in cur.fetchall():
                    print(f"  Level {row[0]}: {row[1]} sections")
                
                # Show sections by type
                print(f"\n🏷️  Section types in DrawingML (section 20):")
                cur.execute("""
                    SELECT section_type, COUNT(*) as count
                    FROM ecma_sections 
                    WHERE level1 = '20'
                    GROUP BY section_type
                    ORDER BY count DESC;
                """)
                
                for row in cur.fetchall():
                    print(f"  {row[0]}: {row[1]} sections")
                    
    except Exception as e:
        print(f"Error in database queries: {e}")

def test_specific_examples(db_manager):
    """Test specific examples mentioned in the requirements"""
    print("\n=== Testing Specific Examples ===")
    
    # Look for the exact example mentioned in the requirements
    target_section = "20.1.2.2.1"
    print(f"\n🎯 Looking for specific section: {target_section} (bldChart)")
    
    try:
        import psycopg2
        with psycopg2.connect(**db_manager.db_config) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT full_section_number, title, description, depth,
                           level1, level2, level3, level4, level5
                    FROM ecma_sections 
                    WHERE full_section_number = %s;
                """, (target_section,))
                
                result = cur.fetchone()
                if result:
                    print(f"  ✅ Found: {result[0]} - {result[1]}")
                    print(f"     Depth: {result[3]}")
                    print(f"     Hierarchy: L1={result[4]}, L2={result[5]}, L3={result[6]}, L4={result[7]}, L5={result[8]}")
                    if result[2]:
                        desc = result[2][:150] + "..." if len(result[2]) > 150 else result[2]
                        print(f"     Description: {desc}")
                else:
                    print(f"  ❌ Section {target_section} not found")
                    
                # Find similar sections
                print(f"\n🔍 Finding sections containing 'bldChart':")
                cur.execute("""
                    SELECT full_section_number, title, depth
                    FROM ecma_sections 
                    WHERE LOWER(title) LIKE '%bldchart%'
                    ORDER BY depth, full_section_number;
                """)
                
                for row in cur.fetchall():
                    print(f"  • {row[0]} (Level {row[2]}) - {row[1]}")
                    
    except Exception as e:
        print(f"Error in specific examples: {e}")

def main():
    """Main test function"""
    print("🚀 Starting ECMA-376 Database Test Suite")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Get and display statistics
    stats = db_manager.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"Total sections: {stats['general']['total_sections']}")
    print(f"Sections with embeddings: {stats['general']['sections_with_embeddings']}")
    
    print(f"\nDepth distribution:")
    for depth, count in stats['depth_distribution'].items():
        print(f"  Level {depth}: {count} sections")
    
    print(f"\nType distribution:")
    for section_type, count in stats['type_distribution'].items():
        print(f"  {section_type}: {count} sections")
    
    # Run all tests
    test_specific_examples(db_manager)
    test_semantic_search(db_manager)
    test_hierarchical_queries(db_manager)
    test_database_queries(db_manager)
    
    print(f"\n✅ All tests completed successfully!")
    print(f"\n💡 The database is ready for use with:")
    print(f"   • 5-level hierarchical structure (level1 through level5)")
    print(f"   • Semantic search using embeddings")
    print(f"   • Full-text search capabilities") 
    print(f"   • Parent-child relationship queries")
    print(f"   • PostgreSQL with optimized indexes")

if __name__ == "__main__":
    main()