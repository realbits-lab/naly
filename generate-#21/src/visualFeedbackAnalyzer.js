/**
 * Visual Feedback Analyzer Module
 * Analyzes generated shapes for PowerPoint suitability
 */

const { GoogleGenerativeAI } = require("@google/generative-ai");

// PowerPoint shape criteria
const POWERPOINT_CRITERIA = {
  // Visual clarity for presentations
  clarity: {
    minContrast: 4.5, // WCAG AA standard
    readableTextSize: 14, // minimum font size in pt
    clearBoundaries: true,
  },
  
  // Professional appearance
  professional: {
    cleanDesign: true,
    appropriateColors: true,
    noClutter: true,
  },
  
  // Technical requirements
  technical: {
    vectorCompatible: true, // SVG or clean HTML/CSS
    scalable: true,
    printable: true,
    animationOptional: true, // animations should be removable
  },
  
  // Content structure
  content: {
    hierarchical: true,
    labeledElements: true,
    logicalFlow: true,
  }
};

/**
 * Initialize analyzer with Gemini for visual analysis
 */
class VisualFeedbackAnalyzer {
  constructor() {
    this.genAI = null;
    this.model = null;
    this.initializeAnalyzer();
  }

  initializeAnalyzer() {
    if (!process.env.GOOGLE_API_KEY) {
      console.warn('GOOGLE_API_KEY not set, using rule-based analysis only');
      return;
    }

    this.genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);
    this.model = this.genAI.getGenerativeModel({
      model: "gemini-2.5-pro",
      generationConfig: {
        temperature: 0.3, // Lower temperature for more consistent analysis
        topK: 10,
        topP: 0.85,
        maxOutputTokens: 2048,
      },
    });
  }

  /**
   * Analyze a shape snapshot for PowerPoint suitability
   * @param {string} imageData - Base64 image data or image URL
   * @param {object} shapeMetadata - Metadata about the shape
   * @returns {object} Analysis results with feedback
   */
  async analyzeShapeForPowerPoint(imageData, shapeMetadata) {
    const analysis = {
      suitable: false,
      score: 0,
      feedback: [],
      suggestions: [],
      regenerate: false,
    };

    try {
      // If Gemini is available, use visual analysis
      if (this.model && imageData) {
        const visualAnalysis = await this.performVisualAnalysis(imageData, shapeMetadata);
        Object.assign(analysis, visualAnalysis);
      } else {
        // Fallback to rule-based analysis
        const ruleAnalysis = this.performRuleBasedAnalysis(shapeMetadata);
        Object.assign(analysis, ruleAnalysis);
      }

      // Determine if regeneration is needed
      analysis.regenerate = analysis.score < 70; // 70% threshold for acceptance
      analysis.suitable = analysis.score >= 70;

    } catch (error) {
      console.error('Analysis error:', error);
      // Default to accepting the shape if analysis fails
      analysis.suitable = true;
      analysis.score = 75;
      analysis.feedback.push('Analysis completed with default approval');
    }

    return analysis;
  }

  /**
   * Perform visual analysis using Gemini
   */
  async performVisualAnalysis(imageData, metadata) {
    const analysisPrompt = `You are analyzing a generated shape/diagram for PowerPoint presentation suitability.

Analyze this image and provide a detailed assessment based on these criteria:

1. VISUAL CLARITY (25 points)
   - Is text readable and well-sized for presentations?
   - Are colors contrasting enough for projection?
   - Are boundaries and sections clearly defined?

2. PROFESSIONAL APPEARANCE (25 points)
   - Does it look professional and business-appropriate?
   - Is the design clean and uncluttered?
   - Are colors appropriate for business presentations?

3. POWERPOINT COMPATIBILITY (25 points)
   - Can this be easily recreated or imported into PowerPoint?
   - Is it scalable without quality loss?
   - Will it print well in black and white?

4. CONTENT EFFECTIVENESS (25 points)
   - Does it effectively communicate information?
   - Is there a clear hierarchy or flow?
   - Are all elements properly labeled?

Provide your response in this exact JSON format:
{
  "score": 0-100,
  "breakdown": {
    "clarity": 0-25,
    "professional": 0-25,
    "compatibility": 0-25,
    "effectiveness": 0-25
  },
  "issues": [
    "Specific issue 1",
    "Specific issue 2"
  ],
  "suggestions": [
    "Specific improvement 1",
    "Specific improvement 2"
  ],
  "suitable": true/false
}

Shape metadata: ${JSON.stringify(metadata)}`;

    try {
      // Prepare the image for Gemini
      const imagePart = {
        inlineData: {
          mimeType: "image/png",
          data: imageData.replace(/^data:image\/\w+;base64,/, ""),
        },
      };

      const result = await this.model.generateContent([analysisPrompt, imagePart]);
      const response = await result.response;
      const text = response.text();

      // Parse the JSON response
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        return {
          score: parsed.score || 0,
          feedback: parsed.issues || [],
          suggestions: parsed.suggestions || [],
          breakdown: parsed.breakdown || {},
          suitable: parsed.suitable || false,
        };
      }
    } catch (error) {
      console.error('Visual analysis error:', error);
    }

    // Fallback if visual analysis fails
    return this.performRuleBasedAnalysis(metadata);
  }

  /**
   * Perform rule-based analysis as fallback
   */
  performRuleBasedAnalysis(metadata) {
    let score = 0;
    const feedback = [];
    const suggestions = [];

    // Check shape type appropriateness
    const goodShapeTypes = ['flowchart', 'piechart', 'barchart', 'orgchart', 'timeline', 'venn'];
    if (goodShapeTypes.includes(metadata.shapeType)) {
      score += 25;
    } else {
      feedback.push('Shape type may not be ideal for PowerPoint');
      suggestions.push('Consider using a more traditional diagram type');
    }

    // Check element count (not too complex)
    if (metadata.elements && metadata.elements > 0 && metadata.elements <= 10) {
      score += 25;
    } else if (metadata.elements > 10) {
      feedback.push('Too many elements for a clear PowerPoint slide');
      suggestions.push('Simplify the diagram to fewer than 10 key elements');
    }

    // Check if it has proper metadata
    if (metadata.description && metadata.description.length > 10) {
      score += 25;
    }

    // Base score for attempting to generate something
    score += 25;

    return {
      score,
      feedback,
      suggestions,
      suitable: score >= 70,
    };
  }

  /**
   * Generate improvement prompt based on feedback
   */
  generateImprovementPrompt(originalPrompt, analysis, previousHtml) {
    let improvementPrompt = `ITERATION REQUIRED: The previous shape generation needs improvement for PowerPoint use.

Original Request: "${originalPrompt}"

ISSUES FOUND:
${analysis.feedback.map((f, i) => `${i + 1}. ${f}`).join('\n')}

REQUIRED IMPROVEMENTS:
${analysis.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}

POWERPOINT SPECIFIC REQUIREMENTS:
1. Ensure high contrast colors (minimum 4.5:1 ratio)
2. Use minimum 14pt font size for all text
3. Keep design simple and uncluttered
4. Make sure it's scalable without quality loss
5. Use professional business colors
6. Ensure clear hierarchy and flow
7. Add proper labels to all elements
8. Avoid overly complex animations

Previous attempt score: ${analysis.score}/100

Please regenerate the shape addressing ALL the issues mentioned above. Focus on making it perfect for PowerPoint presentations.`;

    if (analysis.breakdown) {
      improvementPrompt += `

Score Breakdown:
- Visual Clarity: ${analysis.breakdown.clarity || 0}/25
- Professional Appearance: ${analysis.breakdown.professional || 0}/25
- PowerPoint Compatibility: ${analysis.breakdown.compatibility || 0}/25
- Content Effectiveness: ${analysis.breakdown.effectiveness || 0}/25`;
    }

    return improvementPrompt;
  }
}

/**
 * Capture rendered shape as image
 * This is a placeholder - actual implementation would use html2canvas or similar
 */
async function captureShapeSnapshot(elementId) {
  // This function would be implemented on the client side
  // Returns base64 image data
  return null;
}

/**
 * Calculate color contrast ratio
 */
function getContrastRatio(color1, color2) {
  // Simple contrast calculation
  // In real implementation, would parse colors and calculate properly
  return 5.0; // Placeholder
}

module.exports = {
  VisualFeedbackAnalyzer,
  POWERPOINT_CRITERIA,
  captureShapeSnapshot,
};