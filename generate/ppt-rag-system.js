import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import VectorDatabase from './vector-db.js';
import RAGChatSystem from './rag-chat.js';
import { OpenAI } from 'openai';

dotenv.config();

class PowerPointRAGSystem {
  constructor() {
    this.vectorDB = new VectorDatabase('./ppt-vector-db.json');
    this.chatSystem = new RAGChatSystem();
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
    this.outputDir = './ppt_rag_output';
    this.processedDataPath = './ppt_rag_output/powerpoint_rag_data.json';
  }

  async processPowerPointFile(pptxPath) {
    console.log('🎯 Processing PowerPoint file with Python backend...');
    
    if (!fs.existsSync(pptxPath)) {
      throw new Error(`PowerPoint file not found: ${pptxPath}`);
    }

    try {
      // Call Python script to process PowerPoint
      const pythonScript = path.join(process.cwd(), 'ppt_rag_system.py');
      
      return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python3', [
          pythonScript,
          pptxPath,
          '--output-dir', this.outputDir,
          '--export-nodejs'
        ]);

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
          stdout += data.toString();
          console.log(data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
          stderr += data.toString();
          console.error(data.toString());
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            console.log('✅ Python processing completed successfully');
            resolve({ stdout, stderr });
          } else {
            console.error(`❌ Python process exited with code ${code}`);
            reject(new Error(`Python process failed: ${stderr}`));
          }
        });
      });
    } catch (error) {
      console.error('❌ Error running Python script:', error);
      throw error;
    }
  }

  async generateEnhancedDescriptions(processedDataPath) {
    console.log('🤖 Generating enhanced descriptions with LLM...');
    
    if (!fs.existsSync(processedDataPath)) {
      throw new Error(`Processed data not found: ${processedDataPath}`);
    }

    const data = JSON.parse(fs.readFileSync(processedDataPath, 'utf-8'));
    const enhancedEntries = [];

    for (const entry of data.documents) {
      if (entry.metadata.type === 'slide_description') {
        try {
          // Generate enhanced description using GPT
          const enhancedDescription = await this.generateSlideDescription(entry);
          
          // Create enhanced entry
          const enhancedEntry = {
            ...entry,
            id: `${entry.id}_enhanced`,
            text: enhancedDescription,
            metadata: {
              ...entry.metadata,
              type: 'enhanced_slide_description',
              original_description: entry.text
            }
          };
          
          enhancedEntries.push(enhancedEntry);
          console.log(`✅ Enhanced description for slide ${entry.metadata.slide_index + 1}`);
          
        } catch (error) {
          console.error(`❌ Error enhancing description for slide ${entry.metadata.slide_index + 1}:`, error);
          // Keep original entry if enhancement fails
          enhancedEntries.push(entry);
        }
      } else {
        // Keep non-description entries as is
        enhancedEntries.push(entry);
      }
    }

    return enhancedEntries;
  }

  async generateSlideDescription(entry) {
    const prompt = `
You are analyzing a PowerPoint slide. Based on the following information, generate a comprehensive and detailed description of the slide content:

Slide Information:
- Slide Index: ${entry.metadata.slide_index + 1}
- Current Description: ${entry.text}
- Source File: ${entry.metadata.source_file}

Please provide a detailed description that includes:
1. The main topic or theme of the slide
2. Key visual elements and their arrangement
3. Text content and its purpose
4. Any charts, graphs, or data visualizations
5. Design elements and formatting
6. The slide's role in the overall presentation

Generate a description that would be useful for someone trying to understand the slide content without seeing it.
`;

    const response = await this.openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: "You are a presentation analysis expert. Provide clear, detailed descriptions of PowerPoint slides based on available information."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      max_tokens: 500,
      temperature: 0.7
    });

    return response.choices[0].message.content;
  }

  async addToVectorDatabase(entries) {
    console.log('🔮 Adding entries to vector database...');
    
    // Convert entries to the format expected by VectorDatabase
    const chunks = entries.map(entry => ({
      id: entry.id,
      text: entry.text,
      metadata: entry.metadata
    }));

    await this.vectorDB.addDocuments(chunks);
    console.log(`✅ Added ${chunks.length} entries to vector database`);
  }

  async searchShapes(query, topK = 5) {
    console.log(`🔍 Searching for shapes: "${query}"`);
    
    const results = await this.vectorDB.search(query, topK);
    
    // Filter for shape-related results
    const shapeResults = results.filter(result => 
      result.document.metadata.type === 'shape_text' ||
      result.document.metadata.type === 'slide_description' ||
      result.document.metadata.type === 'enhanced_slide_description'
    );

    return shapeResults;
  }

  async findShapesByType(shapeType) {
    console.log(`🔍 Finding shapes of type: "${shapeType}"`);
    
    const shapeResults = this.vectorDB.findByMetadata({ 
      type: 'shape_text',
      shape_type: shapeType 
    });

    return shapeResults;
  }

  async getSlideShapes(slideIndex) {
    console.log(`🔍 Getting shapes for slide ${slideIndex + 1}`);
    
    const slideResults = this.vectorDB.findByMetadata({ 
      slide_index: slideIndex 
    });

    return slideResults;
  }

  async analyzeShapeDistribution() {
    console.log('📊 Analyzing shape distribution...');
    
    const stats = this.vectorDB.getStats();
    
    console.log('\n📈 Shape Distribution Analysis:');
    console.log('===============================');
    
    if (stats.documentTypes.shape_text) {
      console.log(`Total shapes with text: ${stats.documentTypes.shape_text}`);
    }
    
    if (stats.documentTypes.slide_description) {
      console.log(`Total slide descriptions: ${stats.documentTypes.slide_description}`);
    }
    
    if (stats.documentTypes.enhanced_slide_description) {
      console.log(`Enhanced descriptions: ${stats.documentTypes.enhanced_slide_description}`);
    }

    // Get shape type distribution
    const shapeEntries = this.vectorDB.findByMetadata({ type: 'shape_text' });
    const shapeTypes = {};
    
    shapeEntries.forEach(entry => {
      const shapeType = entry.metadata.shape_type || 'unknown';
      shapeTypes[shapeType] = (shapeTypes[shapeType] || 0) + 1;
    });
    
    console.log('\n🎨 Shape Types:');
    Object.entries(shapeTypes)
      .sort(([,a], [,b]) => b - a)
      .forEach(([type, count]) => {
        console.log(`  ${type}: ${count}`);
      });

    return { stats, shapeTypes };
  }

  async startRAGChat() {
    console.log('\n💬 Starting PowerPoint RAG Chat System');
    console.log('=====================================');
    
    // Initialize chat system with custom context
    const customContext = `
You are a PowerPoint presentation analysis assistant. You have access to detailed information about PowerPoint slides, including:
- Slide descriptions and content
- Shape data (text, positioning, types)
- Visual elements and formatting
- XML structure information

You can help users:
- Find specific shapes or content
- Analyze presentation structure
- Understand slide layouts
- Search for specific information across slides
- Provide insights about presentation design

When answering questions, provide specific slide numbers and shape details when available.
`;

    this.chatSystem.setCustomContext(customContext);
    await this.chatSystem.startChat();
  }

  async demonstrateCapabilities() {
    console.log('\n🎯 Demonstrating PowerPoint RAG Capabilities');
    console.log('===========================================');
    
    // Test searches
    const testQueries = [
      "What shapes contain text?",
      "Show me slides with charts",
      "Find rectangles on slides",
      "What's the main content of slide 1?"
    ];

    for (const query of testQueries) {
      console.log(`\n🔍 Query: "${query}"`);
      const results = await this.searchShapes(query, 3);
      
      if (results.length > 0) {
        results.forEach((result, index) => {
          console.log(`  ${index + 1}. Slide ${result.document.metadata.slide_index + 1} - ${result.document.metadata.type}`);
          console.log(`     Similarity: ${result.similarity.toFixed(3)}`);
          console.log(`     Content: ${result.document.text.substring(0, 100)}...`);
        });
      } else {
        console.log('  No results found');
      }
    }
  }

  async run(pptxPath) {
    try {
      console.log('🚀 Starting PowerPoint RAG System');
      console.log('=================================');
      
      // Step 1: Process PowerPoint file
      await this.processPowerPointFile(pptxPath);
      
      // Step 2: Generate enhanced descriptions
      const enhancedEntries = await this.generateEnhancedDescriptions(this.processedDataPath);
      
      // Step 3: Add to vector database
      await this.addToVectorDatabase(enhancedEntries);
      
      // Step 4: Analyze data
      await this.analyzeShapeDistribution();
      
      // Step 5: Demonstrate capabilities
      await this.demonstrateCapabilities();
      
      // Step 6: Start chat
      await this.startRAGChat();
      
    } catch (error) {
      console.error('❌ Error running PowerPoint RAG system:', error);
      throw error;
    }
  }
}

// Command line interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log(`
PowerPoint RAG System

Usage:
  node ppt-rag-system.js <powerpoint-file> [options]

Options:
  --help              Show this help message
  --demo-only         Only demonstrate capabilities (skip processing)
  --chat-only         Only start chat (assumes data is already processed)

Examples:
  node ppt-rag-system.js sample.pptx
  node ppt-rag-system.js sample.pptx --demo-only
  node ppt-rag-system.js sample.pptx --chat-only
`);
    process.exit(1);
  }

  const pptxPath = args[0];
  const ragSystem = new PowerPointRAGSystem();

  if (args.includes('--help')) {
    console.log('Help message shown above');
    process.exit(0);
  }

  if (args.includes('--demo-only')) {
    ragSystem.demonstrateCapabilities()
      .catch(error => console.error('❌ Error:', error));
  } else if (args.includes('--chat-only')) {
    ragSystem.startRAGChat()
      .catch(error => console.error('❌ Error:', error));
  } else {
    ragSystem.run(pptxPath)
      .catch(error => console.error('❌ Error:', error));
  }
}

export default PowerPointRAGSystem;