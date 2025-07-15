import { AIShapeGenerator } from './ai-generator.js';

async function demonstrateShapes() {
  console.log('🎨 PowerPoint AI Shape Generator Demo');
  console.log('====================================');
  
  const generator = new AIShapeGenerator();
  
  console.log(`📊 Available shape types: ${generator.availableShapeTypes.length}`);
  console.log('\n🔸 Shape Categories:');
  console.log(generator.shapeExamples);
  
  console.log('\n🧪 Testing various shape prompts:');
  
  const testPrompts = [
    "Create a star shape with Welcome",
    "Create a diamond shape",
    "Create a flowchart with start, process, and decision shapes", 
    "Create arrow pointing down",
    "Create a 3D cube shape",
    "Create a callout bubble saying Hello",
    "Create an ellipse with text",
    "Create a hexagon shape"
  ];
  
  for (const prompt of testPrompts) {
    console.log(`\n💭 Testing: "${prompt}"`);
    try {
      const result = await generator.generateShapeFromPrompt(prompt);
      console.log(`✅ Generated ${result.shapes.length} shape(s):`);
      result.shapes.forEach(shape => {
        console.log(`   - ${shape.name} (type: ${shape.type})`);
      });
    } catch (error) {
      console.log(`❌ Error: ${error.message}`);
    }
  }
  
  console.log('\n🎯 Most common shape types in preset definitions:');
  const commonShapes = generator.availableShapeTypes.filter(type => 
    ['ellipse', 'diamond', 'star5', 'star6', 'star8', 'downArrow', 'upArrow', 
     'leftArrow', 'rightArrow', 'flowChartProcess', 'flowChartDecision', 
     'callout1', 'cube', 'can', 'bevel'].includes(type)
  );
  
  commonShapes.forEach(shape => {
    console.log(`   - ${shape}`);
  });
  
  console.log('\n🚀 Ready to generate PowerPoint presentations with AI-powered shapes!');
}

demonstrateShapes().catch(console.error);