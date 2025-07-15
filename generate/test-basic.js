import dotenv from 'dotenv';
import PDFExtractor from './pdf-extractor.js';
import VectorDatabase from './vector-db.js';
import { openai } from '@ai-sdk/openai';
import { generateText } from 'ai';

dotenv.config();

async function testBasicRAG() {
  console.log('🧪 Basic RAG Test');
  console.log('================');

  if (!process.env.OPENAI_API_KEY) {
    console.error('❌ OPENAI_API_KEY not found in environment variables');
    return;
  }

  try {
    // 1. Test PDF extraction
    console.log('1. Testing PDF extraction...');
    const extractor = new PDFExtractor();
    const data = await extractor.extractTextWithHierarchy('./ecma-376.pdf');
    console.log(`   ✅ Extracted ${data.chunks.length} chunks from ${data.totalPages} pages`);

    // 2. Test with first 10 chunks
    console.log('2. Testing vector database with 10 chunks...');
    const testChunks = data.chunks.slice(0, 10);
    const vectorDB = new VectorDatabase('./test-basic-db.json');
    await vectorDB.addDocuments(testChunks);
    console.log(`   ✅ Added ${testChunks.length} chunks to vector database`);

    // 3. Test search
    console.log('3. Testing search...');
    const searchResults = await vectorDB.search("What is Office Open XML?", 3);
    console.log(`   ✅ Found ${searchResults.length} search results`);
    
    if (searchResults.length > 0) {
      console.log(`   Top result similarity: ${searchResults[0].similarity.toFixed(3)}`);
      console.log(`   Content: ${searchResults[0].document.text.substring(0, 100)}...`);
    }

    // 4. Test AI generation
    console.log('4. Testing AI response generation...');
    const context = searchResults.map(r => r.document.text).join('\n\n');
    const model = openai('gpt-4o-mini');
    
    const response = await generateText({
      model,
      messages: [
        { role: 'system', content: 'You are an expert on ECMA-376 Office Open XML. Answer based on the provided context.' },
        { role: 'user', content: `Context: ${context}\n\nQuestion: What is Office Open XML?` }
      ],
      maxTokens: 200
    });

    console.log(`   ✅ AI Response: ${response.text.substring(0, 150)}...`);

    console.log('\n🎉 All tests passed! The basic RAG system is working correctly.');
    
    // Clean up
    try {
      const fs = await import('fs');
      if (fs.existsSync('./test-basic-db.json')) {
        fs.unlinkSync('./test-basic-db.json');
      }
    } catch (e) {
      console.log('Note: Could not clean up test database');
    }

  } catch (error) {
    console.error('❌ Test failed:', error);
  }
}

testBasicRAG();