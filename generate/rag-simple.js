import dotenv from 'dotenv';
import PDFExtractor from './pdf-extractor.js';
import VectorDatabase from './vector-db.js';
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

dotenv.config();

class SimpleRAGSystem {
  constructor(maxChunks = 50) {
    this.pdfExtractor = new PDFExtractor();
    this.vectorDB = new VectorDatabase('./simple-vector-db.json');
    this.model = openai('gpt-4o-mini');
    this.maxChunks = maxChunks;
    this.isInitialized = false;
  }

  async initialize() {
    if (this.isInitialized) {
      console.log('✅ System already initialized');
      return;
    }

    console.log(`🚀 Initializing Simple RAG System (${this.maxChunks} chunks)`);
    console.log('==================================================');

    try {
      // Extract PDF
      console.log('📄 Extracting PDF...');
      const data = await this.pdfExtractor.extractTextWithHierarchy('./ecma-376.pdf');
      console.log(`   - Extracted ${data.chunks.length} chunks from ${data.totalPages} pages`);

      // Process limited chunks
      const chunks = data.chunks.slice(0, this.maxChunks);
      console.log(`   - Processing first ${chunks.length} chunks`);

      // Add to vector database
      console.log('🔮 Creating vector database...');
      await this.vectorDB.addDocuments(chunks);
      console.log(`   - Added ${chunks.length} chunks to vector database`);

      this.isInitialized = true;
      console.log('✅ System initialized successfully!');
      
      // Show statistics
      const stats = this.vectorDB.getStats();
      console.log(`\n📊 Statistics: ${stats.totalDocuments} documents, ${Object.keys(stats.documentTypes).length} types`);
      
    } catch (error) {
      console.error('❌ Initialization failed:', error);
      throw error;
    }
  }

  async askQuestion(question) {
    if (!this.isInitialized) {
      await this.initialize();
    }

    console.log(`\n🔍 Question: "${question}"`);
    console.log('=' + '='.repeat(question.length + 12));

    try {
      // Search for relevant context
      const searchResults = await this.vectorDB.search(question, 3);
      console.log(`📚 Found ${searchResults.length} relevant passages`);

      if (searchResults.length === 0) {
        console.log('❌ No relevant context found. Try a more specific question.');
        return;
      }

      // Show context sources
      console.log('\n📋 Context sources:');
      searchResults.forEach((result, index) => {
        console.log(`   ${index + 1}. Similarity: ${result.similarity.toFixed(3)} - ${result.document.metadata.section || 'Unknown section'}`);
      });

      // Format context for AI
      const context = searchResults.map(r => r.document.text).join('\n\n');

      // Generate AI response
      console.log('\n🤖 Generating response...');
      const response = await generateText({
        model: this.model,
        messages: [
          { 
            role: 'system', 
            content: 'You are an expert on ECMA-376 Office Open XML. Answer questions based on the provided context. Be specific and reference the context when possible.' 
          },
          { 
            role: 'user', 
            content: `Context from ECMA-376 document:\n\n${context}\n\nQuestion: ${question}` 
          }
        ],
        maxTokens: 500,
        temperature: 0.7
      });

      console.log('\n💬 Answer:');
      console.log(response.text);
      console.log('\n' + '='.repeat(80));

    } catch (error) {
      console.error('❌ Error processing question:', error);
    }
  }

  async demo() {
    console.log('🎯 RAG System Demo');
    console.log('==================');

    await this.initialize();

    const demoQuestions = [
      "What is Office Open XML?",
      "How are relationships defined in OOXML?",
      "What are the main parts of a document?",
      "How does WordprocessingML work?",
      "What is SpreadsheetML?",
      "How are themes implemented?"
    ];

    console.log('\n🎮 Running demo with sample questions...\n');

    for (const question of demoQuestions) {
      await this.askQuestion(question);
      await new Promise(resolve => setTimeout(resolve, 1000)); // Small delay
    }

    console.log('\n🎉 Demo complete!');
  }
}

// Usage examples
async function main() {
  const rag = new SimpleRAGSystem(100); // Use 100 chunks for better coverage

  const args = process.argv.slice(2);
  const command = args[0];
  const question = args.slice(1).join(' ');

  if (command === 'demo') {
    await rag.demo();
  } else if (command === 'ask' && question) {
    await rag.askQuestion(question);
  } else if (command === 'init') {
    await rag.initialize();
  } else {
    console.log(`
🚀 Simple RAG System for ECMA-376

Usage:
  node rag-simple.js demo                    # Run demo with sample questions
  node rag-simple.js ask "your question"     # Ask a specific question
  node rag-simple.js init                    # Initialize system only

Examples:
  node rag-simple.js ask "What is Office Open XML?"
  node rag-simple.js ask "How are relationships defined?"
  node rag-simple.js ask "What are the main parts of a document?"
  node rag-simple.js demo
    `);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}

export default SimpleRAGSystem;