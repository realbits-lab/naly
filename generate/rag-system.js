import dotenv from 'dotenv';
import PDFExtractor from './pdf-extractor.js';
import VectorDatabase from './vector-db.js';
import RAGChatSystem from './rag-chat.js';
import fs from 'fs';
import path from 'path';
import readline from 'readline';

dotenv.config();

class RAGSystem {
  constructor() {
    this.pdfExtractor = new PDFExtractor();
    this.vectorDB = new VectorDatabase();
    this.chatSystem = new RAGChatSystem();
    this.pdfPath = './ecma-376.pdf';
    this.processedDataPath = './processed-data.json';
  }

  async initializeSystem() {
    console.log('🚀 Initializing RAG System for ECMA-376 Document');
    console.log('================================================');
    
    // Check if we have already processed data
    if (fs.existsSync(this.processedDataPath)) {
      console.log('📁 Found existing processed data');
      const choice = await this.askUserChoice();
      
      if (choice === 'use') {
        console.log('✅ Using existing processed data');
        return;
      } else {
        console.log('🔄 Reprocessing PDF...');
        this.vectorDB.clear();
      }
    }

    await this.processPDF();
  }

  async processPDF() {
    console.log('📄 Processing PDF...');
    
    if (!fs.existsSync(this.pdfPath)) {
      console.error(`❌ PDF file not found at: ${this.pdfPath}`);
      console.log('Please make sure the ecma-376.pdf file exists in the current directory');
      return;
    }

    try {
      // Extract text with hierarchy
      console.log('🔍 Extracting text with hierarchy information...');
      const extractedData = await this.pdfExtractor.extractTextWithHierarchy(this.pdfPath);
      
      console.log(`📊 Extraction complete:`);
      console.log(`   - Total pages: ${extractedData.totalPages}`);
      console.log(`   - Total chunks: ${extractedData.chunks.length}`);
      console.log(`   - Total characters: ${extractedData.metadata.totalCharacters}`);
      
      // Save processed data
      fs.writeFileSync(this.processedDataPath, JSON.stringify(extractedData, null, 2));
      
      // Add to vector database
      console.log('🔮 Adding chunks to vector database...');
      await this.vectorDB.addDocuments(extractedData.chunks);
      
      console.log('✅ PDF processing complete!');
      
    } catch (error) {
      console.error('❌ Error processing PDF:', error);
      throw error;
    }
  }

  async askUserChoice() {
    return new Promise((resolve) => {
      const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
      });

      rl.question('Found existing processed data. Use existing (use) or reprocess (new)? ', (answer) => {
        rl.close();
        resolve(answer.toLowerCase() === 'use' ? 'use' : 'new');
      });
    });
  }

  async showStatistics() {
    console.log('\n📊 System Statistics');
    console.log('==================');
    
    const stats = this.vectorDB.getStats();
    console.log(`Total Documents: ${stats.totalDocuments}`);
    console.log(`Total Vectors: ${stats.totalVectors}`);
    
    console.log('\nDocument Types:');
    Object.entries(stats.documentTypes).forEach(([type, count]) => {
      console.log(`  ${type}: ${count}`);
    });
    
    console.log('\nHierarchy Levels:');
    Object.entries(stats.hierarchyLevels).forEach(([level, count]) => {
      console.log(`  Level ${level}: ${count}`);
    });
    
    console.log('\nTop Sections:');
    const topSections = Object.entries(stats.sections)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);
    
    topSections.forEach(([section, count]) => {
      console.log(`  "${section}": ${count} chunks`);
    });
  }

  async testSearch(query = "What is Office Open XML?") {
    console.log('\n🔍 Testing Search Functionality');
    console.log('=============================');
    console.log(`Query: "${query}"`);
    
    const results = await this.vectorDB.search(query, 3);
    
    console.log(`\nFound ${results.length} relevant results:`);
    results.forEach((result, index) => {
      console.log(`\n${index + 1}. Similarity: ${result.similarity.toFixed(3)}`);
      console.log(`   Type: ${result.document.metadata.type}`);
      console.log(`   Section: ${result.document.metadata.section || 'Unknown'}`);
      console.log(`   Text: ${result.document.text.substring(0, 200)}...`);
    });
  }

  async startChat() {
    console.log('\n💬 Starting RAG Chat System');
    console.log('===========================');
    await this.chatSystem.startChat();
  }

  async demonstrateMetadataSearch() {
    console.log('\n🔍 Demonstrating Metadata Search');
    console.log('===============================');
    
    // Search by document type
    console.log('1. Searching for section headers:');
    const sections = this.vectorDB.findByMetadata({ type: 'section' });
    console.log(`   Found ${sections.length} section headers`);
    sections.slice(0, 5).forEach((doc, index) => {
      console.log(`   ${index + 1}. ${doc.text}`);
    });
    
    // Search by hierarchy level
    console.log('\n2. Searching for subsections:');
    const subsections = this.vectorDB.findByMetadata({ type: 'subsection' });
    console.log(`   Found ${subsections.length} subsections`);
    subsections.slice(0, 5).forEach((doc, index) => {
      console.log(`   ${index + 1}. ${doc.text}`);
    });
    
    // Search by hierarchy path
    console.log('\n3. Searching for documents containing "XML":');
    const xmlDocs = this.vectorDB.findByMetadata({ hierarchy: 'XML' });
    console.log(`   Found ${xmlDocs.length} documents`);
  }

  async run() {
    try {
      await this.initializeSystem();
      await this.showStatistics();
      await this.testSearch();
      await this.demonstrateMetadataSearch();
      await this.startChat();
    } catch (error) {
      console.error('❌ Error running RAG system:', error);
      process.exit(1);
    }
  }
}

// Command line interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const ragSystem = new RAGSystem();
  
  // Handle command line arguments
  const args = process.argv.slice(2);
  
  if (args.includes('--help')) {
    console.log(`
RAG System for ECMA-376 Document

Usage:
  node rag-system.js [options]

Options:
  --help              Show this help message
  --process-only      Only process the PDF without starting chat
  --chat-only         Only start chat (assumes PDF is already processed)
  --stats             Show database statistics
  --test-search       Test search functionality

Examples:
  node rag-system.js                    # Full system initialization and chat
  node rag-system.js --process-only     # Only process PDF
  node rag-system.js --chat-only        # Only start chat
  node rag-system.js --stats            # Show statistics
    `);
    process.exit(0);
  }

  if (args.includes('--process-only')) {
    ragSystem.initializeSystem()
      .then(() => console.log('✅ Processing complete'))
      .catch(error => console.error('❌ Error:', error));
  } else if (args.includes('--chat-only')) {
    ragSystem.startChat()
      .catch(error => console.error('❌ Error:', error));
  } else if (args.includes('--stats')) {
    ragSystem.showStatistics()
      .catch(error => console.error('❌ Error:', error));
  } else if (args.includes('--test-search')) {
    ragSystem.testSearch()
      .catch(error => console.error('❌ Error:', error));
  } else {
    ragSystem.run()
      .catch(error => console.error('❌ Error:', error));
  }
}

export default RAGSystem;