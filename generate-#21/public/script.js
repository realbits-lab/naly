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

// Send Message
async function handleSend() {
    const prompt = promptInput.value.trim();
    if (!prompt || isGenerating) return;
    
    isGenerating = true;
    updateUI(true);
    
    // Add user message
    addMessage(prompt, 'user');
    
    // Clear input
    promptInput.value = '';
    
    try {
        // Call API
        const response = await fetch('/api/generate-shape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Add assistant message
            addMessage('Shape generated successfully! Check the canvas.', 'assistant');
            
            // Render shape
            renderShape(data);
        } else {
            throw new Error(data.error || 'Failed to generate shape');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message);
        addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    } finally {
        isGenerating = false;
        updateUI(false);
    }
}

// Add Message to Chat
function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `<p>${escapeHtml(text)}</p>`;
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
        styleElement.textContent = data.css.replace(/\.shape/g, `#${uniqueId} .shape`);
        document.head.appendChild(styleElement);
    }
    
    // Add HTML
    shapeContainer.innerHTML = `<div id="${uniqueId}">${data.html}</div>`;
    
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
function exportShape() {
    const shapeContainer = canvasContent.querySelector('.shape-container');
    if (!shapeContainer) {
        showError('No shape to export');
        return;
    }
    
    // Simple implementation - you can enhance this with html2canvas or similar
    const htmlContent = shapeContainer.innerHTML;
    const styles = Array.from(document.styleSheets)
        .map(sheet => {
            try {
                return Array.from(sheet.cssRules)
                    .map(rule => rule.cssText)
                    .join('\n');
            } catch (e) {
                return '';
            }
        })
        .join('\n');
    
    const fullHTML = `
<!DOCTYPE html>
<html>
<head>
    <style>${styles}</style>
</head>
<body>
    ${htmlContent}
</body>
</html>`;
    
    // Download
    const blob = new Blob([fullHTML], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `shape-${Date.now()}.html`;
    a.click();
    URL.revokeObjectURL(url);
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
    examplesContainer.innerHTML = '<p style="font-size: 0.8rem; color: #666;">Quick examples:</p>';
    
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