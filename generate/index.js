import { AIShapeGenerator } from './ai-generator.js';
import { PptxUtils } from './utils.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class PowerPointAIGenerator {
  constructor() {
    this.aiGenerator = new AIShapeGenerator();
    this.tempDir = path.join(__dirname, 'temp');
    this.outputDir = path.join(__dirname, 'output');
    
    // Log shape examples statistics
    this.aiGenerator.logShapeExamplesInfo();
  }
  
  async generatePresentation(userPrompt, outputFileName = 'generated.pptx') {
    try {
      console.log('🚀 Starting PowerPoint AI Generation...');
      console.log(`📝 User prompt: "${userPrompt}"`);
      
      // Step 1: Clean up temp directory and create fresh one
      if (fs.existsSync(this.tempDir)) {
        fs.rmSync(this.tempDir, { recursive: true });
      }
      fs.mkdirSync(this.tempDir, { recursive: true });
      
      // Create output directory if it doesn't exist
      if (!fs.existsSync(this.outputDir)) {
        fs.mkdirSync(this.outputDir, { recursive: true });
      }
      
      // Step 2: Unzip blank.pptx to temp directory
      console.log('📦 Extracting blank.pptx...');
      const blankPptxPath = path.join(__dirname, 'blank.pptx');
      const extractedFiles = await PptxUtils.unzipPptx(blankPptxPath, this.tempDir);
      
      // Step 3: Find slide1.xml
      console.log('🔍 Finding slide1.xml...');
      const slide1Path = path.join(this.tempDir, 'ppt', 'slides', 'slide1.xml');
      if (!fs.existsSync(slide1Path)) {
        throw new Error('slide1.xml not found in blank.pptx');
      }
      
      // Step 4: Generate shape XML using AI
      console.log('🤖 Generating shapes with AI...');
      const shapeXml = await this.aiGenerator.generateShapeXmlFromPrompt(userPrompt);
      
      // Step 5: Inject shape into slide1.xml
      console.log('💉 Injecting shapes into slide...');
      const originalSlideXml = fs.readFileSync(slide1Path, 'utf8');
      const modifiedSlideXml = PptxUtils.injectShapeIntoSlide(originalSlideXml, shapeXml);
      
      // Write the modified slide back
      fs.writeFileSync(slide1Path, modifiedSlideXml);
      
      // Step 6: Zip back to PowerPoint file
      console.log('📦 Creating output PowerPoint file...');
      const outputPath = path.join(this.outputDir, outputFileName);
      await PptxUtils.zipToPptx(this.tempDir, outputPath);
      
      // Step 7: Clean up temp directory
      if (fs.existsSync(this.tempDir)) {
        fs.rmSync(this.tempDir, { recursive: true });
      }
      
      console.log(`✅ Successfully generated: ${outputPath}`);
      return outputPath;
      
    } catch (error) {
      console.error('❌ Error generating presentation:', error);
      
      // Clean up temp directory on error
      if (fs.existsSync(this.tempDir)) {
        fs.rmSync(this.tempDir, { recursive: true });
      }
      
      throw error;
    }
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node index.js "Your prompt here" [output-filename.pptx]');
    console.log('Example: node index.js "Create a title slide with Hello World" hello-world.pptx');
    process.exit(1);
  }
  
  const userPrompt = args[0];
  const outputFileName = args[1] || 'generated.pptx';
  
  try {
    const generator = new PowerPointAIGenerator();
    const outputPath = await generator.generatePresentation(userPrompt, outputFileName);
    
    console.log(`\n🎉 PowerPoint presentation generated successfully!`);
    console.log(`📄 Output file: ${outputPath}`);
    console.log(`\nYou can now open the file in PowerPoint to view the generated content.`);
    
  } catch (error) {
    console.error('\n❌ Failed to generate presentation:', error.message);
    process.exit(1);
  }
}

// Run the main function if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { PowerPointAIGenerator };