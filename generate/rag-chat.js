import { openai } from '@ai-sdk/openai';
import { generateText, streamText } from 'ai';
import VectorDatabase from './vector-db.js';
import readline from 'readline';

class RAGChatSystem {
  constructor() {
    this.vectorDB = new VectorDatabase();
    this.model = openai('gpt-4o-mini');
    this.chatHistory = [];
    this.rl = null;
  }

  setupReadline() {
    if (this.rl) {
      this.rl.close();
    }
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async searchRelevantContext(query, topK = 5) {
    const results = await this.vectorDB.search(query, topK);
    
    return results.map(result => ({
      text: result.document.text,
      metadata: result.document.metadata,
      similarity: result.similarity
    }));
  }

  formatContextForPrompt(contextResults) {
    if (contextResults.length === 0) {
      return "No relevant context found in the ECMA-376 document.";
    }

    let contextText = "Relevant context from ECMA-376 document:\n\n";
    
    contextResults.forEach((result, index) => {
      contextText += `Context ${index + 1} (${result.metadata.type}, Level ${result.metadata.level}):\n`;
      contextText += `Section: ${result.metadata.section || 'Unknown'}\n`;
      contextText += `Similarity: ${result.similarity.toFixed(3)}\n`;
      contextText += `Content: ${result.text}\n\n`;
    });

    return contextText;
  }

  buildSystemPrompt() {
    return `You are an expert assistant for the ECMA-376 Office Open XML File Formats standard. 
You have access to the complete ECMA-376 document through a vector database search system.

Your role is to:
1. Answer questions about the ECMA-376 standard accurately
2. Provide specific references to sections when possible
3. Explain technical concepts in a clear and structured way
4. Help users understand Office Open XML file formats
5. Reference the document hierarchy and structure when relevant

When answering:
- Use the provided context to give accurate information
- Reference specific sections or parts of the document when applicable
- If the context doesn't contain enough information, say so clearly
- Provide practical examples when helpful
- Maintain technical accuracy while being accessible

The context provided includes hierarchical metadata about document structure, so you can reference specific sections, subsections, and document organization.`;
  }

  async generateResponse(userMessage, contextResults) {
    const systemPrompt = this.buildSystemPrompt();
    const context = this.formatContextForPrompt(contextResults);
    
    const messages = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: `Context:\n${context}\n\nUser Question: ${userMessage}` }
    ];

    // Add chat history for context
    this.chatHistory.forEach(msg => {
      messages.push(msg);
    });

    try {
      const result = await generateText({
        model: this.model,
        messages: messages,
        temperature: 0.7,
        maxTokens: 1000
      });

      return result.text;
    } catch (error) {
      console.error('Error generating response:', error);
      return 'I apologize, but I encountered an error generating a response. Please try again.';
    }
  }

  async generateStreamResponse(userMessage, contextResults) {
    const systemPrompt = this.buildSystemPrompt();
    const context = this.formatContextForPrompt(contextResults);
    
    const messages = [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: `Context:\n${context}\n\nUser Question: ${userMessage}` }
    ];

    // Add chat history for context
    this.chatHistory.forEach(msg => {
      messages.push(msg);
    });

    try {
      const result = await streamText({
        model: this.model,
        messages: messages,
        temperature: 0.7,
        maxTokens: 1000
      });

      return result;
    } catch (error) {
      console.error('Error generating stream response:', error);
      return null;
    }
  }

  async processQuery(userMessage, useStreaming = false) {
    console.log('\n🔍 Searching for relevant context...');
    
    // Search for relevant context
    const contextResults = await this.searchRelevantContext(userMessage);
    
    console.log(`📚 Found ${contextResults.length} relevant passages`);
    
    if (contextResults.length > 0) {
      console.log('📊 Context relevance scores:');
      contextResults.forEach((result, index) => {
        console.log(`  ${index + 1}. ${result.similarity.toFixed(3)} - ${result.metadata.section || 'Unknown section'}`);
      });
    }

    console.log('\n🤖 Generating response...\n');

    if (useStreaming) {
      const stream = await this.generateStreamResponse(userMessage, contextResults);
      if (stream) {
        process.stdout.write('Assistant: ');
        for await (const chunk of stream.textStream) {
          process.stdout.write(chunk);
        }
        console.log('\n');
      }
    } else {
      const response = await this.generateResponse(userMessage, contextResults);
      console.log('Assistant:', response);
    }

    // Update chat history
    this.chatHistory.push({ role: 'user', content: userMessage });
    
    // Keep only last 10 messages to avoid token limits
    if (this.chatHistory.length > 10) {
      this.chatHistory = this.chatHistory.slice(-10);
    }
  }

  async startChat() {
    console.log('🚀 RAG Chat System for ECMA-376 Document');
    console.log('======================================');
    
    // Setup fresh readline interface
    this.setupReadline();
    
    const stats = this.vectorDB.getStats();
    console.log(`📊 Database stats: ${stats.totalDocuments} documents loaded`);
    console.log('💬 Type your questions about ECMA-376. Type "exit" to quit, "stats" for database info, "stream" to toggle streaming mode.\n');

    let useStreaming = false;

    const askQuestion = () => {
      this.rl.question('You: ', async (input) => {
        const message = input.trim();
        
        if (message.toLowerCase() === 'exit') {
          console.log('👋 Goodbye!');
          this.rl.close();
          return;
        }
        
        if (message.toLowerCase() === 'stats') {
          console.log('\n📊 Database Statistics:');
          console.log(JSON.stringify(stats, null, 2));
          console.log('');
          askQuestion();
          return;
        }
        
        if (message.toLowerCase() === 'stream') {
          useStreaming = !useStreaming;
          console.log(`🔄 Streaming mode: ${useStreaming ? 'ON' : 'OFF'}\n`);
          askQuestion();
          return;
        }
        
        if (message) {
          await this.processQuery(message, useStreaming);
        }
        
        askQuestion();
      });
    };

    askQuestion();
  }

  async searchByMetadata(filters) {
    return this.vectorDB.findByMetadata(filters);
  }

  getVectorDBStats() {
    return this.vectorDB.getStats();
  }

  close() {
    if (this.rl) {
      this.rl.close();
    }
  }
}

export default RAGChatSystem;