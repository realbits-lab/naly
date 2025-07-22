/**
 * Test script for the feedback-based shape generation system
 * This demonstrates the iterative improvement process
 */

const fetch = require('node-fetch');
const fs = require('fs').promises;
const path = require('path');

// Configuration
const BASE_URL = 'http://localhost:3000';
const TEST_PROMPTS = [
  "Create a simple pie chart with 4 segments showing quarterly sales",
  "Draw a flowchart for user login process with error handling",
  "Make an organizational chart for a small company with 10 employees",
  "Design a Venn diagram comparing JavaScript, Python, and Java"
];

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m',
  red: '\x1b[31m'
};

// Test the shape generation with feedback
async function testShapeGeneration(prompt) {
  console.log(`\n${colors.bright}${colors.blue}Testing: "${prompt}"${colors.reset}`);
  console.log('='.repeat(50));
  
  try {
    // Initial generation
    console.log(`${colors.yellow}Iteration 1: Initial generation...${colors.reset}`);
    const response = await fetch(`${BASE_URL}/api/generate-shape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        prompt,
        iteration: 1
      })
    });
    
    const data = await response.json();
    
    if (!data.success) {
      throw new Error(data.error || 'Generation failed');
    }
    
    console.log(`${colors.green}✓ Shape generated successfully${colors.reset}`);
    console.log(`  Shape type: ${data.metadata.shapeType}`);
    console.log(`  Elements: ${data.metadata.elements}`);
    
    // Simulate visual analysis (in real usage, this would capture the rendered shape)
    const mockImageData = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==';
    
    console.log(`\n${colors.yellow}Analyzing shape for PowerPoint suitability...${colors.reset}`);
    const analysisResponse = await fetch(`${BASE_URL}/api/analyze-shape`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        imageData: mockImageData,
        metadata: data.metadata
      })
    });
    
    const analysis = await analysisResponse.json();
    
    console.log(`${colors.blue}Analysis Results:${colors.reset}`);
    console.log(`  Score: ${analysis.score}/100`);
    console.log(`  Suitable: ${analysis.suitable ? 'Yes' : 'No'}`);
    
    if (analysis.feedback && analysis.feedback.length > 0) {
      console.log(`  Issues: ${analysis.feedback.join(', ')}`);
    }
    
    if (analysis.suggestions && analysis.suggestions.length > 0) {
      console.log(`  Suggestions: ${analysis.suggestions.join(', ')}`);
    }
    
    // If not suitable, iterate
    if (!analysis.suitable && analysis.regenerate) {
      console.log(`\n${colors.yellow}Iteration 2: Regenerating based on feedback...${colors.reset}`);
      
      const improvedResponse = await fetch(`${BASE_URL}/api/generate-shape`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          iteration: 2,
          feedback: analysis
        })
      });
      
      const improvedData = await improvedResponse.json();
      
      if (improvedData.success) {
        console.log(`${colors.green}✓ Improved shape generated${colors.reset}`);
        
        // Re-analyze
        const finalAnalysisResponse = await fetch(`${BASE_URL}/api/analyze-shape`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            imageData: mockImageData,
            metadata: improvedData.metadata
          })
        });
        
        const finalAnalysis = await finalAnalysisResponse.json();
        console.log(`  Final Score: ${finalAnalysis.score}/100`);
        console.log(`  Final Suitability: ${finalAnalysis.suitable ? 'Yes' : 'No'}`);
      }
    }
    
    console.log(`\n${colors.green}Test completed successfully!${colors.reset}`);
    
  } catch (error) {
    console.error(`${colors.red}Test failed: ${error.message}${colors.reset}`);
  }
}

// Test the health endpoint
async function testHealthEndpoint() {
  console.log(`\n${colors.bright}${colors.blue}Testing Health Endpoint${colors.reset}`);
  console.log('='.repeat(50));
  
  try {
    const response = await fetch(`${BASE_URL}/api/health`);
    const data = await response.json();
    
    console.log(`Status: ${data.status}`);
    console.log(`Gemini Configured: ${data.geminiConfigured ? 'Yes' : 'No'}`);
    console.log('Features:');
    Object.entries(data.features).forEach(([feature, enabled]) => {
      console.log(`  ${enabled ? '✓' : '✗'} ${feature}`);
    });
    
  } catch (error) {
    console.error(`${colors.red}Health check failed: ${error.message}${colors.reset}`);
  }
}

// Main test runner
async function runTests() {
  console.log(`${colors.bright}Shape Generator Feedback System Test${colors.reset}`);
  console.log('Starting tests...\n');
  
  // Test health endpoint first
  await testHealthEndpoint();
  
  // Test each prompt
  for (const prompt of TEST_PROMPTS) {
    await testShapeGeneration(prompt);
    // Small delay between tests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log(`\n${colors.bright}${colors.green}All tests completed!${colors.reset}`);
}

// Check if server is running
async function checkServer() {
  try {
    const response = await fetch(`${BASE_URL}/api/health`);
    return response.ok;
  } catch (error) {
    return false;
  }
}

// Entry point
async function main() {
  console.log('Checking if server is running...');
  
  const serverRunning = await checkServer();
  if (!serverRunning) {
    console.error(`${colors.red}Error: Server is not running at ${BASE_URL}${colors.reset}`);
    console.log('Please start the server with: npm start');
    process.exit(1);
  }
  
  console.log(`${colors.green}Server is running!${colors.reset}`);
  await runTests();
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = { testShapeGeneration, testHealthEndpoint };