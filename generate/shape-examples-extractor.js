import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export class ShapeExamplesExtractor {
  constructor() {
    this.shapeExamples = new Map();
    this.slidesPath = path.join(__dirname, 'sample1', 'ppt', 'slides');
    this.loadShapeExamples();
  }
  
  loadShapeExamples() {
    try {
      if (!fs.existsSync(this.slidesPath)) {
        console.warn('Sample slides directory not found');
        return;
      }
      
      // Get all slide XML files
      const slideFiles = fs.readdirSync(this.slidesPath)
        .filter(file => file.startsWith('slide') && file.endsWith('.xml'))
        .sort((a, b) => {
          const matchA = a.match(/\d+/);
          const matchB = b.match(/\d+/);
          if (!matchA || !matchB) return 0;
          const numA = parseInt(matchA[0]);
          const numB = parseInt(matchB[0]);
          return numA - numB;
        });
      
      console.log(`📄 Found ${slideFiles.length} slide files to analyze`);
      
      // Process first 10 slides to get a good variety of examples
      const sampleSlides = slideFiles.slice(0, 10);
      
      for (const slideFile of sampleSlides) {
        this.extractShapesFromSlide(slideFile);
      }
      
      console.log(`🎨 Extracted examples: ${this.shapeExamples.size} categories`);
      
    } catch (error) {
      console.warn('Error loading shape examples:', error.message);
    }
  }
  
  extractShapesFromSlide(slideFile) {
    try {
      const slidePath = path.join(this.slidesPath, slideFile);
      const slideContent = fs.readFileSync(slidePath, 'utf8');
      
      // Extract all <p:sp> elements (individual shapes)
      const shapeMatches = slideContent.match(/<p:sp[^>]*>(.*?)<\/p:sp>/gs);
      
      if (shapeMatches) {
        for (const shapeMatch of shapeMatches) {
          this.categorizeAndStoreShape(shapeMatch, slideFile);
        }
      }
      
    } catch (error) {
      console.warn(`Error processing ${slideFile}:`, error.message);
    }
  }
  
  categorizeAndStoreShape(shapeXml, sourceFile) {
    try {
      const shape = this.parseShapeXml(shapeXml);
      if (!shape) return;
      
      // Determine shape category
      let category = 'basic';
      
      if (shape.hasCustomGeometry) {
        if (shape.pathCommands.includes('cubicBezTo')) {
          category = 'custom_bezier';
        } else {
          category = 'custom_geometry';
        }
      } else if (shape.hasPresetGeometry) {
        category = `preset_${shape.presetType}`;
      } else if (shape.isTextBox) {
        category = 'text_box';
      }
      
      // Store unique examples (avoid duplicates)
      if (!this.shapeExamples.has(category)) {
        this.shapeExamples.set(category, []);
      }
      
      const examples = this.shapeExamples.get(category);
      if (examples.length < 3) { // Limit to 3 examples per category
        examples.push({
          xml: this.cleanShapeXml(shapeXml),
          source: sourceFile,
          description: this.generateShapeDescription(shape),
          properties: shape
        });
      }
      
    } catch (error) {
      console.warn('Error categorizing shape:', error.message);
    }
  }
  
  parseShapeXml(shapeXml) {
    try {
      const shape = {
        hasCustomGeometry: shapeXml.includes('<a:custGeom>'),
        hasPresetGeometry: shapeXml.includes('<a:prstGeom'),
        isTextBox: shapeXml.includes('txBox="1"'),
        pathCommands: [],
        presetType: null,
        fillType: null,
        hasEffects: shapeXml.includes('<a:effectLst>'),
        hasTransform: shapeXml.includes('<a:xfrm>')
      };
      
      // Extract preset geometry type
      const presetMatch = shapeXml.match(/<a:prstGeom prst="([^"]*)">/);
      if (presetMatch) {
        shape.presetType = presetMatch[1];
      }
      
      // Extract path commands for custom geometry
      const pathCommands = [];
      if (shape.hasCustomGeometry) {
        const moveToMatches = shapeXml.match(/<a:moveTo>/g);
        const lnToMatches = shapeXml.match(/<a:lnTo>/g);
        const cubicBezToMatches = shapeXml.match(/<a:cubicBezTo>/g);
        const closeMatches = shapeXml.match(/<a:close>/g);
        
        if (moveToMatches) pathCommands.push(...moveToMatches.map(() => 'moveTo'));
        if (lnToMatches) pathCommands.push(...lnToMatches.map(() => 'lnTo'));
        if (cubicBezToMatches) pathCommands.push(...cubicBezToMatches.map(() => 'cubicBezTo'));
        if (closeMatches) pathCommands.push(...closeMatches.map(() => 'close'));
      }
      shape.pathCommands = pathCommands;
      
      // Extract fill type
      if (shapeXml.includes('<a:solidFill>')) {
        if (shapeXml.includes('<a:schemeClr')) {
          shape.fillType = 'schemeColor';
        } else if (shapeXml.includes('<a:srgbClr')) {
          shape.fillType = 'rgbColor';
        } else {
          shape.fillType = 'solidFill';
        }
      } else if (shapeXml.includes('<a:noFill')) {
        shape.fillType = 'noFill';
      }
      
      return shape;
      
    } catch (error) {
      console.warn('Error parsing shape XML:', error.message);
      return null;
    }
  }
  
  cleanShapeXml(shapeXml) {
    // Remove excessive whitespace and format for readability
    return shapeXml
      .replace(/\\s+/g, ' ')
      .replace(/> </g, '>\\n<')
      .trim();
  }
  
  generateShapeDescription(shape) {
    let description = '';
    
    if (shape.isTextBox) {
      description = 'Text box';
    } else if (shape.hasCustomGeometry) {
      if (shape.pathCommands.includes('cubicBezTo')) {
        description = 'Custom shape with curved paths';
      } else {
        description = 'Custom geometric shape';
      }
    } else if (shape.hasPresetGeometry) {
      description = `Preset shape: ${shape.presetType}`;
    } else {
      description = 'Basic shape';
    }
    
    if (shape.fillType) {
      description += ` with ${shape.fillType}`;
    }
    
    if (shape.hasEffects) {
      description += ' and effects';
    }
    
    return description;
  }
  
  getExamplesByCategory(category) {
    return this.shapeExamples.get(category) || [];
  }
  
  getAllCategories() {
    return Array.from(this.shapeExamples.keys());
  }
  
  generateFewShotExamples() {
    const examples = [];
    
    // Add examples from different categories
    const priorityCategories = [
      'text_box',
      'custom_geometry', 
      'custom_bezier',
      'preset_rect',
      'preset_blockArc'
    ];
    
    for (const category of priorityCategories) {
      const categoryExamples = this.getExamplesByCategory(category);
      if (categoryExamples.length > 0) {
        const example = categoryExamples[0]; // Take the first example
        examples.push({
          category,
          description: example.description,
          xml: this.simplifyExampleXml(example.xml)
        });
      }
    }
    
    // Add any remaining categories up to a limit
    const remainingCategories = this.getAllCategories()
      .filter(cat => !priorityCategories.includes(cat))
      .slice(0, 3);
    
    for (const category of remainingCategories) {
      const categoryExamples = this.getExamplesByCategory(category);
      if (categoryExamples.length > 0) {
        const example = categoryExamples[0];
        examples.push({
          category,
          description: example.description,
          xml: this.simplifyExampleXml(example.xml)
        });
      }
    }
    
    return examples;
  }
  
  simplifyExampleXml(xmlString) {
    // Simplify XML for use in prompts by removing some verbose attributes
    return xmlString
      .replace(/\\s*(xmlns[^=]*="[^"]*")/g, '') // Remove xmlns declarations
      .replace(/\\s*(id="[^"]*")/g, '') // Remove id attributes
      .replace(/\\s*(name="[^"]*")/g, '') // Remove name attributes
      .replace(/\\s+/g, ' ') // Normalize whitespace
      .trim();
  }
  
  generatePromptExamples() {
    const fewShotExamples = this.generateFewShotExamples();
    
    let promptText = '\\n\\n## REAL POWERPOINT SHAPE EXAMPLES\\n\\n';
    promptText += 'Here are actual OpenXML shape examples from PowerPoint files to guide your generation:\\n\\n';
    
    for (const example of fewShotExamples) {
      promptText += `### ${example.category.toUpperCase().replace(/_/g, ' ')}\\n`;
      promptText += `Description: ${example.description}\\n`;
      promptText += '```xml\\n';
      promptText += example.xml;
      promptText += '\\n```\\n\\n';
    }
    
    promptText += '**GENERATION GUIDELINES:**\\n';
    promptText += '- Use `<a:custGeom>` for custom shapes with `<a:pathLst>` containing path commands\\n';
    promptText += '- Use `<a:prstGeom prst="shape_name">` for standard preset shapes\\n';
    promptText += '- Include proper `<a:xfrm>` for positioning with `<a:off>` and `<a:ext>`\\n';
    promptText += '- Use `<a:solidFill>` with `<a:schemeClr>` or `<a:srgbClr>` for colors\\n';
    promptText += '- Add `<p:txBody>` for text content with proper formatting\\n';
    promptText += '- Include `txBox="1"` in `<p:cNvSpPr>` for text-only shapes\\n\\n';
    
    return promptText;
  }
  
  getStatistics() {
    const stats = {
      totalCategories: this.shapeExamples.size,
      totalExamples: 0,
      categoryBreakdown: {}
    };
    
    for (const [category, examples] of this.shapeExamples) {
      stats.categoryBreakdown[category] = examples.length;
      stats.totalExamples += examples.length;
    }
    
    return stats;
  }
}