const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const { analyzeAndEnhancePrompt } = require('./src/promptAnalyzer');
const { generateShapeWithGemini } = require('./src/geminiClient');
const { processShapeResponse } = require('./src/shapeRenderer');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
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

// Main shape generation endpoint
app.post('/api/generate-shape', async (req, res) => {
  try {
    const { prompt } = req.body;
    
    if (!prompt || prompt.trim().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Prompt is required'
      });
    }

    // Step 1: Analyze and enhance the prompt
    console.log('Analyzing prompt:', prompt);
    const enhancedPrompt = await analyzeAndEnhancePrompt(prompt);
    
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
      originalPrompt: prompt
    });
    
  } catch (error) {
    console.error('Error generating shape:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Failed to generate shape'
    });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    geminiConfigured: !!process.env.GOOGLE_API_KEY
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
  if (!process.env.GOOGLE_API_KEY) {
    console.warn('⚠️  Warning: GOOGLE_API_KEY not set in environment variables');
  }
});