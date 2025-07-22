const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const { analyzeAndEnhancePrompt } = require('./src/promptAnalyzer');
const { generateShapeWithGemini } = require('./src/geminiClient');
const { processShapeResponse } = require('./src/shapeRenderer');
const { VisualFeedbackAnalyzer } = require('./src/visualFeedbackAnalyzer');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize feedback analyzer
const feedbackAnalyzer = new VisualFeedbackAnalyzer();

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' })); // Increased limit for image data
app.use(express.static('public'));

// Rate limiting
const rateLimit = require('express-rate-limit');
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api', limiter);

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Main shape generation endpoint with feedback support
app.post('/api/generate-shape', async (req, res) => {
  try {
    const { prompt, iteration = 1, feedback = null } = req.body;
    
    if (!prompt || prompt.trim().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Prompt is required'
      });
    }

    // Step 1: Analyze and enhance the prompt
    console.log(`Processing prompt (iteration ${iteration}):`, prompt);
    let enhancedPrompt = await analyzeAndEnhancePrompt(prompt);
    
    // If we have feedback from a previous iteration, incorporate it
    if (feedback && iteration > 1) {
      console.log('Incorporating feedback from previous iteration');
      enhancedPrompt = feedbackAnalyzer.generateImprovementPrompt(prompt, feedback, '');
    }
    
    // Step 2: Generate shape with Gemini
    console.log('Generating shape with Gemini...');
    const geminiResponse = await generateShapeWithGemini(enhancedPrompt);
    
    // Step 3: Process the response
    console.log('Processing shape response...');
    const processedShape = processShapeResponse(geminiResponse);
    
    // Step 4: Send response
    res.json({
      success: true,
      ...processedShape,
      enhancedPrompt,
      originalPrompt: prompt,
      iteration
    });
    
  } catch (error) {
    console.error('Error generating shape:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to generate shape'
    });
  }
});

// Shape analysis endpoint
app.post('/api/analyze-shape', async (req, res) => {
  try {
    const { imageData, metadata } = req.body;
    
    if (!imageData) {
      return res.status(400).json({
        success: false,
        error: 'Image data is required for analysis'
      });
    }
    
    console.log('Analyzing shape for PowerPoint suitability...');
    const analysis = await feedbackAnalyzer.analyzeShapeForPowerPoint(imageData, metadata);
    
    console.log(`Analysis complete. Score: ${analysis.score}/100, Suitable: ${analysis.suitable}`);
    
    res.json({
      success: true,
      ...analysis
    });
    
  } catch (error) {
    console.error('Error analyzing shape:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to analyze shape',
      // Default to suitable if analysis fails
      suitable: true,
      score: 75,
      feedback: [],
      suggestions: []
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    geminiConfigured: !!process.env.GOOGLE_API_KEY,
    features: {
      shapeGeneration: true,
      feedbackAnalysis: true,
      iterativeImprovement: true,
      powerpointOptimization: true
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    error: 'Something went wrong!'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Shape Generator server running on http://localhost:${PORT}`);
  console.log('Features enabled:');
  console.log('  ✓ PowerPoint-optimized shape generation');
  console.log('  ✓ Visual feedback analysis');
  console.log('  ✓ Iterative improvement (up to 3 iterations)');
  console.log('  ✓ High-quality image export');
  
  if (!process.env.GOOGLE_API_KEY) {
    console.warn('⚠️  Warning: GOOGLE_API_KEY not set in environment variables');
    console.warn('    The system will use fallback shapes instead of Gemini AI');
  }
});