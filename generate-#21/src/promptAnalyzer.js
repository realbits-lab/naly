/**
 * Prompt Analyzer Module
 * Analyzes and enhances user prompts for better Gemini understanding
 */

// Keywords that indicate different shape types
const SHAPE_KEYWORDS = {
    flowchart: ['flowchart', 'flow', 'process', 'workflow', 'steps', 'decision', 'procedure'],
    piechart: ['pie chart', 'pie', 'percentage', 'distribution', 'portion', 'share', 'breakdown'],
    barchart: ['bar chart', 'bar', 'comparison', 'bars', 'column chart', 'histogram'],
    orgchart: ['organizational', 'org chart', 'hierarchy', 'structure', 'team', 'organization'],
    mindmap: ['mind map', 'mindmap', 'brainstorm', 'ideas', 'concepts', 'branches'],
    venn: ['venn diagram', 'venn', 'overlap', 'intersection', 'sets', 'relationships'],
    timeline: ['timeline', 'chronological', 'events', 'history', 'schedule', 'roadmap'],
    diagram: ['diagram', 'visualization', 'chart', 'graph', 'illustration']
};

// Color keywords
const COLOR_KEYWORDS = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown', 'black', 'white', 'gray', 'colorful', 'vibrant', 'pastel', 'monochrome'];

// Style keywords
const STYLE_KEYWORDS = ['modern', 'minimal', 'simple', 'detailed', 'professional', 'casual', 'formal', 'creative', 'clean', 'elegant'];

/**
 * Analyze the user prompt and extract key information
 * @param {string} prompt - User's original prompt
 * @returns {object} Analysis results
 */
function analyzePrompt(prompt) {
    const lowerPrompt = prompt.toLowerCase();
    
    // Detect shape type
    let detectedShapeType = 'diagram'; // default
    let shapeConfidence = 0;
    
    for (const [shapeType, keywords] of Object.entries(SHAPE_KEYWORDS)) {
        const matches = keywords.filter(keyword => lowerPrompt.includes(keyword));
        if (matches.length > shapeConfidence) {
            detectedShapeType = shapeType;
            shapeConfidence = matches.length;
        }
    }
    
    // Detect colors mentioned
    const mentionedColors = COLOR_KEYWORDS.filter(color => lowerPrompt.includes(color));
    
    // Detect style preferences
    const mentionedStyles = STYLE_KEYWORDS.filter(style => lowerPrompt.includes(style));
    
    // Extract potential data points or elements
    const numbers = prompt.match(/\d+/g) || [];
    const quotedTexts = prompt.match(/"[^"]+"/g) || [];
    
    // Detect complexity hints
    const isComplex = lowerPrompt.includes('complex') || lowerPrompt.includes('detailed') || lowerPrompt.includes('comprehensive');
    const isSimple = lowerPrompt.includes('simple') || lowerPrompt.includes('basic') || lowerPrompt.includes('minimal');
    
    return {
        detectedShapeType,
        shapeConfidence,
        mentionedColors,
        mentionedStyles,
        numbers,
        quotedTexts,
        complexity: isComplex ? 'complex' : (isSimple ? 'simple' : 'moderate'),
        originalPrompt: prompt
    };
}

/**
 * Enhance the prompt with additional context and clarity
 * @param {string} prompt - User's original prompt
 * @returns {string} Enhanced prompt for Gemini
 */
async function analyzeAndEnhancePrompt(prompt) {
    const analysis = analyzePrompt(prompt);
    
    // Build enhanced prompt
    let enhancedPrompt = `Create a ${analysis.detectedShapeType} with the following specifications:\n\n`;
    
    // Add original request
    enhancedPrompt += `User Request: "${prompt}"\n\n`;
    
    // Add shape-specific instructions
    enhancedPrompt += getShapeSpecificInstructions(analysis.detectedShapeType);
    
    // Add color preferences
    if (analysis.mentionedColors.length > 0) {
        enhancedPrompt += `\nColor Scheme: Use ${analysis.mentionedColors.join(', ')} colors as the primary palette.\n`;
    } else {
        enhancedPrompt += `\nColor Scheme: Use a professional and visually appealing color palette.\n`;
    }
    
    // Add style preferences
    if (analysis.mentionedStyles.length > 0) {
        enhancedPrompt += `Style: Make it ${analysis.mentionedStyles.join(' and ')}.\n`;
    }
    
    // Add complexity guidance
    enhancedPrompt += `\nComplexity: Create a ${analysis.complexity} design that is easy to understand.\n`;
    
    // Add data points if numbers were mentioned
    if (analysis.numbers.length > 0) {
        enhancedPrompt += `\nData Points: Include ${analysis.numbers.join(', ')} as relevant values or segments.\n`;
    }
    
    // Add quoted texts as labels if present
    if (analysis.quotedTexts.length > 0) {
        enhancedPrompt += `\nLabels: Use these texts: ${analysis.quotedTexts.join(', ')}\n`;
    }
    
    // Add general instructions
    enhancedPrompt += `
\nGeneral Requirements:
- Make it visually appealing and professional
- Ensure text is readable and well-positioned
- Use appropriate spacing and alignment
- Make it responsive and scalable
- Include hover effects where appropriate
- Ensure accessibility with proper contrast ratios
`;
    
    return enhancedPrompt;
}

/**
 * Get shape-specific instructions based on detected type
 * @param {string} shapeType - Detected shape type
 * @returns {string} Shape-specific instructions
 */
function getShapeSpecificInstructions(shapeType) {
    const instructions = {
        flowchart: `Create a flowchart with:
- Clear start and end points
- Decision diamonds for conditional logic
- Process rectangles for actions
- Arrows showing flow direction
- Proper spacing between elements`,
        
        piechart: `Create a pie chart with:
- Clearly labeled segments
- Percentage values displayed
- A legend if needed
- Smooth animations on hover
- Total value in the center (optional)`,
        
        barchart: `Create a bar chart with:
- Labeled axes
- Clear value indicators
- Consistent bar spacing
- Grid lines for easy reading
- Hover tooltips with exact values`,
        
        orgchart: `Create an organizational chart with:
- Hierarchical structure
- Clear reporting lines
- Role/title labels
- Consistent box sizes
- Expandable/collapsible nodes if complex`,
        
        mindmap: `Create a mind map with:
- Central concept clearly highlighted
- Branching structure
- Color-coded categories
- Readable text at all levels
- Smooth curves for connections`,
        
        venn: `Create a Venn diagram with:
- Clear circle/set labels
- Intersection areas highlighted
- Proper overlap visualization
- Color coding for different sets
- Labels for intersection areas`,
        
        timeline: `Create a timeline with:
- Clear chronological order
- Event markers and labels
- Date/time indicators
- Visual flow from past to future
- Milestone highlights`,
        
        diagram: `Create a diagram with:
- Clear visual hierarchy
- Proper element relationships
- Consistent styling
- Informative labels
- Professional appearance`
    };
    
    return instructions[shapeType] || instructions.diagram;
}

// Export the enhancement function
module.exports = {
    analyzeAndEnhancePrompt,
    analyzePrompt
};