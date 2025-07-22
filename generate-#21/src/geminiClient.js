/**
 * Gemini API Client Module
 * Handles communication with Google's Gemini AI for shape generation
 */

const { GoogleGenerativeAI } = require('@google/generative-ai');
const fs = require('fs').promises;
const path = require('path');

// Initialize Gemini
let genAI;
let model;

// Initialize the Gemini client
function initializeGemini() {
    if (!process.env.GOOGLE_API_KEY) {
        throw new Error('GOOGLE_API_KEY environment variable is not set');
    }
    
    genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
    model = genAI.getGenerativeModel({ 
        model: 'gemini-1.5-flash',
        generationConfig: {
            temperature: 0.7,
            topK: 20,
            topP: 0.9,
            maxOutputTokens: 4096,
        }
    });
}

// Load system prompt
async function loadSystemPrompt() {
    try {
        const promptPath = path.join(__dirname, '..', 'systemPrompts', 'shapeGeneration.txt');
        return await fs.readFile(promptPath, 'utf-8');
    } catch (error) {
        console.warn('System prompt file not found, using default');
        return getDefaultSystemPrompt();
    }
}

// Default system prompt if file is not found
function getDefaultSystemPrompt() {
    return `You are an expert at creating beautiful, informative diagrams and shapes using HTML, CSS, and JavaScript.

Your task is to generate code that creates visually appealing shapes and diagrams based on user requests.

IMPORTANT INSTRUCTIONS:
1. Generate ONLY the HTML, CSS, and JavaScript code needed for the shape
2. Make the output visually comfortable and easy to understand
3. Summarize the user's prompt infographically
4. Use modern, clean design principles
5. Ensure the shape is responsive and works well at different sizes
6. Include smooth animations and transitions where appropriate
7. Use semantic HTML for accessibility

OUTPUT FORMAT:
You must return a JSON object with exactly these fields:
{
    "html": "<!-- Your HTML code here -->",
    "css": "/* Your CSS code here */",
    "js": "// Your JavaScript code here (optional)",
    "metadata": {
        "shapeType": "flowchart|piechart|barchart|etc",
        "elements": 5,
        "description": "Brief description of what was created"
    }
}

DESIGN GUIDELINES:
- Use a professional color palette
- Ensure sufficient contrast for readability
- Add subtle shadows and borders for depth
- Use consistent spacing and alignment
- Make interactive elements obvious (hover states, cursor changes)
- Optimize for both light and dark backgrounds

TECHNICAL REQUIREMENTS:
- Use CSS classes prefixed with 'shape-' to avoid conflicts
- Make shapes scalable using relative units (%, em, rem, vw, vh)
- Include CSS transitions for smooth interactions
- Use CSS Grid or Flexbox for layouts
- Add data attributes for dynamic updates if needed

Remember: The goal is to create shapes that effectively communicate information in a visually pleasing way.`;
}

/**
 * Generate a shape using Gemini AI
 * @param {string} enhancedPrompt - The enhanced prompt from the analyzer
 * @returns {object} Generated shape code and metadata
 */
async function generateShapeWithGemini(enhancedPrompt) {
    try {
        // Initialize if not already done
        if (!model) {
            initializeGemini();
        }
        
        // Load system prompt
        const systemPrompt = await loadSystemPrompt();
        
        // Combine system prompt with enhanced user prompt
        const fullPrompt = `${systemPrompt}

USER REQUEST:
${enhancedPrompt}

Generate the shape code now:`;
        
        // Generate content
        console.log('Calling Gemini API...');
        const result = await model.generateContent(fullPrompt);
        const response = await result.response;
        const text = response.text();
        
        // Parse the response
        const parsedResponse = parseGeminiResponse(text);
        
        return parsedResponse;
        
    } catch (error) {
        console.error('Gemini API Error:', error);
        
        // Fallback response for testing/demo
        if (error.message.includes('API_KEY')) {
            console.warn('Using fallback response due to missing API key');
            return getFallbackResponse(enhancedPrompt);
        }
        
        throw error;
    }
}

/**
 * Parse Gemini's response to extract code
 * @param {string} responseText - Raw response from Gemini
 * @returns {object} Parsed shape data
 */
function parseGeminiResponse(responseText) {
    try {
        // Try to parse as JSON first
        const jsonMatch = responseText.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const parsed = JSON.parse(jsonMatch[0]);
            return {
                html: parsed.html || '',
                css: parsed.css || '',
                js: parsed.js || '',
                metadata: parsed.metadata || {}
            };
        }
        
        // Fallback: Extract code blocks
        const htmlMatch = responseText.match(/```html\n([\s\S]*?)\n```/);
        const cssMatch = responseText.match(/```css\n([\s\S]*?)\n```/);
        const jsMatch = responseText.match(/```javascript\n([\s\S]*?)\n```/);
        
        return {
            html: htmlMatch ? htmlMatch[1] : '<div class="shape-error">Failed to parse HTML</div>',
            css: cssMatch ? cssMatch[1] : '.shape-error { color: red; }',
            js: jsMatch ? jsMatch[1] : '',
            metadata: {
                shapeType: 'unknown',
                parseMethod: 'fallback'
            }
        };
        
    } catch (error) {
        console.error('Error parsing Gemini response:', error);
        throw new Error('Failed to parse AI response');
    }
}

/**
 * Get fallback response for demo/testing
 * @param {string} prompt - User prompt
 * @returns {object} Fallback shape data
 */
function getFallbackResponse(prompt) {
    const promptLower = prompt.toLowerCase();
    
    // Detect shape type from prompt
    if (promptLower.includes('pie')) {
        return getPieChartFallback();
    } else if (promptLower.includes('flow')) {
        return getFlowchartFallback();
    } else if (promptLower.includes('bar')) {
        return getBarChartFallback();
    } else {
        return getDefaultShapeFallback();
    }
}

// Fallback shapes
function getPieChartFallback() {
    return {
        html: `
<div class="shape-container">
    <div class="shape-pie-chart">
        <svg viewBox="0 0 200 200" class="pie-svg">
            <circle cx="100" cy="100" r="80" fill="#4CAF50" class="pie-segment" 
                    stroke="#fff" stroke-width="2" 
                    stroke-dasharray="125.6 377" 
                    transform="rotate(-90 100 100)"/>
            <circle cx="100" cy="100" r="80" fill="#2196F3" class="pie-segment" 
                    stroke="#fff" stroke-width="2" 
                    stroke-dasharray="94.2 377" stroke-dashoffset="-125.6"
                    transform="rotate(-90 100 100)"/>
            <circle cx="100" cy="100" r="80" fill="#FF9800" class="pie-segment" 
                    stroke="#fff" stroke-width="2" 
                    stroke-dasharray="94.2 377" stroke-dashoffset="-219.8"
                    transform="rotate(-90 100 100)"/>
            <circle cx="100" cy="100" r="80" fill="#F44336" class="pie-segment" 
                    stroke="#fff" stroke-width="2" 
                    stroke-dasharray="62.8 377" stroke-dashoffset="-314"
                    transform="rotate(-90 100 100)"/>
        </svg>
        <div class="pie-legend">
            <div class="legend-item"><span style="background: #4CAF50"></span> Category A (33%)</div>
            <div class="legend-item"><span style="background: #2196F3"></span> Category B (25%)</div>
            <div class="legend-item"><span style="background: #FF9800"></span> Category C (25%)</div>
            <div class="legend-item"><span style="background: #F44336"></span> Category D (17%)</div>
        </div>
    </div>
</div>`,
        css: `
.shape-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}

.shape-pie-chart {
    display: flex;
    gap: 2rem;
    align-items: center;
}

.pie-svg {
    width: 300px;
    height: 300px;
}

.pie-segment {
    transition: opacity 0.3s ease;
    cursor: pointer;
}

.pie-segment:hover {
    opacity: 0.8;
}

.pie-legend {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
}

.legend-item span {
    width: 20px;
    height: 20px;
    border-radius: 4px;
}`,
        js: `
// Add interactivity to pie segments
const segments = document.querySelectorAll('.pie-segment');
const legendItems = document.querySelectorAll('.legend-item');

segments.forEach((segment, index) => {
    segment.addEventListener('mouseenter', () => {
        legendItems[index].style.fontWeight = 'bold';
    });
    
    segment.addEventListener('mouseleave', () => {
        legendItems[index].style.fontWeight = 'normal';
    });
});`,
        metadata: {
            shapeType: 'piechart',
            elements: 4,
            description: 'Interactive pie chart with hover effects'
        }
    };
}

function getFlowchartFallback() {
    return {
        html: `
<div class="shape-container">
    <div class="shape-flowchart">
        <div class="flow-node flow-start">Start</div>
        <div class="flow-arrow">↓</div>
        <div class="flow-node flow-process">Process Input</div>
        <div class="flow-arrow">↓</div>
        <div class="flow-node flow-decision">Valid?</div>
        <div class="flow-branches">
            <div class="flow-branch">
                <div class="flow-arrow">← No</div>
                <div class="flow-node flow-process">Show Error</div>
            </div>
            <div class="flow-branch">
                <div class="flow-arrow">Yes →</div>
                <div class="flow-node flow-process">Continue</div>
            </div>
        </div>
        <div class="flow-arrow">↓</div>
        <div class="flow-node flow-end">End</div>
    </div>
</div>`,
        css: `
.shape-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}

.shape-flowchart {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.flow-node {
    padding: 1rem 2rem;
    border: 2px solid #333;
    background: white;
    font-weight: 500;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.flow-node:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.flow-start, .flow-end {
    border-radius: 50px;
    background: #4CAF50;
    color: white;
}

.flow-process {
    border-radius: 8px;
    background: #2196F3;
    color: white;
}

.flow-decision {
    transform: rotate(45deg);
    padding: 1.5rem;
    background: #FF9800;
    color: white;
}

.flow-decision::before {
    content: attr(data-text);
    display: block;
    transform: rotate(-45deg);
}

.flow-arrow {
    font-size: 1.5rem;
    color: #666;
}

.flow-branches {
    display: flex;
    gap: 4rem;
    align-items: center;
}

.flow-branch {
    display: flex;
    align-items: center;
    gap: 1rem;
}`,
        js: '',
        metadata: {
            shapeType: 'flowchart',
            elements: 6,
            description: 'Simple flowchart with decision branch'
        }
    };
}

function getBarChartFallback() {
    return {
        html: `
<div class="shape-container">
    <div class="shape-bar-chart">
        <div class="chart-title">Sample Data Visualization</div>
        <div class="chart-bars">
            <div class="bar-group">
                <div class="bar" style="height: 70%;">
                    <span class="bar-value">70</span>
                </div>
                <span class="bar-label">Q1</span>
            </div>
            <div class="bar-group">
                <div class="bar" style="height: 85%;">
                    <span class="bar-value">85</span>
                </div>
                <span class="bar-label">Q2</span>
            </div>
            <div class="bar-group">
                <div class="bar" style="height: 60%;">
                    <span class="bar-value">60</span>
                </div>
                <span class="bar-label">Q3</span>
            </div>
            <div class="bar-group">
                <div class="bar" style="height: 90%;">
                    <span class="bar-value">90</span>
                </div>
                <span class="bar-label">Q4</span>
            </div>
        </div>
    </div>
</div>`,
        css: `
.shape-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}

.shape-bar-chart {
    text-align: center;
}

.chart-title {
    font-size: 1.5rem;
    font-weight: bold;
    margin-bottom: 2rem;
    color: #333;
}

.chart-bars {
    display: flex;
    align-items: flex-end;
    gap: 2rem;
    height: 250px;
    padding: 0 1rem;
}

.bar-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
}

.bar {
    width: 60px;
    background: linear-gradient(to top, #2196F3, #64B5F6);
    border-radius: 4px 4px 0 0;
    position: relative;
    transition: all 0.3s ease;
    cursor: pointer;
}

.bar:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
}

.bar-value {
    position: absolute;
    top: -25px;
    left: 50%;
    transform: translateX(-50%);
    font-weight: bold;
    color: #333;
}

.bar-label {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}`,
        js: '',
        metadata: {
            shapeType: 'barchart',
            elements: 4,
            description: 'Animated bar chart with hover effects'
        }
    };
}

function getDefaultShapeFallback() {
    return {
        html: `
<div class="shape-container">
    <div class="shape-default">
        <h3>Shape Generator</h3>
        <p>Your custom shape will appear here based on your prompt.</p>
        <div class="shape-placeholder">
            <svg viewBox="0 0 200 200" class="placeholder-svg">
                <rect x="20" y="20" width="160" height="160" rx="10" 
                      fill="#e3f2fd" stroke="#2196F3" stroke-width="2"/>
                <circle cx="100" cy="100" r="40" fill="#2196F3" opacity="0.7"/>
                <path d="M 60 100 L 140 100 M 100 60 L 100 140" 
                      stroke="white" stroke-width="3" stroke-linecap="round"/>
            </svg>
        </div>
    </div>
</div>`,
        css: `
.shape-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 2rem;
}

.shape-default {
    text-align: center;
}

.shape-default h3 {
    color: #333;
    margin-bottom: 1rem;
}

.shape-default p {
    color: #666;
    margin-bottom: 2rem;
}

.shape-placeholder {
    display: inline-block;
}

.placeholder-svg {
    width: 200px;
    height: 200px;
    filter: drop-shadow(0 4px 6px rgba(0, 0, 0, 0.1));
}`,
        js: '',
        metadata: {
            shapeType: 'placeholder',
            elements: 1,
            description: 'Default placeholder shape'
        }
    };
}

// Export functions
module.exports = {
    generateShapeWithGemini,
    initializeGemini
};