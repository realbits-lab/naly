import dotenv from 'dotenv';
import PDFExtractor from './pdf-extractor.js';
import VectorDatabase from './vector-db.js';
import RAGChatSystem from './rag-chat.js';
import fs from 'fs';
import path from 'path';
import readline from 'readline';

dotenv.config();

class FastRAGSystem {
  constructor(maxChunks = 100) {
    this.pdfExtractor = new PDFExtractor();
    this.vectorDB = new VectorDatabase();
    this.chatSystem = new RAGChatSystem();
    this.pdfPath = './ecma-376.pdf';
    this.processedDataPath = './processed-data-fast.json';
    this.maxChunks = maxChunks;
  }

  async initializeSystem() {
    console.log(`🚀 Initializing Fast RAG System (${this.maxChunks} chunks max)`);
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
    console.log('📄 Processing PDF (limited chunks for testing)...');
    
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
      
      // Limit chunks for faster processing
      const limitedChunks = extractedData.chunks.slice(0, this.maxChunks);
      console.log(`   - Processing first ${limitedChunks.length} chunks for testing`);
      
      // Update extracted data
      const limitedData = {
        ...extractedData,
        chunks: limitedChunks
      };
      
      // Save processed data
      fs.writeFileSync(this.processedDataPath, JSON.stringify(limitedData, null, 2));
      
      // Add to vector database
      console.log('🔮 Adding chunks to vector database...');
      await this.vectorDB.addDocuments(limitedChunks);
      
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

  async run() {
    try {
      await this.initializeSystem();
      await this.showStatistics();
      await this.testSearch();
      await this.startChat();
    } catch (error) {
      console.error('❌ Error running RAG system:', error);
      process.exit(1);
    }
  }
}

// Command line interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const maxChunks = parseInt(process.argv[2]) || 100;
  const fastRAG = new FastRAGSystem(maxChunks);
  
  console.log(`🚀 Fast RAG System for ECMA-376 Document (${maxChunks} chunks)`);
  console.log('=========================================');
  
  fastRAG.run()
    .catch(error => console.error('❌ Error:', error));
}

export default FastRAGSystem;