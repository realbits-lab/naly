# PowerPoint RAG System

A comprehensive system for extracting shape data from PowerPoint files and building a RAG (Retrieval-Augmented Generation) search interface for querying presentation content.

## 🎯 Overview

This system combines PowerPoint processing, LLM-based description generation, and vector database storage to create a powerful RAG search interface for PowerPoint presentations.

### Key Features

- **PowerPoint Processing**: Extract comprehensive shape data, XML structure, and metadata
- **PDF Conversion**: Convert PowerPoint slides to PDF for visual analysis
- **LLM Description Generation**: Generate detailed slide descriptions using OpenAI GPT
- **Vector Database Storage**: Store embeddings for semantic search
- **RAG Chat Interface**: Interactive chat system for querying presentation content
- **Shape Analysis**: Search and analyze specific shapes, text, and visual elements

## 🏗️ Architecture

The system consists of two main components:

1. **Python Backend** (`ppt_rag_system.py`): 
   - PowerPoint file processing and XML extraction
   - PDF conversion using LibreOffice
   - Data preparation and export

2. **Node.js Frontend** (`generate/ppt-rag-system.js`):
   - LLM-based description enhancement
   - Vector database integration
   - RAG chat interface

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Node.js 16+
- LibreOffice (for PDF conversion)
- OpenAI API key

### Installation

1. **Install Python dependencies:**
```bash
pip install python-pptx pillow
```

2. **Install Node.js dependencies:**
```bash
cd generate
npm install
```

3. **Set up OpenAI API key:**
```bash
echo "OPENAI_API_KEY=your_api_key_here" > generate/.env
```

### Basic Usage

1. **Process a PowerPoint file:**
```bash
python3 ppt_rag_system.py examples/extract/sample_parts/sample1-1.pptx --export-nodejs
```

2. **Start the RAG chat system:**
```bash
cd generate
node ppt-rag-chat.js ../ppt_rag_output/powerpoint_rag_data.json
```

3. **Ask questions about your presentation:**
```
You: What shapes are on slide 1?
You: Find all text boxes in the presentation
You: What's the main content of slide 2?
```

## 📋 Detailed Usage

### Python Backend

The Python backend processes PowerPoint files and extracts comprehensive data:

```bash
# Basic processing
python3 ppt_rag_system.py input.pptx

# With custom output directory
python3 ppt_rag_system.py input.pptx --output-dir custom_output

# Export for Node.js RAG system
python3 ppt_rag_system.py input.pptx --export-nodejs
```

**Output files:**
- `{filename}_processed.json`: Complete slide and shape data
- `{filename}_processed_vector_entries.json`: Vector database entries
- `{filename}.pdf`: PDF conversion of slides
- `powerpoint_rag_data.json`: Node.js compatible format

### Node.js RAG System

The Node.js system provides enhanced descriptions and RAG capabilities:

```bash
cd generate

# Full processing with enhanced descriptions
node ppt-rag-system.js ../path/to/presentation.pptx

# Demo mode only
node ppt-rag-system.js ../path/to/presentation.pptx --demo-only

# Chat only (assumes data is processed)
node ppt-rag-system.js ../path/to/presentation.pptx --chat-only
```

### RAG Chat Interface

The chat interface provides powerful querying capabilities:

```bash
# Start chat with processed data
node ppt-rag-chat.js path/to/powerpoint_rag_data.json
```

**Available commands:**
- `/help`: Show help message
- `/stats`: Display presentation statistics
- `/shapes`: List all shape types
- `/slide N`: Show information for slide N
- `/exit`: Exit the chat

**Example queries:**
- "What shapes contain text?"
- "Show me slides with charts"
- "Find all rectangles"
- "What's the main content of slide 1?"
- "List all text on slide 2"

## 🔧 Testing

Run the comprehensive test suite:

```bash
# Test the complete system
python3 test_ppt_rag_system.py

# Run demo script
./demo_ppt_rag.sh
```

## 📊 Data Structure

The system extracts and stores the following data:

### Slide Data
- Slide index and PDF page number
- Enhanced LLM-generated descriptions
- Shape information (type, position, text content)
- XML structure data
- Media files and metadata

### Shape Data
- Shape type and geometry
- Position and dimensions
- Text content and formatting
- Visual properties (fill, line, shadow)
- Custom geometry definitions

### Vector Database Entries
- Slide descriptions with metadata
- Shape text content with positioning
- Searchable embeddings for semantic queries

## 🎨 Example Queries and Responses

### Query: "What shapes are on slide 1?"
**Response:** "Slide 1 contains several shapes including text boxes, rectangles, and image placeholders. The main content includes a title placeholder with 'Here is where this template begins' and additional text elements positioned at specific coordinates."

### Query: "Find all text boxes"
**Response:** "I found 3 text boxes across the presentation:
1. Slide 1: Title text box at position (100, 200) with content 'Here is where this template begins'
2. Slide 1: Content text box at position (150, 400) with body text
3. Slide 2: Header text box with subtitle content"

## 🔍 Advanced Features

### Shape Analysis
- Search by shape type (rectangles, circles, text boxes)
- Filter by slide number or position
- Analyze shape distribution across slides

### Visual Search
- Semantic search across slide content
- Find related shapes and elements
- Context-aware responses

### XML Structure Analysis
- Access raw PowerPoint XML data
- Analyze formatting and structure
- Extract custom geometry definitions

## 📝 System Requirements

- **Python**: 3.7+ with python-pptx, pillow
- **Node.js**: 16+ with OpenAI API access
- **LibreOffice**: For PDF conversion (optional)
- **Memory**: Minimum 2GB RAM for processing
- **Storage**: Variable based on presentation size

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is part of the PowerPoint template generation framework. Please refer to the main project license.

## 🆘 Troubleshooting

### Common Issues

1. **LibreOffice not found**: Install LibreOffice or use fallback image extraction
2. **OpenAI API errors**: Check API key and quota
3. **Memory issues**: Process smaller files or increase available memory
4. **Vector database errors**: Ensure proper JSON format and file permissions

### Debug Mode

Enable debug output:
```bash
# Python backend
python3 ppt_rag_system.py input.pptx --debug

# Node.js system
DEBUG=* node ppt-rag-system.js input.pptx
```

## 📞 Support

For support and questions:
1. Check the troubleshooting section
2. Review the test files and examples
3. Consult the main project documentation

---

**Built with ❤️ for PowerPoint analysis and RAG search**