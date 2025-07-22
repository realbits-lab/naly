// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const promptInput = document.getElementById('promptInput');
const sendButton = document.getElementById('sendButton');
const canvasContent = document.getElementById('canvasContent');
const canvasContainer = document.getElementById('canvasContainer');
const errorModal = document.getElementById('errorModal');
const errorMessage = document.getElementById('errorMessage');
const closeModal = document.querySelector('.close');

// Zoom Controls
const zoomInBtn = document.getElementById('zoomIn');
const zoomOutBtn = document.getElementById('zoomOut');
const resetZoomBtn = document.getElementById('resetZoom');
const exportBtn = document.getElementById('exportShape');

// State
let currentZoom = 1;
let isGenerating = false;
let currentPrompt = '';
let iterationCount = 0;
const MAX_ITERATIONS = 3;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    promptInput.focus();
});

// Event Listeners
function setupEventListeners() {
    sendButton.addEventListener('click', handleSend);
    promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });
    
    // Zoom controls
    zoomInBtn.addEventListener('click', () => adjustZoom(0.25));
    zoomOutBtn.addEventListener('click', () => adjustZoom(-0.25));
    resetZoomBtn.addEventListener('click', resetZoom);
    exportBtn.addEventListener('click', exportShape);
    
    // Modal
    closeModal.addEventListener('click', closeErrorModal);
    window.addEventListener('click', (e) => {
        if (e.target === errorModal) {
            closeErrorModal();
        }
    });
}

// Send Message with Iterative Feedback
async function handleSend() {
    const prompt = promptInput.value.trim();
    if (!prompt || isGenerating) return;
    
    currentPrompt = prompt;
    iterationCount = 0;
    isGenerating = true;
    updateUI(true);
    
    // Add user message
    addMessage(prompt, 'user');
    
    // Clear input
    promptInput.value = '';
    
    // Start generation with feedback loop
    await generateWithFeedback(prompt);
    
    isGenerating = false;
    updateUI(false);
}

// Generate with Feedback Loop
async function generateWithFeedback(prompt, previousAnalysis = null) {
    try {
        iterationCount++;
        
        if (iterationCount > MAX_ITERATIONS) {
            addMessage(`Reached maximum iterations (${MAX_ITERATIONS}). Using best result.`, 'system');
            return;
        }
        
        // Show iteration status
        if (iterationCount > 1) {
            addMessage(`Iteration ${iterationCount}: Regenerating based on feedback...`, 'system');
        }
        
        // Prepare request data
        const requestData = {
            prompt,
            iteration: iterationCount,
            feedback: previousAnalysis
        };
        
        // Call API
        const response = await fetch('/api/generate-shape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Render shape
            renderShape(data);
            
            // Wait for rendering to complete
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Capture and analyze the shape
            const analysis = await captureAndAnalyzeShape(data.metadata);
            
            if (analysis && !analysis.suitable && analysis.regenerate && iterationCount < MAX_ITERATIONS) {
                // Show feedback
                addMessage(`Analysis: Score ${analysis.score}/100. Issues found: ${analysis.feedback.join(', ')}`, 'system');
                
                // Regenerate with feedback
                await generateWithFeedback(prompt, analysis);
            } else {
                // Success!
                const finalScore = analysis ? analysis.score : 100;
                addMessage(`Shape generated successfully! PowerPoint suitability: ${finalScore}/100`, 'assistant');
                
                if (analysis && analysis.suggestions.length > 0) {
                    addMessage(`Suggestions for manual improvement: ${analysis.suggestions.join('; ')}`, 'system');
                }
            }
        } else {
            throw new Error(data.error || 'Failed to generate shape');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    }
}

// Capture and Analyze Shape
async function captureAndAnalyzeShape(metadata) {
    try {
        const shapeContainer = canvasContent.querySelector('.shape-container');
        if (!shapeContainer) {
            console.warn('No shape container found for analysis');
            return null;
        }
        
        // Capture the shape using html2canvas
        const canvas = await html2canvas(shapeContainer, {
            backgroundColor: '#ffffff',
            scale: 2, // Higher quality
            logging: false
        });
        
        // Convert to base64
        const imageData = canvas.toDataURL('image/png');
        
        // Send for analysis
        const response = await fetch('/api/analyze-shape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                imageData,
                metadata
            })
        });
        
        const analysis = await response.json();
        return analysis;
        
    } catch (error) {
        console.error('Shape analysis error:', error);
        // Continue without analysis if it fails
        return null;
    }
}

// Add Message to Chat
function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    if (type === 'system') {
        messageDiv.innerHTML = `<p><em>${escapeHtml(text)}</em></p>`;
    } else {
        messageDiv.innerHTML = `<p>${escapeHtml(text)}</p>`;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Render Shape on Canvas
function renderShape(data) {
    // Clear empty state
    const emptyState = canvasContent.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Create shape container
    const shapeContainer = document.createElement('div');
    shapeContainer.className = 'shape-container generated-shape';
    
    // Create a unique ID for styles
    const uniqueId = `shape-${Date.now()}`;
    
    // Add CSS
    if (data.css) {
        const styleElement = document.createElement('style');
        // Update CSS to use ppt-shape- prefix as per system prompt
        let processedCSS = data.css;
        if (!data.css.includes('ppt-shape-')) {
            processedCSS = data.css.replace(/\.shape/g, '.ppt-shape');
        }
        styleElement.textContent = processedCSS.replace(/\.ppt-shape/g, `#${uniqueId} .ppt-shape`);
        document.head.appendChild(styleElement);
    }
    
    // Add HTML
    let processedHTML = data.html;
    if (!data.html.includes('ppt-shape')) {
        processedHTML = data.html.replace(/class="shape/g, 'class="ppt-shape');
    }
    shapeContainer.innerHTML = `<div id="${uniqueId}">${processedHTML}</div>`;
    
    // Clear previous shapes (optional - remove if you want to keep history)
    canvasContent.innerHTML = '';
    
    // Add to canvas
    canvasContent.appendChild(shapeContainer);
    
    // Execute JavaScript if provided
    if (data.js) {
        try {
            // Create a function to safely execute the JS in the shape context
            const executeShapeJS = new Function('container', data.js);
            executeShapeJS(shapeContainer);
        } catch (error) {
            console.warn('Error executing shape JavaScript:', error);
        }
    }
    
    // Reset zoom
    resetZoom();
    
    // Add iteration indicator if in feedback loop
    if (iterationCount > 1) {
        const iterationBadge = document.createElement('div');
        iterationBadge.className = 'iteration-badge';
        iterationBadge.textContent = `Iteration ${iterationCount}`;
        iterationBadge.style.cssText = 'position: absolute; top: 10px; right: 10px; background: #2563eb; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;';
        shapeContainer.appendChild(iterationBadge);
    }
}

// Zoom Functions
function adjustZoom(delta) {
    currentZoom = Math.max(0.5, Math.min(2, currentZoom + delta));
    canvasContent.style.transform = `scale(${currentZoom})`;
}

function resetZoom() {
    currentZoom = 1;
    canvasContent.style.transform = 'scale(1)';
}

// Export Shape
async function exportShape() {
    const shapeContainer = canvasContent.querySelector('.shape-container');
    if (!shapeContainer) {
        showError('No shape to export');
        return;
    }
    
    try {
        // Use html2canvas for high-quality export
        const canvas = await html2canvas(shapeContainer, {
            backgroundColor: '#ffffff',
            scale: 2,
            logging: false
        });
        
        // Convert to blob and download
        canvas.toBlob((blob) => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `powerpoint-shape-${Date.now()}.png`;
            a.click();
            URL.revokeObjectURL(url);
        });
        
        addMessage('Shape exported as PNG image.', 'system');
    } catch (error) {
        console.error('Export error:', error);
        showError('Failed to export shape');
    }
}

// UI Updates
function updateUI(generating) {
    sendButton.disabled = generating;
    promptInput.disabled = generating;
    
    const buttonText = sendButton.querySelector('.button-text');
    const spinner = sendButton.querySelector('.loading-spinner');
    
    if (generating) {
        buttonText.style.display = 'none';
        spinner.style.display = 'inline';
    } else {
        buttonText.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// Error Handling
function showError(message) {
    errorMessage.textContent = message;
    errorModal.style.display = 'flex';
}

function closeErrorModal() {
    errorModal.style.display = 'none';
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Example Prompts (Quick Actions)
const examplePrompts = [
    "Create a flowchart for user registration",
    "Draw a pie chart with 4 segments",
    "Make an organizational chart",
    "Design a mind map about AI",
    "Generate a Venn diagram with 3 circles"
];

// Add example prompt buttons (optional enhancement)
function addExampleButtons() {
    const examplesContainer = document.createElement('div');
    examplesContainer.className = 'example-prompts mt-2';
    examplesContainer.innerHTML = '<p style="font-size: 0.8rem; color: #666;">Quick examples (optimized for PowerPoint):</p>';
    
    const buttonsDiv = document.createElement('div');
    buttonsDiv.style.display = 'flex';
    buttonsDiv.style.flexWrap = 'wrap';
    buttonsDiv.style.gap = '0.5rem';
    buttonsDiv.style.marginTop = '0.5rem';
    
    examplePrompts.forEach(prompt => {
        const btn = document.createElement('button');
        btn.textContent = prompt.split(' ').slice(0, 3).join(' ') + '...';
        btn.style.fontSize = '0.75rem';
        btn.style.padding = '0.25rem 0.5rem';
        btn.style.border = '1px solid #d1d5db';
        btn.style.borderRadius = '4px';
        btn.style.background = 'white';
        btn.style.cursor = 'pointer';
        btn.onclick = () => {
            promptInput.value = prompt;
            promptInput.focus();
        };
        buttonsDiv.appendChild(btn);
    });
    
    examplesContainer.appendChild(buttonsDiv);
    
    // Add after the first system message
    const firstMessage = chatMessages.querySelector('.message.system');
    if (firstMessage) {
        firstMessage.appendChild(examplesContainer);
    }
}

// Initialize example buttons
addExampleButtons();

// Add feedback indicator styles
const style = document.createElement('style');
style.textContent = `
.iteration-badge {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.message.system {
    background-color: #FEF3C7;
    color: #92400E;
    font-size: 0.9rem;
}
`;
document.head.appendChild(style);