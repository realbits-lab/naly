import PDFExtractor from './pdf-extractor.js';
import VectorDatabase from './vector-db.js';
import RAGChatSystem from './rag-chat.js';
import fs from 'fs';
import dotenv from 'dotenv';

dotenv.config();

class RAGSystemTest {
  constructor() {
    this.pdfExtractor = new PDFExtractor();
    this.vectorDB = new VectorDatabase('./test-vector-db.json');
    this.pdfPath = './ecma-376.pdf';
    this.results = {
      pdfExtraction: null,
      vectorStorage: null,
      search: null,
      chat: null
    };
  }

  async testPDFExtraction() {
    console.log('🧪 Testing PDF Extraction...');
    
    try {
      if (!fs.existsSync(this.pdfPath)) {
        throw new Error(`PDF file not found: ${this.pdfPath}`);
      }

      const startTime = Date.now();
      const extractedData = await this.pdfExtractor.extractTextWithHierarchy(this.pdfPath);
      const endTime = Date.now();

      this.results.pdfExtraction = {
        success: true,
        totalPages: extractedData.totalPages,
        totalChunks: extractedData.chunks.length,
        totalCharacters: extractedData.metadata.totalCharacters,
        processingTime: endTime - startTime,
        sampleChunk: extractedData.chunks[0] || null
      };

      console.log(`✅ PDF Extraction Success:`);
      console.log(`   Pages: ${this.results.pdfExtraction.totalPages}`);
      console.log(`   Chunks: ${this.results.pdfExtraction.totalChunks}`);
      console.log(`   Characters: ${this.results.pdfExtraction.totalCharacters}`);
      console.log(`   Time: ${this.results.pdfExtraction.processingTime}ms`);

      return extractedData;
    } catch (error) {
      console.error(`❌ PDF Extraction Failed: ${error.message}`);
      this.results.pdfExtraction = {
        success: false,
        error: error.message
      };
      throw error;
    }
  }

  async testVectorStorage(chunks) {
    console.log('\n🧪 Testing Vector Storage...');
    
    try {
      if (!process.env.OPENAI_API_KEY) {
        throw new Error('OPENAI_API_KEY not found in environment variables');
      }

      const startTime = Date.now();
      
      // Test with a smaller subset for quick testing
      const testChunks = chunks.slice(0, Math.min(10, chunks.length));
      await this.vectorDB.addDocuments(testChunks);
      
      const endTime = Date.now();
      const stats = this.vectorDB.getStats();

      this.results.vectorStorage = {
        success: true,
        documentsStored: stats.totalDocuments,
        vectorsStored: stats.totalVectors,
        processingTime: endTime - startTime,
        stats: stats
      };

      console.log(`✅ Vector Storage Success:`);
      console.log(`   Documents: ${this.results.vectorStorage.documentsStored}`);
      console.log(`   Vectors: ${this.results.vectorStorage.vectorsStored}`);
      console.log(`   Time: ${this.results.vectorStorage.processingTime}ms`);

      return true;
    } catch (error) {
      console.error(`❌ Vector Storage Failed: ${error.message}`);
      this.results.vectorStorage = {
        success: false,
        error: error.message
      };
      throw error;
    }
  }

  async testSearch() {
    console.log('\n🧪 Testing Search Functionality...');
    
    try {
      const testQueries = [
        "What is Office Open XML?",
        "How are relationships defined?",
        "What are the main parts of a document?"
      ];

      const searchResults = {};
      
      for (const query of testQueries) {
        const startTime = Date.now();
        const results = await this.vectorDB.search(query, 3);
        const endTime = Date.now();
        
        searchResults[query] = {
          results: results.length,
          topSimilarity: results[0]?.similarity || 0,
          processingTime: endTime - startTime
        };
        
        console.log(`   "${query}": ${results.length} results, top similarity: ${results[0]?.similarity?.toFixed(3) || 'N/A'}`);
      }

      this.results.search = {
        success: true,
        testQueries: testQueries.length,
        results: searchResults
      };

      console.log(`✅ Search Test Success: ${testQueries.length} queries tested`);
      return true;
    } catch (error) {
      console.error(`❌ Search Test Failed: ${error.message}`);
      this.results.search = {
        success: false,
        error: error.message
      };
      throw error;
    }
  }

  async testMetadataFiltering() {
    console.log('\n🧪 Testing Metadata Filtering...');
    
    try {
      const filters = [
        { type: 'section' },
        { type: 'paragraph' },
        { level: 1 },
        { level: 2 }
      ];

      const filterResults = {};
      
      for (const filter of filters) {
        const results = this.vectorDB.findByMetadata(filter);
        filterResults[JSON.stringify(filter)] = results.length;
        console.log(`   ${JSON.stringify(filter)}: ${results.length} documents`);
      }

      console.log(`✅ Metadata Filtering Success`);
      return true;
    } catch (error) {
      console.error(`❌ Metadata Filtering Failed: ${error.message}`);
      throw error;
    }
  }

  async testChatSystem() {
    console.log('\n🧪 Testing Chat System Initialization...');
    
    try {
      const chatSystem = new RAGChatSystem();
      
      // Test context search
      const contextResults = await chatSystem.searchRelevantContext("What is Office Open XML?", 3);
      
      this.results.chat = {
        success: true,
        contextResults: contextResults.length,
        sampleContext: contextResults[0] || null
      };

      console.log(`✅ Chat System Success: ${contextResults.length} context results`);
      return true;
    } catch (error) {
      console.error(`❌ Chat System Failed: ${error.message}`);
      this.results.chat = {
        success: false,
        error: error.message
      };
      throw error;
    }
  }

  generateReport() {
    console.log('\n📊 Test Report');
    console.log('==============');
    
    const totalTests = Object.keys(this.results).length;
    const passedTests = Object.values(this.results).filter(r => r?.success).length;
    
    console.log(`Overall: ${passedTests}/${totalTests} tests passed`);
    console.log();
    
    Object.entries(this.results).forEach(([test, result]) => {
      const status = result?.success ? '✅ PASS' : '❌ FAIL';
      console.log(`${status} ${test}`);
      
      if (result?.error) {
        console.log(`       Error: ${result.error}`);
      }
    });
    
    if (this.results.pdfExtraction?.success) {
      console.log(`\n📄 PDF Processing:`);
      console.log(`   - Pages: ${this.results.pdfExtraction.totalPages}`);
      console.log(`   - Chunks: ${this.results.pdfExtraction.totalChunks}`);
      console.log(`   - Processing time: ${this.results.pdfExtraction.processingTime}ms`);
    }
    
    if (this.results.vectorStorage?.success) {
      console.log(`\n🔮 Vector Storage:`);
      console.log(`   - Documents: ${this.results.vectorStorage.documentsStored}`);
      console.log(`   - Vectors: ${this.results.vectorStorage.vectorsStored}`);
      console.log(`   - Processing time: ${this.results.vectorStorage.processingTime}ms`);
    }
    
    console.log(`\n${passedTests === totalTests ? '🎉 All tests passed!' : '⚠️ Some tests failed'}`);
  }

  async runAllTests() {
    console.log('🚀 Running RAG System Tests');
    console.log('===========================');
    
    try {
      // Test PDF extraction
      const extractedData = await this.testPDFExtraction();
      
      // Test vector storage
      await this.testVectorStorage(extractedData.chunks);
      
      // Test search functionality
      await this.testSearch();
      
      // Test metadata filtering
      await this.testMetadataFiltering();
      
      // Test chat system
      await this.testChatSystem();
      
      this.generateReport();
      
    } catch (error) {
      console.error('\n❌ Test suite failed:', error.message);
      this.generateReport();
    } finally {
      // Clean up test database
      try {
        if (fs.existsSync('./test-vector-db.json')) {
          fs.unlinkSync('./test-vector-db.json');
        }
      } catch (error) {
        console.log('Note: Could not clean up test database file');
      }
    }
  }
}

// Run tests if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const tester = new RAGSystemTest();
  tester.runAllTests();
}

export default RAGSystemTest;