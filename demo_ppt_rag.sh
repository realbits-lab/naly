#!/bin/bash

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
