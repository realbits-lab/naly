#!/usr/bin/env python3

import os
import sys
import json
import subprocess
from pathlib import Path

def test_ppt_rag_system():
    """Test the PowerPoint RAG system with sample files"""
    
    print("🧪 Testing PowerPoint RAG System")
    print("=================================")
    
    # Test files
    test_files = [
        "examples/extract/sample_parts/sample1-1.pptx",
        "examples/extract/sample_parts/sample1-2.pptx",
        "examples/extract/sample_parts/sample1.pptx"
    ]
    
    results = []
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"⚠️  Test file not found: {test_file}")
            continue
            
        print(f"\n📁 Testing: {test_file}")
        print("-" * 50)
        
        try:
            # Run the Python RAG system
            result = subprocess.run([
                'python3', 'ppt_rag_system.py',
                test_file,
                '--output-dir', f'test_output_{Path(test_file).stem}',
                '--export-nodejs'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Python processing successful")
                
                # Check output files
                output_dir = Path(f'test_output_{Path(test_file).stem}')
                if output_dir.exists():
                    files = list(output_dir.glob('*'))
                    print(f"📄 Generated {len(files)} files:")
                    for file in files:
                        print(f"   - {file.name}")
                
                results.append({
                    'file': test_file,
                    'status': 'success',
                    'output_dir': str(output_dir)
                })
            else:
                print("❌ Python processing failed")
                print(f"Error: {result.stderr}")
                results.append({
                    'file': test_file,
                    'status': 'failed',
                    'error': result.stderr
                })
                
        except subprocess.TimeoutExpired:
            print("⏰ Processing timed out")
            results.append({
                'file': test_file,
                'status': 'timeout'
            })
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                'file': test_file,
                'status': 'error',
                'error': str(e)
            })
    
    # Print summary
    print("\n📊 Test Summary")
    print("===============")
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"Successful: {successful}/{len(results)}")
    
    for result in results:
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_emoji} {result['file']}: {result['status']}")
    
    return results

def test_specific_questions():
    """Test specific questions that the system should be able to answer"""
    
    print("\n🔍 Testing Specific Questions")
    print("=============================")
    
    questions = [
        "What shapes are on slide 1?",
        "Find all text boxes in the presentation",
        "What's the main content of the first slide?",
        "Show me all rectangles in the presentation",
        "What charts are in the presentation?",
        "Find slides with financial data",
        "List all text on slide 1",
        "What's the layout of slide 2?"
    ]
    
    print("Questions the system should be able to answer:")
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}")
    
    print("\n💡 To test these questions:")
    print("1. Run the system with a PowerPoint file")
    print("2. Use the chat interface to ask these questions")
    print("3. Verify the responses are accurate and helpful")

def create_demo_script():
    """Create a demo script for easy testing"""
    
    demo_script = """#!/bin/bash

# PowerPoint RAG System Demo Script

echo "🎯 PowerPoint RAG System Demo"
echo "============================"

# Check if sample file exists
SAMPLE_FILE="examples/extract/sample_parts/sample1-1.pptx"
if [ ! -f "$SAMPLE_FILE" ]; then
    echo "❌ Sample file not found: $SAMPLE_FILE"
    echo "Please make sure you have sample PowerPoint files in the examples/extract/sample_parts/ directory"
    exit 1
fi

echo "📁 Using sample file: $SAMPLE_FILE"
echo ""

# Step 1: Process PowerPoint file
echo "🔄 Step 1: Processing PowerPoint file..."
python3 ppt_rag_system.py "$SAMPLE_FILE" --output-dir demo_output --export-nodejs

if [ $? -eq 0 ]; then
    echo "✅ PowerPoint processing completed"
else
    echo "❌ PowerPoint processing failed"
    exit 1
fi

# Step 2: Run Node.js RAG system
echo ""
echo "🔄 Step 2: Starting Node.js RAG system..."
cd generate
node ppt-rag-system.js "../$SAMPLE_FILE" --demo-only

echo ""
echo "🎉 Demo completed!"
echo "You can now run the chat interface with:"
echo "cd generate && node ppt-rag-chat.js ../demo_output/powerpoint_rag_data.json"
"""

    with open("demo_ppt_rag.sh", "w") as f:
        f.write(demo_script)
    
    # Make executable
    os.chmod("demo_ppt_rag.sh", 0o755)
    
    print("\n🚀 Demo script created: demo_ppt_rag.sh")
    print("Run with: ./demo_ppt_rag.sh")

def main():
    """Main test function"""
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    
    # Check if Python script exists
    if not Path("ppt_rag_system.py").exists():
        print("❌ ppt_rag_system.py not found")
        return
    
    # Check if sample files exist
    sample_dir = Path("examples/extract/sample_parts")
    if not sample_dir.exists():
        print("❌ Sample directory not found")
        return
    
    print("✅ Dependencies check passed")
    
    # Run tests
    results = test_ppt_rag_system()
    
    # Test questions
    test_specific_questions()
    
    # Create demo script
    create_demo_script()
    
    print("\n🎯 Next Steps:")
    print("1. Install Node.js dependencies: cd generate && npm install")
    print("2. Set up OpenAI API key in .env file")
    print("3. Run the demo script: ./demo_ppt_rag.sh")
    print("4. Or test manually with specific files")

if __name__ == "__main__":
    main()