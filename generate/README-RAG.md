# RAG System for ECMA-376 Document

A comprehensive Retrieval-Augmented Generation (RAG) system for querying the ECMA-376 Office Open XML File Formats standard document.

## Features

- **PDF Text Extraction**: Extracts text with hierarchical structure (sections, subsections, paragraphs)
- **Vector Database**: Stores document chunks with embeddings for semantic search
- **Metadata Preservation**: Maintains document hierarchy and structure information
- **AI-Powered Chat**: Interactive chat interface using OpenAI's GPT models
- **Chunking Strategy**: Intelligent text chunking with overlap for better context
- **Multiple Search Modes**: Semantic search and metadata-based filtering

## Architecture

### Core Components

1. **PDFExtractor** (`pdf-extractor.js`)
   - Extracts text from PDF with hierarchy detection
   - Identifies sections, subsections, and paragraphs
   - Creates chunks with metadata about document structure

2. **VectorDatabase** (`vector-db.js`)
   - Stores document chunks with embeddings
   - Implements cosine similarity search
   - Supports metadata filtering and statistics

3. **RAGChatSystem** (`rag-chat.js`)
   - Interactive chat interface
   - Context-aware responses using retrieved documents
   - Streaming and non-streaming response modes

4. **RAGSystem** (`rag-system.js`)
   - Main orchestrator for the entire system
   - Handles initialization, processing, and chat startup

## Setup

### Prerequisites

- Node.js (v18 or later)
- OpenAI API key
- ECMA-376 PDF document

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

3. Ensure the ECMA-376 PDF is in the current directory as `ecma-376.pdf`

## Usage

### Basic Usage

```bash
# Run the complete system (process PDF + start chat)
node rag-system.js

# Process PDF only
node rag-system.js --process-only

# Start chat only (requires pre-processed data)
node rag-system.js --chat-only

# Show database statistics
node rag-system.js --stats

# Test search functionality
node rag-system.js --test-search
```

### Demo Mode

```bash
# Run demonstration without chat
node demo-rag.js demo

# Run interactive demo with chat
node demo-rag.js interactive
```

### Programmatic Usage

```javascript
import RAGSystem from './rag-system.js';

const ragSystem = new RAGSystem();

// Initialize and process PDF
await ragSystem.initializeSystem();

// Search for relevant content
const results = await ragSystem.vectorDB.search("What is Office Open XML?", 5);

// Start chat interface
await ragSystem.startChat();
```

## System Components

### Text Extraction & Chunking

The system uses intelligent text extraction that:
- Detects document hierarchy (titles, sections, subsections)
- Preserves structural metadata
- Creates overlapping chunks for better context
- Handles different content types (paragraphs, lists, headers)

### Vector Database

Features:
- **Embedding Model**: OpenAI text-embedding-3-small
- **Similarity Search**: Cosine similarity with configurable top-k
- **Metadata Storage**: Hierarchical document structure
- **Persistence**: JSON file storage for offline access

### Chat Interface

The chat system provides:
- **Context-Aware Responses**: Uses retrieved documents for accurate answers
- **Streaming Support**: Real-time response generation
- **Command Interface**: Special commands for system interaction
- **Chat History**: Maintains conversation context

## Configuration

### Environment Variables

```env
OPENAI_API_KEY=your_openai_api_key_here
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini
VECTOR_DB_PATH=./vector-db.json
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
PDF_PATH=./ecma-376.pdf
PROCESSED_DATA_PATH=./processed-data.json
```

### Chunking Parameters

- **Chunk Size**: 1000 characters (configurable)
- **Overlap**: 200 characters (configurable)
- **Strategy**: Recursive character splitting with hierarchy preservation

## Chat Commands

During chat interaction:
- `exit` - Exit the chat system
- `stats` - Show database statistics
- `stream` - Toggle streaming mode on/off

## Example Queries

The system can answer questions like:
- "What is Office Open XML?"
- "How are relationships defined in OOXML?"
- "What are the main parts of a SpreadsheetML document?"
- "How does WordprocessingML handle styles?"
- "What are the security considerations for OOXML?"

## Data Structure

### Document Chunks

```javascript
{
  id: "chunk_1",
  text: "The content of the chunk...",
  metadata: {
    type: "paragraph",           // section, subsection, paragraph, list-item
    level: 3,                    // hierarchy level (0-3)
    hierarchy: ["Section 1", "Subsection 1.1"],  // parent hierarchy
    section: "Section 1 > Subsection 1.1",       // human-readable path
    chunkIndex: 1
  }
}
```

### Vector Storage

```javascript
{
  documents: [/* document chunks */],
  vectors: [/* embedding vectors */],
  lastUpdated: "2024-01-01T00:00:00.000Z"
}
```

## Performance

- **PDF Processing**: ~2-5 minutes for large documents
- **Vector Search**: <100ms for typical queries
- **Chat Response**: 1-3 seconds depending on context size

## Limitations

- Requires OpenAI API key (paid service)
- PDF text extraction may not capture complex formatting
- Vector database is in-memory with JSON persistence
- Single-user system (no concurrent chat sessions)

## Future Enhancements

- Support for multiple PDF documents
- Advanced metadata extraction (tables, images)
- Persistent vector database (PostgreSQL with pgvector)
- Multi-user chat sessions
- Web interface
- Document summarization capabilities

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure OPENAI_API_KEY is set in .env
2. **PDF Not Found**: Verify ecma-376.pdf exists in the directory
3. **Memory Issues**: Reduce chunk size or process in batches
4. **Slow Processing**: Check network connection and API rate limits

### Debug Mode

Enable debug logging:
```javascript
// In any module
console.log = (...args) => {
  console.error(new Date().toISOString(), ...args);
};
```

## License

MIT License - see LICENSE file for details.