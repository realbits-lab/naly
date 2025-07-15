import RAGSystem from './rag-system.js';
import dotenv from 'dotenv';

dotenv.config();

// Sample demonstration of the RAG system
async function demoRAGSystem() {
  console.log('🚀 RAG System Demo for ECMA-376 Document');
  console.log('========================================');
  
  if (!process.env.OPENAI_API_KEY) {
    console.error('❌ OPENAI_API_KEY not found in environment variables');
    console.log('Please copy .env.example to .env and add your OpenAI API key');
    return;
  }

  const ragSystem = new RAGSystem();

  try {
    // Initialize the system
    await ragSystem.initializeSystem();
    
    // Show system statistics
    await ragSystem.showStatistics();
    
    // Test various searches
    console.log('\n🔍 Testing Search Capabilities');
    console.log('============================');
    
    const testQueries = [
      "What is Office Open XML?",
      "How are relationships defined in OOXML?",
      "What are the main parts of a SpreadsheetML document?",
      "How does WordprocessingML handle styles?",
      "What are the security considerations for OOXML?",
      "How are themes implemented in PresentationML?"
    ];
    
    for (const query of testQueries) {
      console.log(`\n📋 Query: "${query}"`);
      await ragSystem.testSearch(query);
    }
    
    // Demonstrate metadata search
    await ragSystem.demonstrateMetadataSearch();
    
    console.log('\n✅ Demo complete! You can now start the chat system.');
    console.log('Run: node rag-system.js --chat-only');
    
  } catch (error) {
    console.error('❌ Demo failed:', error);
  }
}

// Interactive demo mode
async function interactiveDemo() {
  const ragSystem = new RAGSystem();
  
  console.log('\n🎮 Interactive Demo Mode');
  console.log('========================');
  console.log('This will run the full RAG system with chat interface');
  console.log('Commands available during chat:');
  console.log('- "stats" - Show database statistics');
  console.log('- "stream" - Toggle streaming mode');
  console.log('- "exit" - Exit the chat');
  console.log('');
  
  await ragSystem.run();
}

// Command line interface
const mode = process.argv[2];

if (mode === 'demo') {
  demoRAGSystem();
} else if (mode === 'interactive' || !mode) {
  interactiveDemo();
} else {
  console.log(`
Usage: node demo-rag.js [mode]

Modes:
  demo        - Run demonstration without chat
  interactive - Run full interactive system (default)
  
Examples:
  node demo-rag.js demo        # Run demo only
  node demo-rag.js interactive # Run interactive chat
  node demo-rag.js            # Run interactive chat (default)
  `);
}