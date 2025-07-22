# 🚀 Quick Start Guide - Shape Generator with Feedback

This guide will help you get the PowerPoint-optimized shape generator running in 5 minutes.

## Prerequisites
- Node.js 16+ installed
- Google API key for Gemini

## Step 1: Install Dependencies
```bash
cd generate-#21
npm install
```

## Step 2: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:
```
GOOGLE_API_KEY=your_actual_api_key_here
```

## Step 3: Start the Server
```bash
npm start
```

You should see:
```
Shape Generator server running on http://localhost:3000
Features enabled:
  ✓ PowerPoint-optimized shape generation
  ✓ Visual feedback analysis
  ✓ Iterative improvement (up to 3 iterations)
  ✓ High-quality image export
```

## Step 4: Open the Web Interface
Open your browser and go to: http://localhost:3000

## Step 5: Try Your First Shape

1. In the chat panel, type: **"Create a pie chart with 4 segments"**
2. Press Enter or click Send
3. Watch as the system:
   - Generates the initial shape
   - Analyzes it for PowerPoint suitability
   - Automatically improves it if needed
   - Shows the final result with a quality score

## Understanding the Feedback Loop

When you generate a shape, you'll see messages like:
- `Iteration 1: Initial generation...`
- `Analysis: Score 65/100. Issues found: Text too small, Low contrast`
- `Iteration 2: Regenerating based on feedback...`
- `Shape generated successfully! PowerPoint suitability: 92/100`

## Example Prompts to Test Feedback

### Prompts that trigger improvement:
- "Create a flowchart with very thin lines" 
- "Make a pie chart with tiny text"
- "Draw a complex mind map with 20 nodes"

### Prompts that usually pass first time:
- "Create a professional bar chart"
- "Make a simple organizational chart"
- "Design a clean Venn diagram"

## Export Your Shapes

Click the 💾 button to export any shape as a high-quality PNG image ready for PowerPoint.

## Troubleshooting

### No API Key
If you see fallback shapes, check your `.env` file has the correct API key.

### Analysis Not Working
The system will still generate shapes even if analysis fails. Check the console for errors.

### Server Won't Start
Make sure port 3000 is free or change it in `.env`:
```
PORT=3001
```

## Next Steps

- Read the full README.md for detailed documentation
- Run `npm run test:feedback` to see automated testing
- Customize the system prompt in `systemPrompts/shapeGeneration.txt`
- Adjust feedback thresholds in `src/visualFeedbackAnalyzer.js`

Happy shape generating! 🎨