/**
 * Shape Renderer Module
 * Processes and validates shape responses from Gemini
 */

/**
 * Process the shape response from Gemini
 * @param {object} geminiResponse - Raw response from Gemini
 * @returns {object} Processed shape data ready for rendering
 */
function processShapeResponse(geminiResponse) {
    // Validate response structure
    if (!geminiResponse || typeof geminiResponse !== 'object') {
        throw new Error('Invalid response format from AI');
    }
    
    // Extract and sanitize HTML
    const html = sanitizeHTML(geminiResponse.html || '');
    
    // Extract and validate CSS
    const css = validateCSS(geminiResponse.css || '');
    
    // Extract and validate JavaScript
    const js = validateJavaScript(geminiResponse.js || '');
    
    // Process metadata
    const metadata = processMetadata(geminiResponse.metadata || {});
    
    return {
        html,
        css,
        js,
        metadata,
        timestamp: new Date().toISOString()
    };
}

/**
 * Sanitize HTML to prevent XSS attacks
 * @param {string} html - Raw HTML string
 * @returns {string} Sanitized HTML
 */
function sanitizeHTML(html) {
    // Remove script tags
    html = html.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
    
    // Remove event handlers
    html = html.replace(/\son\w+\s*=\s*["'][^"']*["']/gi, '');
    
    // Remove javascript: URLs
    html = html.replace(/javascript:/gi, '');
    
    // Ensure all tags are properly closed
    html = ensureClosedTags(html);
    
    return html.trim();
}

/**
 * Validate and clean CSS
 * @param {string} css - Raw CSS string
 * @returns {string} Validated CSS
 */
function validateCSS(css) {
    // Remove any @import statements (security)
    css = css.replace(/@import\s+[^;]+;/gi, '');
    
    // Remove javascript in CSS
    css = css.replace(/javascript:/gi, '');
    
    // Ensure CSS is scoped to shape elements
    css = scopeCSS(css);
    
    return css.trim();
}

/**
 * Validate JavaScript code
 * @param {string} js - Raw JavaScript string
 * @returns {string} Validated JavaScript
 */
function validateJavaScript(js) {
    if (!js) return '';
    
    // Basic validation - remove dangerous patterns
    const dangerousPatterns = [
        /eval\s*\(/gi,
        /new\s+Function\s*\(/gi,
        /document\.write/gi,
        /window\.location/gi,
        /document\.cookie/gi,
        /localStorage/gi,
        /sessionStorage/gi,
        /fetch\s*\(/gi,
        /XMLHttpRequest/gi
    ];
    
    let validatedJS = js;
    dangerousPatterns.forEach(pattern => {
        validatedJS = validatedJS.replace(pattern, '/* blocked */');
    });
    
    // Wrap in IIFE to prevent global scope pollution
    validatedJS = `(function() {
    try {
        ${validatedJS}
    } catch (error) {
        console.error('Shape JavaScript error:', error);
    }
})();`;
    
    return validatedJS;
}

/**
 * Process and validate metadata
 * @param {object} metadata - Raw metadata object
 * @returns {object} Processed metadata
 */
function processMetadata(metadata) {
    const defaultMetadata = {
        shapeType: 'unknown',
        elements: 0,
        description: 'Generated shape',
        complexity: 'medium'
    };
    
    return {
        ...defaultMetadata,
        ...metadata,
        // Ensure safe values
        shapeType: String(metadata.shapeType || 'unknown').toLowerCase(),
        elements: parseInt(metadata.elements) || 0,
        description: String(metadata.description || '').substring(0, 200)
    };
}

/**
 * Ensure all HTML tags are properly closed
 * @param {string} html - HTML string
 * @returns {string} HTML with closed tags
 */
function ensureClosedTags(html) {
    // Simple tag closing for common self-closing tags
    const selfClosingTags = ['img', 'br', 'hr', 'input', 'meta', 'link'];
    
    selfClosingTags.forEach(tag => {
        const regex = new RegExp(`<${tag}([^>]*)(?<!/)>`, 'gi');
        html = html.replace(regex, `<${tag}$1 />`);
    });
    
    return html;
}

/**
 * Scope CSS to prevent style conflicts
 * @param {string} css - CSS string
 * @returns {string} Scoped CSS
 */
function scopeCSS(css) {
    // Add .shape-container prefix to all selectors if not already present
    const lines = css.split('\n');
    const scopedLines = [];
    let inRule = false;
    
    lines.forEach(line => {
        const trimmed = line.trim();
        
        // Skip empty lines and comments
        if (!trimmed || trimmed.startsWith('/*')) {
            scopedLines.push(line);
            return;
        }
        
        // Check if this is a selector line
        if (trimmed.includes('{')) {
            inRule = true;
            // Only add scope if not already scoped
            if (!trimmed.includes('.shape-container') && !trimmed.includes('.shape-')) {
                const selector = trimmed.substring(0, trimmed.indexOf('{'));
                const scopedSelector = selector.split(',').map(s => {
                    s = s.trim();
                    // Don't scope keyframes or media queries
                    if (s.startsWith('@')) return s;
                    return `.shape-container ${s}`;
                }).join(', ');
                scopedLines.push(`${scopedSelector} {`);
            } else {
                scopedLines.push(line);
            }
        } else if (trimmed === '}') {
            inRule = false;
            scopedLines.push(line);
        } else {
            scopedLines.push(line);
        }
    });
    
    return scopedLines.join('\n');
}

/**
 * Generate error shape for display
 * @param {string} errorMessage - Error message to display
 * @returns {object} Error shape data
 */
function generateErrorShape(errorMessage) {
    return {
        html: `
<div class="shape-error-container">
    <div class="shape-error-icon">⚠️</div>
    <h3>Shape Generation Error</h3>
    <p>${escapeHtml(errorMessage)}</p>
    <p class="shape-error-hint">Please try again with a different prompt.</p>
</div>`,
        css: `
.shape-error-container {
    text-align: center;
    padding: 2rem;
    background: #fee;
    border: 2px dashed #f44336;
    border-radius: 8px;
    max-width: 400px;
    margin: 0 auto;
}

.shape-error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.shape-error-container h3 {
    color: #d32f2f;
    margin-bottom: 0.5rem;
}

.shape-error-container p {
    color: #666;
    margin: 0.5rem 0;
}

.shape-error-hint {
    font-size: 0.9rem;
    font-style: italic;
}`,
        js: '',
        metadata: {
            shapeType: 'error',
            elements: 0,
            description: 'Error shape display'
        }
    };
}

/**
 * Escape HTML for safe display
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Optimize shape for performance
 * @param {object} shapeData - Shape data to optimize
 * @returns {object} Optimized shape data
 */
function optimizeShape(shapeData) {
    // Minify CSS
    if (shapeData.css) {
        shapeData.css = shapeData.css
            .replace(/\s+/g, ' ')
            .replace(/\s*{\s*/g, '{')
            .replace(/\s*}\s*/g, '}')
            .replace(/\s*:\s*/g, ':')
            .replace(/\s*;\s*/g, ';')
            .trim();
    }
    
    // Add performance hints
    shapeData.performanceHints = {
        renderTime: Date.now(),
        cssRules: (shapeData.css.match(/{/g) || []).length,
        domElements: (shapeData.html.match(/<[^/][^>]*>/g) || []).length
    };
    
    return shapeData;
}

// Export functions
module.exports = {
    processShapeResponse,
    generateErrorShape,
    optimizeShape
};