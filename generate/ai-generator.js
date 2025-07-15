import { generateText } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { CustomGeometryGenerator } from './custom-geometry.js';
import { ShapeExamplesExtractor } from './shape-examples-extractor.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

export class AIShapeGenerator {
  constructor() {
    if (!process.env.OPENAI_API_KEY) {
      throw new Error('OPENAI_API_KEY is required in environment variables');
    }
    this.openai = createOpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
    this.customGeometry = new CustomGeometryGenerator();
    this.shapeExamplesExtractor = new ShapeExamplesExtractor();
    this.loadPresetShapeDefinitions();
  }
  
  loadPresetShapeDefinitions() {
    try {
      // Get available shapes from the custom geometry generator
      this.availableShapeTypes = this.customGeometry.getAvailableShapes();
      
      // Get real PowerPoint shape examples from extracted slides
      this.realShapeExamples = this.shapeExamplesExtractor.generatePromptExamples();
      
      // Create examples for common shape categories (fallback)
      this.shapeExamples = this.generateShapeExamples();
      
      console.log(`🎨 Loaded ${this.shapeExamplesExtractor.getStatistics().totalExamples} real shape examples from ${this.shapeExamplesExtractor.getStatistics().totalCategories} categories`);
    } catch (error) {
      console.warn('Could not load preset shape definitions:', error.message);
      this.availableShapeTypes = [];
      this.shapeExamples = '';
      this.realShapeExamples = '';
    }
  }
  
  generateShapeExamples() {
    const examples = [
      {
        category: "Basic Shapes",
        examples: [
          { type: "ellipse", description: "Circular or oval shape" },
          { type: "diamond", description: "Diamond shape" },
          { type: "star5", description: "5-pointed star" },
          { type: "star6", description: "6-pointed star" },
          { type: "star8", description: "8-pointed star" }
        ]
      },
      {
        category: "Arrows",
        examples: [
          { type: "downArrow", description: "Downward pointing arrow" },
          { type: "upArrow", description: "Upward pointing arrow" },
          { type: "leftArrow", description: "Left pointing arrow" },
          { type: "rightArrow", description: "Right pointing arrow" },
          { type: "bentArrow", description: "Bent arrow shape" }
        ]
      },
      {
        category: "Callouts",
        examples: [
          { type: "callout1", description: "Simple callout bubble" },
          { type: "callout2", description: "Callout with line" },
          { type: "cloudCallout", description: "Cloud-shaped callout" }
        ]
      },
      {
        category: "Flowchart",
        examples: [
          { type: "flowChartProcess", description: "Process rectangle" },
          { type: "flowChartDecision", description: "Decision diamond" },
          { type: "flowChartDocument", description: "Document shape" },
          { type: "flowChartTerminator", description: "Start/end oval" }
        ]
      },
      {
        category: "3D Objects",
        examples: [
          { type: "cube", description: "3D cube shape" },
          { type: "can", description: "Cylinder shape" },
          { type: "bevel", description: "Beveled rectangle" }
        ]
      }
    ];
    
    return examples.map(category => {
      const exampleList = category.examples.map(ex => 
        `    - ${ex.type}: ${ex.description}`
      ).join('\n');
      return `${category.category}:\n${exampleList}`;
    }).join('\n\n');
  }
  
  async generateShapeFromPrompt(userPrompt) {
    try {
      const systemPrompt = `You are an expert in PowerPoint OpenXML shape generation with access to real PowerPoint shape examples and comprehensive preset shape definitions. 
Your task is to analyze the user's prompt and generate shape parameters that will be used to create OpenXML shapes in a PowerPoint slide.

CRITICAL: You must respond with ONLY valid JSON. No explanations, no additional text, just the JSON object.

Return exactly this JSON structure:
{
  "shapes": [
    {
      "id": 2,
      "name": "descriptive_name",
      "x": 914400,
      "y": 457200,
      "width": 7315200,
      "height": 914400,
      "text": "text_content",
      "type": "ellipse"
    }
  ]
}

${this.realShapeExamples || ''}

AVAILABLE PRESET SHAPE TYPES:
You have access to ${this.availableShapeTypes.length} preset shape types from the PowerPoint OpenXML specification. 
Here are the main categories with examples:

${this.shapeExamples}

SHAPE TYPE SELECTION GUIDELINES:
- Study the REAL POWERPOINT SHAPE EXAMPLES above to understand proper OpenXML structure
- For geometric shapes: Use "ellipse", "diamond", "star5", "star6", "star8", etc.
- For arrows: Use "downArrow", "upArrow", "leftArrow", "rightArrow", "bentArrow"
- For callouts: Use "callout1", "callout2", "cloudCallout"
- For flowcharts: Use "flowChartProcess", "flowChartDecision", "flowChartDocument", "flowChartTerminator"
- For 3D objects: Use "cube", "can", "bevel"
- For text-only: Use "textBox" (fallback)
- Prefer shapes that match the patterns shown in the real examples above

POSITIONING GUIDELINES:
- EMU (English Metric Units): 1 inch = 914400 EMU
- Slide dimensions: approximately 9144000 EMU width x 6858000 EMU height
- Position (0,0) is top-left corner
- Generate realistic positions and sizes that fit within the slide
- Create meaningful text content based on the user's request
- You can create multiple shapes if the prompt suggests it
- Use incremental numeric IDs starting from 2 (ID 1 is reserved for the slide group)
- All numeric values should be integers, not strings

POSITIONING EXAMPLES:
- Title: x=914400, y=457200, width=7315200, height=914400
- Body text: x=914400, y=1828800, width=7315200, height=2743200
- Small shape: x=2286000, y=2286000, width=1828800, height=914400
- Large shape: x=1371600, y=1371600, width=6400800, height=4114800

FEW-SHOT EXAMPLES:

Example 1 - User: "Create a star shape with Welcome"
{
  "shapes": [
    {
      "id": 2,
      "name": "welcome_star",
      "x": 2286000,
      "y": 1828800,
      "width": 4572000,
      "height": 3200400,
      "text": "Welcome",
      "type": "star5"
    }
  ]
}

Example 2 - User: "Create a flowchart with start and process"
{
  "shapes": [
    {
      "id": 2,
      "name": "start_shape",
      "x": 3657600,
      "y": 914400,
      "width": 1828800,
      "height": 914400,
      "text": "Start",
      "type": "flowChartTerminator"
    },
    {
      "id": 3,
      "name": "process_shape",
      "x": 3657600,
      "y": 2286000,
      "width": 1828800,
      "height": 914400,
      "text": "Process",
      "type": "flowChartProcess"
    }
  ]
}

Example 3 - User: "Create a diamond shape"
{
  "shapes": [
    {
      "id": 2,
      "name": "diamond_shape",
      "x": 2743200,
      "y": 2286000,
      "width": 3657600,
      "height": 2286000,
      "text": "Diamond",
      "type": "diamond"
    }
  ]
}

RESPOND WITH ONLY THE JSON OBJECT, NO OTHER TEXT.`;

      const { text } = await generateText({
        model: this.openai('gpt-4'),
        system: systemPrompt,
        prompt: userPrompt,
        temperature: 0.7,
      });
      
      // Parse the JSON response
      const cleanedText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      const shapeData = JSON.parse(cleanedText);
      
      // Validate the response structure
      if (!shapeData.shapes || !Array.isArray(shapeData.shapes)) {
        throw new Error('Invalid shape data structure');
      }
      
      // Validate each shape
      shapeData.shapes.forEach((shape, index) => {
        const required = ['id', 'name', 'x', 'y', 'width', 'height', 'text'];
        required.forEach(field => {
          if (!shape.hasOwnProperty(field)) {
            throw new Error(`Shape ${index} missing required field: ${field}`);
          }
        });
      });
      
      return shapeData;
    } catch (error) {
      console.error('Error generating shape from prompt:', error);
      throw error;
    }
  }
  
  async generateShapeXmlFromPrompt(userPrompt) {
    try {
      const shapeData = await this.generateShapeFromPrompt(userPrompt);
      
      // Convert shape data to XML
      const shapeXmlArray = shapeData.shapes.map(shape => {
        return this.generateShapeXml(shape);
      });
      
      return shapeXmlArray.join('\n');
    } catch (error) {
      console.error('Error generating shape XML from prompt:', error);
      throw error;
    }
  }
  
  generateShapeXml(shapeData) {
    const { id, name, x, y, width, height, text, type = 'textBox' } = shapeData;
    
    // Generate custom geometry using the custom geometry generator
    let geometryXml = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>';
    
    if (type === 'textBox') {
      geometryXml = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>';
    } else if (this.availableShapeTypes.includes(type)) {
      // Use custom geometry from the preset definitions
      geometryXml = this.customGeometry.generateCustomGeometry(type, width, height, 0, 0);
    } else {
      // Fallback mappings for common shape types
      switch (type) {
        case 'circle':
          geometryXml = this.customGeometry.generateCustomGeometry('ellipse', width, height, 0, 0);
          break;
        case 'rectangle':
          geometryXml = this.customGeometry.generateRectangleGeometry(width, height);
          break;
        case 'triangle':
          geometryXml = this.customGeometry.generateCustomGeometry('triangle', width, height, 0, 0);
          break;
        case 'arrow':
          geometryXml = this.customGeometry.generateCustomGeometry('rightArrow', width, height, 0, 0);
          break;
        default:
          geometryXml = this.customGeometry.generateRectangleGeometry(width, height);
      }
    }
    
    // Choose colors based on shape type
    let fillColor = "E6E6FA"; // Default light purple
    let lineColor = "000000"; // Default black
    
    if (type.includes('star')) {
      fillColor = "FFD700"; // Gold for stars
    } else if (type.includes('Arrow') || type.includes('arrow')) {
      fillColor = "87CEEB"; // Sky blue for arrows
    } else if (type.includes('flowChart')) {
      fillColor = "F0F8FF"; // Alice blue for flowchart
    } else if (type.includes('callout')) {
      fillColor = "FFFACD"; // Lemon chiffon for callouts
    } else if (type === 'diamond') {
      fillColor = "DDA0DD"; // Plum for diamond
    } else if (type === 'ellipse') {
      fillColor = "98FB98"; // Pale green for ellipse
    } else if (type === 'cube' || type === 'can' || type === 'bevel') {
      fillColor = "D3D3D3"; // Light gray for 3D objects
    }
    
    const shapeXml = `
      <p:sp>
        <p:nvSpPr>
          <p:cNvPr id="${id}" name="${name}"/>
          <p:cNvSpPr/>
          <p:nvPr/>
        </p:nvSpPr>
        <p:spPr>
          <a:xfrm>
            <a:off x="${x}" y="${y}"/>
            <a:ext cx="${width}" cy="${height}"/>
          </a:xfrm>
          ${geometryXml}
          <a:solidFill>
            <a:srgbClr val="${fillColor}"/>
          </a:solidFill>
          <a:ln w="12700">
            <a:solidFill>
              <a:srgbClr val="${lineColor}"/>
            </a:solidFill>
          </a:ln>
        </p:spPr>
        <p:txBody>
          <a:bodyPr/>
          <a:lstStyle/>
          <a:p>
            <a:r>
              <a:rPr lang="en-US" sz="1800"/>
              <a:t>${text}</a:t>
            </a:r>
          </a:p>
        </p:txBody>
      </p:sp>`;
    
    return shapeXml;
  }
  
  getShapeExamplesStatistics() {
    return this.shapeExamplesExtractor.getStatistics();
  }
  
  getAvailableCategories() {
    return this.shapeExamplesExtractor.getAllCategories();
  }
  
  logShapeExamplesInfo() {
    const stats = this.getShapeExamplesStatistics();
    console.log('\n📊 Shape Examples Statistics:');
    console.log(`Total Categories: ${stats.totalCategories}`);
    console.log(`Total Examples: ${stats.totalExamples}`);
    console.log('\nCategory Breakdown:');
    Object.entries(stats.categoryBreakdown).forEach(([category, count]) => {
      console.log(`  ${category}: ${count} examples`);
    });
    console.log('');
  }
}