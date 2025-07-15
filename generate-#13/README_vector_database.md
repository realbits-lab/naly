# Vector Database System for PowerPoint Slide Analysis

A comprehensive RAG (Retrieval-Augmented Generation) system that creates a vector database from PowerPoint slides and provides intelligent search capabilities.

## 🎯 Overview

This system processes PowerPoint slides by:

1. **Analyzing slide images** - Extracts visual elements and describes their purposes
2. **Generating vector embeddings** - Converts descriptions to searchable vectors  
3. **Storing in vector database** - Uses FAISS + SQLite for efficient similarity search
4. **Providing RAG chat interface** - Allows natural language queries about slides

## 📁 Files Structure

```
vector_db_system.py          # Core system implementation
enhanced_vector_db.py        # Enhanced version processing all slides
test_vector_db.py           # Test script for validation
requirements.txt            # Python dependencies
README_vector_database.md   # This documentation
```

## 🔧 Key Components

### 1. SlideAnalyzer
- Analyzes slide images and XML content
- Generates detailed shape descriptions
- Identifies purposes for each visual element
- Special detailed analysis for slide 1 (title slide)

### 2. VectorDatabase  
- Uses SentenceTransformer for text embeddings
- FAISS index for vector similarity search
- SQLite for metadata and relationships
- Stores descriptions, XML content, and image paths

### 3. RAGChatBot
- Natural language query interface
- Retrieves relevant slides using vector similarity
- Generates responses with slide details and purposes

## 🚀 Installation & Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic test
python test_vector_db.py

# Run enhanced system with all slides
python enhanced_vector_db.py
```

## 💾 Database Schema

### Slides Table
- `slide_number`: Slide identifier
- `title`: Slide title
- `description`: Full text description for embeddings
- `xml_content`: Raw PowerPoint XML
- `image_path`: Path to slide image
- `shapes_json`: JSON array of shape analysis
- `overall_purpose`: Slide's main purpose
- `embedding_id`: FAISS index reference

### Embeddings Table
- `slide_id`: Foreign key to slides
- `embedding_text`: Text used for vector generation

## 🔍 Example Queries

The RAG system can answer queries like:

- "What slides contain charts or graphs?"
- "Show me slides about design elements"
- "Find slides with data visualization"
- "Which slides have donut charts?"
- "What slides show color schemes?"

## 📊 Slide Analysis Example

For slide 1, the system identifies:

### Visual Elements
- **Donut Chart**: 4-segment circular chart for data distribution
- **Bar Chart**: 4 vertical bars for metric comparison  
- **Background Document**: Paper-like effect for professional appearance
- **Title Text**: "Design Elements Infographics"
- **Subtitle Text**: "Here is where this template begins"

### Purposes
- Title slide introducing infographic template
- Showcases available visual elements
- Establishes professional design aesthetic
- Demonstrates template capabilities

## 🎯 Vector Similarity Search

Uses cosine similarity on normalized embeddings:
- Query text → embedding vector
- Search FAISS index for similar vectors
- Retrieve slide metadata from SQLite
- Rank by similarity scores

## 📈 System Performance

- **34 slides processed** in comprehensive database
- **384-dimension embeddings** using all-MiniLM-L6-v2
- **Sub-second search response** times
- **Relevance scores** 0.3-0.6 for good matches

## 🔮 Future Enhancements

1. **Advanced Image Analysis**: Use computer vision for automatic shape detection
2. **Multi-modal Embeddings**: Combine text and visual features
3. **Semantic Slide Clustering**: Group similar slides automatically
4. **Export Capabilities**: Generate reports from query results
5. **Batch Processing**: Handle multiple presentations

## 🧪 Testing

The system includes comprehensive testing:

```bash
# Basic functionality test
python test_vector_db.py

# Demo with multiple queries  
echo "1" | python enhanced_vector_db.py

# Interactive chat mode
echo "2" | python enhanced_vector_db.py
```

## 📋 Technical Details

- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Index**: FAISS IndexFlatIP (inner product)
- **Database**: SQLite with normalized schema
- **Search**: Top-k similarity with metadata retrieval
- **Response Generation**: Template-based with slide context

This system demonstrates practical RAG implementation for document analysis and provides a foundation for more advanced slide intelligence applications.