import dotenv from 'dotenv';
import readline from 'readline';
import { OpenAI } from 'openai';
import VectorDatabase from './vector-db.js';

dotenv.config();

class PowerPointRAGChat {
  constructor(vectorDbPath = './ppt-vector-db.json') {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    this.vectorDB = new VectorDatabase(vectorDbPath);
    this.conversationHistory = [];
  }

  async searchRelevantContent(query, topK = 5) {
    // Search for relevant content
    const results = await this.vectorDB.search(query, topK);
    
    // Group results by type for better context
    const groupedResults = {
      slide_descriptions: [],
      enhanced_descriptions: [],
      shape_text: [],
      other: []
    };

    results.forEach(result => {
      const type = result.document.metadata.type;
      if (type === 'slide_description') {
        groupedResults.slide_descriptions.push(result);
      } else if (type === 'enhanced_slide_description') {
        groupedResults.enhanced_descriptions.push(result);
      } else if (type === 'shape_text') {
        groupedResults.shape_text.push(result);
      } else {
        groupedResults.other.push(result);
      }
    });

    return groupedResults;
  }

  buildContextFromResults(groupedResults) {
    let context = '';

    // Add enhanced descriptions first (most comprehensive)
    if (groupedResults.enhanced_descriptions.length > 0) {
      context += '\n=== Slide Descriptions ===\n';
      groupedResults.enhanced_descriptions.forEach(result => {
        context += `Slide ${result.document.metadata.slide_index + 1}: ${result.document.text}\n\n`;
      });
    }

    // Add slide descriptions if no enhanced ones
    if (groupedResults.enhanced_descriptions.length === 0 && groupedResults.slide_descriptions.length > 0) {
      context += '\n=== Slide Descriptions ===\n';
      groupedResults.slide_descriptions.forEach(result => {
        context += `Slide ${result.document.metadata.slide_index + 1}: ${result.document.text}\n\n`;
      });
    }

    // Add shape-specific information
    if (groupedResults.shape_text.length > 0) {
      context += '\n=== Shape Information ===\n';
      groupedResults.shape_text.forEach(result => {
        const meta = result.document.metadata;
        context += `Slide ${meta.slide_index + 1}, Shape "${meta.shape_name || 'unnamed'}" (${meta.shape_type}): ${result.document.text}\n`;
        
        // Add positioning info if available
        if (meta.shape_data) {
          const pos = meta.shape_data;
          context += `  Position: (${pos.left}, ${pos.top}), Size: ${pos.width}x${pos.height}\n`;
        }
        context += '\n';
      });
    }

    return context;
  }

  async generateResponse(userQuery, context) {
    const systemPrompt = `You are a PowerPoint presentation analysis assistant. You have access to detailed information about PowerPoint slides including descriptions, shape data, and positioning.

Your capabilities include:
- Analyzing slide content and structure
- Finding specific shapes, text, or elements
- Providing insights about presentation design
- Answering questions about slide layouts
- Explaining visual elements and their relationships

When answering:
- Always reference specific slide numbers when relevant
- Provide detailed information about shapes, including their types and positions
- Be specific about what you find in the presentation
- If you don't find relevant information, say so clearly
- Offer to help with related questions

Context from the presentation:
${context}

Previous conversation:
${this.conversationHistory.slice(-4).map(msg => `${msg.role}: ${msg.content}`).join('\n')}`;

    const response = await this.openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: systemPrompt
        },
        {
          role: "user",
          content: userQuery
        }
      ],
      max_tokens: 1000,
      temperature: 0.7
    });

    return response.choices[0].message.content;
  }

  async handleSpecialCommands(input) {
    const command = input.toLowerCase().trim();

    if (command === '/stats') {
      const stats = this.vectorDB.getStats();
      console.log('\n📊 Presentation Statistics:');
      console.log('===========================');
      console.log(`Total entries: ${stats.totalDocuments}`);
      console.log('\nEntry types:');
      Object.entries(stats.documentTypes).forEach(([type, count]) => {
        console.log(`  ${type}: ${count}`);
      });
      return true;
    }

    if (command === '/shapes') {
      const shapeEntries = this.vectorDB.findByMetadata({ type: 'shape_text' });
      const shapeTypes = {};
      
      shapeEntries.forEach(entry => {
        const shapeType = entry.metadata.shape_type || 'unknown';
        shapeTypes[shapeType] = (shapeTypes[shapeType] || 0) + 1;
      });
      
      console.log('\n🎨 Shape Types in Presentation:');
      console.log('===============================');
      Object.entries(shapeTypes)
        .sort(([,a], [,b]) => b - a)
        .forEach(([type, count]) => {
          console.log(`  ${type}: ${count}`);
        });
      return true;
    }

    if (command.startsWith('/slide ')) {
      const slideNum = parseInt(command.split(' ')[1]) - 1;
      const slideResults = this.vectorDB.findByMetadata({ slide_index: slideNum });
      
      console.log(`\n📄 Slide ${slideNum + 1} Information:`);
      console.log('===============================');
      
      if (slideResults.length === 0) {
        console.log('No information found for this slide.');
        return true;
      }

      slideResults.forEach(entry => {
        console.log(`Type: ${entry.metadata.type}`);
        if (entry.metadata.type === 'shape_text') {
          console.log(`Shape: ${entry.metadata.shape_name || 'unnamed'} (${entry.metadata.shape_type})`);
        }
        console.log(`Content: ${entry.text.substring(0, 200)}${entry.text.length > 200 ? '...' : ''}`);
        console.log('---');
      });
      return true;
    }

    if (command === '/help') {
      console.log(`
💡 PowerPoint RAG Chat Commands:
================================

Questions you can ask:
- "What shapes are on slide 2?"
- "Find all text boxes in the presentation"
- "What's the main content of slide 1?"
- "Show me all rectangles"
- "What charts are in the presentation?"

Special commands:
- /stats          - Show presentation statistics
- /shapes         - List all shape types in presentation
- /slide N        - Show information for slide N
- /help           - Show this help message
- /exit or /quit  - Exit the chat

Examples:
- "Find slides with the word 'revenue'"
- "What shapes contain financial data?"
- "Show me the layout of slide 3"
- "List all text on slide 1"
`);
      return true;
    }

    return false;
  }

  async startChat() {
    console.log('\n💬 PowerPoint RAG Chat System');
    console.log('=============================');
    console.log('Ask questions about the PowerPoint presentation!');
    console.log('Type /help for available commands or /exit to quit.\n');

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const askQuestion = () => {
      rl.question('You: ', async (input) => {
        const userInput = input.trim();

        if (userInput.toLowerCase() === '/exit' || userInput.toLowerCase() === '/quit') {
          console.log('\n👋 Thank you for using PowerPoint RAG Chat!');
          rl.close();
          return;
        }

        if (!userInput) {
          askQuestion();
          return;
        }

        try {
          // Handle special commands
          if (await this.handleSpecialCommands(userInput)) {
            askQuestion();
            return;
          }

          // Search for relevant content
          const groupedResults = await this.searchRelevantContent(userInput, 5);
          
          // Build context
          const context = this.buildContextFromResults(groupedResults);
          
          if (!context.trim()) {
            console.log('\n🤖 Assistant: I don\'t have information about that in the presentation. Could you try rephrasing your question or asking about specific slides or shapes?');
            askQuestion();
            return;
          }

          // Generate response
          const response = await this.generateResponse(userInput, context);
          
          console.log(`\n🤖 Assistant: ${response}`);
          
          // Update conversation history
          this.conversationHistory.push(
            { role: 'user', content: userInput },
            { role: 'assistant', content: response }
          );

          // Keep only last 10 messages
          if (this.conversationHistory.length > 10) {
            this.conversationHistory = this.conversationHistory.slice(-10);
          }

        } catch (error) {
          console.error('\n❌ Error:', error.message);
        }

        askQuestion();
      });
    };

    askQuestion();
  }
}

// Command line interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  
  let dbPath = './ppt-vector-db.json';
  if (args.length > 0) {
    dbPath = args[0];
  }

  const chat = new PowerPointRAGChat(dbPath);
  chat.startChat().catch(error => console.error('❌ Error:', error));
}

export default PowerPointRAGChat;