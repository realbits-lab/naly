#\!/bin/bash

# PowerPoint RAG System Demo Script

echo "🎯 PowerPoint RAG System Demo"
echo "============================"

# Check if sample file exists
SAMPLE_FILE="examples/extract/sample_parts/sample1-1.pptx"
if [ \! -f "$SAMPLE_FILE" ]; then
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

# Step 2: Show generated files
echo ""
echo "📄 Generated files:"
ls -la demo_output/

echo ""
echo "🔍 Sample data preview:"
echo "Slide descriptions:"
python3 -c "
import json
with open('demo_output/powerpoint_rag_data.json', 'r') as f:
    data = json.load(f)
    for doc in data['documents'][:3]:
        print(f'- {doc[\"id\"]}: {doc[\"text\"][:80]}...')
"

echo ""
echo "📊 Data statistics:"
python3 -c "
import json
with open('demo_output/powerpoint_rag_data.json', 'r') as f:
    data = json.load(f)
    print(f'Total entries: {len(data[\"documents\"])}')
    print(f'Entry types: {data[\"metadata\"][\"entry_types\"]}')
"

echo ""
echo "🎉 Demo completed\!"
echo ""
echo "🚀 Next steps:"
echo "1. Start the RAG chat system:"
echo "   cd generate && node ppt-rag-chat.js ../demo_output/powerpoint_rag_data.json"
echo ""
echo "2. Ask questions like:"
echo "   - What shapes are on slide 1?"
echo "   - Find all text boxes"
echo "   - What's the main content of the slide?"
echo ""
echo "3. Use commands like:"
echo "   - /stats (show statistics)"
echo "   - /shapes (list shape types)"
echo "   - /slide 1 (show slide 1 info)"
echo "   - /help (show help)"
EOF < /dev/null