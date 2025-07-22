# Shape Generator with Gemini AI

A web-based shape generator that creates diagram shapes based on user prompts using Google's Gemini AI model.

## 🎯 Overview

This system implements GitHub issue #21: Build a shape generator that:
1. Takes user prompts via a chat interface
2. Analyzes and enhances prompts for better AI understanding
3. Generates diagram shapes using Gemini AI
4. Displays results on an interactive canvas

## 🏗️ Architecture

```
User Input → Prompt Analysis → Gemini AI → HTML/CSS/JS → Canvas Display
     ↓              ↓               ↓              ↓              ↓
Chat Panel    Enhancement     Shape Gen    Rendering      Canvas Panel
```

## 📁 Project Structure

```
generate-#21/
├── README.md              # This file
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies (if needed)
├── server.js             # Express server for API handling
├── public/               # Static web files
│   ├── index.html        # Main web interface
│   ├── style.css         # UI styling
│   └── script.js         # Client-side logic
├── src/
│   ├── promptAnalyzer.js  # Prompt enhancement logic
│   ├── geminiClient.js    # Gemini API integration
│   └── shapeRenderer.js   # Shape rendering utilities
└── systemPrompts/
    └── shapeGeneration.txt # System prompt for Gemini
```

## 🚀 Features

- **Interactive Chat Panel**: User-friendly interface for entering shape prompts
- **Smart Prompt Analysis**: Enhances user prompts for better AI comprehension
- **Gemini AI Integration**: Leverages Google's Gemini 2.5 Pro model for shape generation
- **Real-time Canvas Rendering**: Instant visualization of generated shapes
- **Infographic Style**: Shapes are generated to be visually appealing and informative
- **Responsive Design**: Works on desktop and mobile devices
- **🔄 Iterative Feedback Loop**: Automatically analyzes and improves shapes for PowerPoint
- **📊 PowerPoint Optimization**: Ensures all shapes meet presentation standards
- **🎯 Visual Quality Analysis**: AI-powered assessment of shape suitability
- **📸 High-Quality Export**: Export shapes as PNG images for presentations

## 💻 Installation

1. **Clone and navigate to directory**:
   ```bash
   cd generate-#21
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

4. **Run the server**:
   ```bash
   npm start
   ```

5. **Open in browser**:
   ```
   http://localhost:3000
   ```

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Your Google API key for Gemini
- `PORT`: Server port (default: 3000)

### System Prompt
The system prompt in `systemPrompts/shapeGeneration.txt` guides Gemini to:
- Generate HTML/CSS/JS code for shapes
- Create visually comfortable and easy-to-understand diagrams
- Summarize user prompts infographically
- Ensure responsive and accessible designs

## 📝 Usage

1. **Enter a prompt** in the chat panel (e.g., "Create a flowchart showing user registration process")
2. **Click Send** to process your request
3. **View the generated shape** on the canvas panel
4. **Interact** with the shape (zoom, pan, etc.)
5. **Save or export** your diagram

## 🎨 Example Prompts

- "Create a pie chart showing market share distribution"
- "Draw a flowchart for a login system"
- "Generate an organizational chart for a small company"
- "Make a mind map about climate change"
- "Design a Venn diagram comparing programming languages"

## 🔄 Iterative Feedback System

The shape generator includes an intelligent feedback loop that ensures all generated shapes are optimized for PowerPoint presentations:

### How It Works

1. **Initial Generation**: Creates a shape based on your prompt
2. **Visual Analysis**: Captures and analyzes the rendered shape
3. **PowerPoint Suitability Check**: Evaluates against these criteria:
   - Visual clarity (contrast, text size, boundaries)
   - Professional appearance (clean design, appropriate colors)
   - Technical compatibility (scalability, print-friendly)
   - Content effectiveness (hierarchy, labeling, flow)
4. **Automatic Improvement**: If score < 70/100, regenerates with specific feedback
5. **Final Optimization**: Ensures the shape meets all PowerPoint standards

### Scoring System

Each shape is scored out of 100 points:
- **25 points**: Visual Clarity
- **25 points**: Professional Appearance  
- **25 points**: PowerPoint Compatibility
- **25 points**: Content Effectiveness

Shapes scoring 70+ are considered suitable for presentations.

### Maximum Iterations

The system will iterate up to 3 times to achieve the best result. Each iteration incorporates feedback from the previous analysis to improve:
- Color contrast
- Text readability
- Layout simplicity
- Professional styling
- Element sizing
- Overall clarity

## 🔌 API Endpoints

### POST /api/generate-shape
Generate a shape from a user prompt with optional feedback iteration.

**Request**:
```json
{
  "prompt": "Create a flowchart for user authentication",
  "iteration": 1,
  "feedback": null
}
```

**Response**:
```json
{
  "success": true,
  "html": "<div class='ppt-shape'>...</div>",
  "css": ".ppt-shape { ... }",
  "js": "// Shape interaction code",
  "enhancedPrompt": "Generate a detailed flowchart...",
  "metadata": {
    "shapeType": "flowchart",
    "elements": 5,
    "powerpointReady": true
  },
  "iteration": 1
}
```

### POST /api/analyze-shape
Analyze a shape for PowerPoint suitability.

**Request**:
```json
{
  "imageData": "data:image/png;base64,...",
  "metadata": {
    "shapeType": "flowchart",
    "elements": 5
  }
}
```

**Response**:
```json
{
  "success": true,
  "suitable": true,
  "score": 85,
  "feedback": ["Text size could be larger"],
  "suggestions": ["Increase font size to 16pt"],
  "regenerate": false,
  "breakdown": {
    "clarity": 20,
    "professional": 23,
    "compatibility": 22,
    "effectiveness": 20
  }
}
```

## 🧩 Components

### Chat Panel
- Message history
- Input field with prompt suggestions
- Send button with loading states
- Error handling for failed requests

### Canvas Panel
- Zoomable and pannable canvas
- Shape rendering area
- Export options (PNG, SVG, PDF)
- Responsive sizing

### Prompt Analyzer
- Keyword extraction
- Context enhancement
- Shape type detection
- Clarity improvement

### Gemini Integration
- API client with retry logic
- Response parsing
- Error handling
- Rate limiting

## 🎯 System Prompt Strategy

The system prompt instructs Gemini to:
1. Analyze the user's intent
2. Generate semantic HTML structure
3. Apply modern CSS styling
4. Add interactive JavaScript when needed
5. Ensure accessibility standards
6. Optimize for visual clarity

## 🧪 Testing

### Unit Tests
Run unit tests:
```bash
npm test
```

### Feedback System Test
Test the iterative feedback loop:
```bash
# Start the server first
npm start

# In another terminal, run the feedback test
npm run test:feedback
```

This test will:
1. Generate shapes for various prompts
2. Analyze them for PowerPoint suitability
3. Demonstrate the iterative improvement process
4. Show scoring and feedback details

### Manual Testing
1. Start the server: `npm start`
2. Open browser: `http://localhost:3000`
3. Try prompts like:
   - "Create a pie chart with small text" (will trigger feedback)
   - "Draw a flowchart with thin lines" (will trigger feedback)
   - "Make a professional bar chart" (should pass first time)

Test coverage includes:
- Prompt analysis accuracy
- API integration
- Shape rendering
- UI responsiveness
- Error scenarios
- Feedback loop iterations
- PowerPoint optimization

## 🚧 Future Enhancements

- Shape editing capabilities
- Multiple shape layouts
- Collaboration features
- Shape templates library
- Export to PowerPoint
- Animation support
- Theme customization

## 🐛 Troubleshooting

### Common Issues

1. **Gemini API errors**: Check API key and quota
2. **Shapes not rendering**: Verify browser console for JS errors
3. **Slow generation**: Consider implementing caching
4. **Layout issues**: Check responsive CSS

### Debug Mode
Enable debug mode by adding `?debug=true` to the URL for verbose logging.

## 📚 Dependencies

### Frontend
- Modern vanilla JavaScript (ES6+)
- CSS3 with flexbox/grid
- HTML5 Canvas API (optional)

### Backend
- Express.js for server
- Google Generative AI SDK
- dotenv for configuration
- cors for cross-origin requests

## 🤝 Contributing

1. Follow the project's coding standards
2. Add tests for new features
3. Update documentation
4. Submit PR with clear description

## 📄 License

This module is part of the PowerPoint template generation framework and follows the main project's license.

---

**Implementation for GitHub Issue #21**: Build a shape generator with Gemini AI integration.