// Electronic Voting Systems Q&A Data
const votingSystemAnswers = {
    "How does electronic voting ensure ballot security and prevent fraud?": {
        answer: "Electronic voting systems employ multiple security layers including:\n\n• **End-to-end encryption** - All ballot data is encrypted from voter input to final tallying\n• **Digital signatures** - Each vote is cryptographically signed to prevent tampering\n• **Audit trails** - Comprehensive logging of all system activities\n• **Voter verification** - Paper backup receipts or voter-verified paper audit trails (VVPAT)\n• **Access controls** - Multi-factor authentication for system administrators\n• **Physical security** - Tamper-evident seals and secure storage of voting machines\n• **Network isolation** - Air-gapped systems or secure network protocols"
    },
    "What are the main components and architecture of an electronic voting system?": {
        answer: "Electronic voting systems typically consist of:\n\n• **Voter Registration Database** - Maintains eligible voter records and prevents duplicate voting\n• **Electronic Ballot Display** - Touch screen or other interface for vote selection\n• **Vote Recording System** - Securely captures and stores ballot choices\n• **Ballot Definition System** - Configures races, candidates, and ballot layouts\n• **Results Tabulation System** - Aggregates votes and generates reports\n• **Audit and Monitoring Tools** - Track system performance and detect anomalies\n• **Security Infrastructure** - Encryption, authentication, and access control systems\n• **Backup and Recovery Systems** - Ensure continuity during failures"
    },
    "How is voter authentication and identity verification handled in e-voting systems?": {
        answer: "Voter authentication in electronic voting involves multiple verification steps:\n\n• **Primary Identification** - Government-issued photo ID verification\n• **Voter Registration Check** - Real-time lookup in electoral database\n• **Biometric Verification** - Fingerprint or facial recognition (in some systems)\n• **Digital Certificates** - Cryptographic tokens for remote voting\n• **Signature Verification** - Comparison with registered signature samples\n• **Multi-factor Authentication** - Combination of something you know, have, and are\n• **Poll Book Integration** - Electronic check-in systems linked to voter rolls\n• **One-Person-One-Vote Controls** - Prevention of duplicate voting attempts"
    },
    "What backup and recovery procedures exist for electronic voting system failures?": {
        answer: "Electronic voting systems implement comprehensive backup strategies:\n\n• **Redundant Hardware** - Multiple voting machines and backup servers\n• **Paper Backup Systems** - Emergency paper ballots for complete system failures\n• **Data Replication** - Real-time copying of vote data to multiple secure locations\n• **Battery Backup** - Uninterruptible power supplies for temporary power loss\n• **Manual Procedures** - Documented processes for reverting to paper-based voting\n• **Rapid Deployment** - Pre-positioned replacement equipment\n• **Data Recovery Tools** - Specialized software to restore corrupted vote databases\n• **Communication Backups** - Satellite or cellular backup for network failures"
    },
    "How are electronic voting results audited and verified for accuracy?": {
        answer: "Electronic voting results undergo rigorous auditing processes:\n\n• **Risk-Limiting Audits** - Statistical sampling to verify election outcomes\n• **Post-Election Audits** - Mandatory review of paper trails against electronic results\n• **Logic and Accuracy Testing** - Pre-election testing with known vote patterns\n• **Parallel Testing** - Shadow elections run simultaneously for comparison\n• **Chain of Custody** - Documented tracking of all equipment and data\n• **Independent Verification** - Third-party examination of results and procedures\n• **Cryptographic Verification** - Mathematical proof of vote integrity\n• **Public Transparency** - Open source code review and public observation"
    }
};

// Initialize chat functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    setupEventListeners();
    loadUserInfo();
});

function initializeChat() {
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    
    // Auto-resize textarea
    messageInput.addEventListener('input', function() {
        this.style.height = '40px';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        
        // Enable/disable send button
        sendBtn.disabled = !this.value.trim();
    });
    
    // Send on Enter (but not Shift+Enter)
    messageInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function setupEventListeners() {
    // Send button
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
}

function loadUserInfo() {
    const userInfo = localStorage.getItem('userInfo');
    if (userInfo) {
        const user = JSON.parse(userInfo);
        const userAvatar = document.getElementById('userAvatar');
        if (user.picture) {
            userAvatar.innerHTML = `<img src="${user.picture}" alt="${user.name}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;">`;
        } else {
            userAvatar.textContent = user.name ? user.name.charAt(0).toUpperCase() : 'U';
        }
    }
}

function askQuestion(button) {
    const question = button.getAttribute('data-question');
    sendUserMessage(question);
    
    // Hide suggested questions after first interaction
    const suggestedQuestions = document.querySelector('.suggested-questions');
    suggestedQuestions.classList.add('hidden');
    
    // Show bot response
    setTimeout(() => {
        showBotResponse(question);
    }, 1000);
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    sendUserMessage(message);
    messageInput.value = '';
    messageInput.style.height = '40px';
    document.getElementById('sendBtn').disabled = true;
    
    // Hide suggested questions after first custom message
    const suggestedQuestions = document.querySelector('.suggested-questions');
    suggestedQuestions.classList.add('hidden');
    
    // Show typing indicator and then response
    showTypingIndicator();
    setTimeout(() => {
        hideTypingIndicator();
        showBotResponse(message);
    }, 1500);
}

function sendUserMessage(message) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'user-message message-fade-in';
    messageDiv.innerHTML = `
        <div class="message-bubble">${escapeHtml(message)}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showBotResponse(userMessage) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'bot-message message-fade-in';
    
    // Check if user asked for FAQ
    if (userMessage.toLowerCase().includes('faq')) {
        showSuggestedQuestions();
        return;
    }
    
    // Check if user input starts with # (error code)
    if (userMessage.trim().startsWith('#')) {
        const errorCode = userMessage.trim();
        const errorResponse = getErrorCodeSolution(errorCode);
        
        messageDiv.innerHTML = `
            <div class="bot-avatar">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div class="message-bubble">${formatResponse(errorResponse)}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        scrollToBottom();
        return;
    }
    
    // Find matching answer or provide a general response
    let response = findBestResponse(userMessage);
    
    messageDiv.innerHTML = `
        <div class="bot-avatar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="message-bubble">${formatResponse(response.answer)}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function findBestResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();
    
    // Check for exact or close matches
    for (const [question, response] of Object.entries(votingSystemAnswers)) {
        if (lowerMessage.includes(question.toLowerCase()) || question.toLowerCase().includes(lowerMessage)) {
            return response;
        }
    }
    
    // Check for keyword matches
    const keywords = {
        'security': votingSystemAnswers["How does electronic voting ensure ballot security and prevent fraud?"],
        'fraud': votingSystemAnswers["How does electronic voting ensure ballot security and prevent fraud?"],
        'encryption': votingSystemAnswers["How does electronic voting ensure ballot security and prevent fraud?"],
        'architecture': votingSystemAnswers["What are the main components and architecture of an electronic voting system?"],
        'components': votingSystemAnswers["What are the main components and architecture of an electronic voting system?"],
        'authentication': votingSystemAnswers["How is voter authentication and identity verification handled in e-voting systems?"],
        'identity': votingSystemAnswers["How is voter authentication and identity verification handled in e-voting systems?"],
        'verification': votingSystemAnswers["How is voter authentication and identity verification handled in e-voting systems?"],
        'backup': votingSystemAnswers["What backup and recovery procedures exist for electronic voting system failures?"],
        'recovery': votingSystemAnswers["What backup and recovery procedures exist for electronic voting system failures?"],
        'failure': votingSystemAnswers["What backup and recovery procedures exist for electronic voting system failures?"],
        'audit': votingSystemAnswers["How are electronic voting results audited and verified for accuracy?"],
        'accuracy': votingSystemAnswers["How are electronic voting results audited and verified for accuracy?"],
        'results': votingSystemAnswers["How are electronic voting results audited and verified for accuracy?"]
    };
    
    for (const [keyword, response] of Object.entries(keywords)) {
        if (lowerMessage.includes(keyword)) {
            return response;
        }
    }
    
    // Default response
    return {
        answer: "Thank you for your question about electronic voting systems. While I don't have a specific answer for that particular question, I can help you with information about:\n\n• Ballot security and fraud prevention\n• System architecture and components\n• Voter authentication processes\n• Backup and recovery procedures\n• Result auditing and verification\n\nPlease feel free to ask about any of these topics, or rephrase your question to be more specific."
    };
}


function getErrorCodeSolution(errorCode) {
    // Electronic voting system error codes database
    const errorCodes = {
        '#E001': 'Authentication Failed - Voter credentials could not be verified.\n\n**Solution:**\n• Verify voter ID matches registration records\n• Check for typos in voter information\n• Ensure voter is registered in correct precinct\n• Contact election administrator for manual verification',
        
        '#E002': 'System Timeout - Connection to voting database lost.\n\n**Solution:**\n• Wait 30 seconds and retry the operation\n• Check network connectivity\n• Verify server status with technical support\n• Use backup voting method if available',
        
        '#E003': 'Ballot Definition Error - Invalid ballot configuration detected.\n\n**Solution:**\n• Reload ballot definition from secure source\n• Verify ballot matches current election setup\n• Contact election administrator immediately\n• Do not proceed with voting until resolved',
        
        '#E004': 'Encryption Failure - Unable to encrypt ballot data.\n\n**Solution:**\n• Restart the voting terminal\n• Check cryptographic module status\n• Verify system certificates are valid\n• Switch to backup encryption system',
        
        '#E005': 'Vote Storage Error - Failed to save ballot securely.\n\n**Solution:**\n• Verify sufficient storage space available\n• Check write permissions on storage device\n• Test storage device integrity\n• Use alternative storage method if configured',
        
        '#E006': 'Audit Trail Failure - Unable to record transaction log.\n\n**Solution:**\n• Check audit log storage availability\n• Verify logging service is running\n• Ensure proper file permissions\n• Contact system administrator immediately',
        
        '#E007': 'Printer Malfunction - Voter receipt could not be printed.\n\n**Solution:**\n• Check printer paper supply\n• Verify printer cable connections\n• Restart printer service\n• Use manual receipt process if required',
        
        '#E008': 'Security Seal Breach - Tampering detected on voting device.\n\n**Solution:**\n• Immediately secure the device\n• Document the incident with photos\n• Contact election security officer\n• Remove device from service until investigation',
        
        '#E009': 'Power Supply Failure - Insufficient power to continue operation.\n\n**Solution:**\n• Check power cable connections\n• Verify UPS battery status\n• Switch to backup power source\n• Use emergency paper ballots if needed',
        
        '#E010': 'Clock Synchronization Error - System time is incorrect.\n\n**Solution:**\n• Synchronize with authorized time server\n• Verify network time protocol settings\n• Check system clock battery\n• Record time discrepancy for audit purposes'
    };
    
    const upperErrorCode = errorCode.toUpperCase();
    
    if (errorCodes[upperErrorCode]) {
        return `**Error Code:** ${upperErrorCode}\n\n${errorCodes[upperErrorCode]}`;
    } else {
        // Extract just the error code part for display
        const codeNumber = errorCode.substring(1); // Remove the #
        return `**Error Code:** ${errorCode}\n\nThis error code is not in our current database. For electronic voting system errors:\n\n**General Troubleshooting Steps:**\n• Document the exact error message and time\n• Take a screenshot if possible\n• Note what action triggered the error\n• Contact your election administrator immediately\n• Do not attempt to bypass security measures\n• Use backup voting procedures if available\n\n**Common Error Code Ranges:**\n• #E001-E010: System and authentication errors\n• #E011-E020: Network and communication errors\n• #E021-E030: Hardware and device errors\n• #E031-E040: Security and encryption errors\n\nFor immediate assistance, contact technical support with the error code **${errorCode}**.`;
    }
}

function showSuggestedQuestions() {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'bot-message message-fade-in';
    
    messageDiv.innerHTML = `
        <div class="bot-avatar">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div class="message-bubble">
            <p style="margin-bottom: 16px;">Here are the frequently asked questions about electronic voting systems:</p>
            <div class="question-grid">
                <button class="question-btn" onclick="askQuestion(this)" data-question="How does electronic voting ensure ballot security and prevent fraud?" style="margin-bottom: 8px;">
                    <span class="question-icon">🔒</span>
                    <span class="question-text">How does electronic voting ensure ballot security and prevent fraud?</span>
                </button>
                
                <button class="question-btn" onclick="askQuestion(this)" data-question="What are the main components and architecture of an electronic voting system?" style="margin-bottom: 8px;">
                    <span class="question-icon">⚙️</span>
                    <span class="question-text">What are the main components and architecture of an electronic voting system?</span>
                </button>
                
                <button class="question-btn" onclick="askQuestion(this)" data-question="How is voter authentication and identity verification handled in e-voting systems?" style="margin-bottom: 8px;">
                    <span class="question-icon">👤</span>
                    <span class="question-text">How is voter authentication and identity verification handled in e-voting systems?</span>
                </button>
                
                <button class="question-btn" onclick="askQuestion(this)" data-question="What backup and recovery procedures exist for electronic voting system failures?" style="margin-bottom: 8px;">
                    <span class="question-icon">💾</span>
                    <span class="question-text">What backup and recovery procedures exist for electronic voting system failures?</span>
                </button>
                
                <button class="question-btn" onclick="askQuestion(this)" data-question="How are electronic voting results audited and verified for accuracy?" style="margin-bottom: 0;">
                    <span class="question-icon">📊</span>
                    <span class="question-text">How are electronic voting results audited and verified for accuracy?</span>
                </button>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

function showTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'flex';
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'none';
}

function formatResponse(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n• /g, '<br>• ')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

function goBack() {
    if (document.referrer && document.referrer.includes('google-login.html')) {
        window.history.back();
    } else {
        window.location.href = 'google-login.html';
    }
}

// Initialize welcome message animation
setTimeout(() => {
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.classList.add('message-fade-in');
    }
}, 300);