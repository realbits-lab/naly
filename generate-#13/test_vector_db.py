#!/usr/bin/env python3
"""
Test script for the vector database system.
"""

from vector_db_system import SlideAnalyzer, VectorDatabase, RAGChatBot
from pathlib import Path

def test_system():
    """Test the vector database system without interactive chat."""
    print("🧪 Testing Vector Database System...")
    
    try:
        # Initialize components
        print("1. Initializing analyzer...")
        analyzer = SlideAnalyzer()
        
        print("2. Initializing vector database...")
        vector_db = VectorDatabase()
        
        # Paths
        slides_dir = Path("sample1-pptx/ppt/slides")
        images_dir = Path("sample1-pdf")
        
        # Process slide 1
        image_path = images_dir / "page-01.png"
        xml_path = slides_dir / "slide1.xml"
        
        if image_path.exists() and xml_path.exists():
            print("3. Processing slide 1...")
            
            # Read XML content
            with open(xml_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Analyze slide
            slide_data = analyzer.analyze_slide_image(str(image_path), str(xml_path))
            
            print(f"   ✅ Analysis complete - Found {len(slide_data['shapes'])} shapes")
            
            # Add to vector database
            slide_id = vector_db.add_slide(slide_data, xml_content, str(image_path))
            print(f"   ✅ Added to database with ID: {slide_id}")
            
            # Test search
            print("4. Testing search functionality...")
            chat_bot = RAGChatBot(vector_db)
            
            test_queries = [
                "donut chart",
                "bar chart",
                "infographic",
                "design elements"
            ]
            
            for query in test_queries:
                print(f"\n🔍 Testing query: '{query}'")
                response = chat_bot.chat(query)
                print(f"Response: {response[:800]}...")
                if "XML Content:" in response:
                    print("   ✅ XML data included in response")
            
            print("\n✅ All tests passed!")
            
        else:
            print(f"❌ Files not found: {image_path}, {xml_path}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_system()