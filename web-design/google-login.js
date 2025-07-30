// Google OAuth Configuration
const GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';

// Initialize Google Sign-In
function initializeGoogleSignIn() {
    google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleCredentialResponse,
        auto_select: false,
        cancel_on_tap_outside: true
    });

    // Render the Google Sign-In button
    google.accounts.id.renderButton(
        document.getElementById('googleSignIn'),
        {
            theme: 'outline',
            size: 'large',
            width: '100%',
            text: 'continue_with',
            shape: 'rectangular'
        }
    );

    // Display the One Tap dialog
    google.accounts.id.prompt();
}

// Handle Google Sign-In response
function handleCredentialResponse(response) {
    console.log('Encoded JWT ID token: ' + response.credential);
    
    // Decode the JWT token to get user information
    const responsePayload = decodeJwtResponse(response.credential);
    
    console.log('ID: ' + responsePayload.sub);
    console.log('Full Name: ' + responsePayload.name);
    console.log('Given Name: ' + responsePayload.given_name);
    console.log('Family Name: ' + responsePayload.family_name);
    console.log('Image URL: ' + responsePayload.picture);
    console.log('Email: ' + responsePayload.email);

    // Handle successful login
    handleSuccessfulLogin(responsePayload);
}

// Decode JWT token
function decodeJwtResponse(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    
    return JSON.parse(jsonPayload);
}

// Handle successful login
function handleSuccessfulLogin(userInfo) {
    // Store user information
    localStorage.setItem('userInfo', JSON.stringify(userInfo));
    
    // Show success message
    showMessage('Login successful! Welcome, ' + userInfo.name, 'success');
    
    // Redirect or update UI
    setTimeout(() => {
        // Redirect to chat page
        window.location.href = 'chat.html';
    }, 2000);
}

// Show messages to user
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Add styles
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;
    
    if (type === 'success') {
        messageDiv.style.backgroundColor = '#34a853';
    } else if (type === 'error') {
        messageDiv.style.backgroundColor = '#ea4335';
    } else {
        messageDiv.style.backgroundColor = '#1a73e8';
    }
    
    document.body.appendChild(messageDiv);
    
    // Remove message after 3 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

// Email form validation
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Handle traditional email form submission
function handleEmailForm() {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const nextBtn = document.querySelector('.next-btn');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = emailInput.value.trim();
        const inputGroup = emailInput.parentElement;
        
        // Remove previous error states
        inputGroup.classList.remove('error');
        const existingError = inputGroup.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Validate email
        if (!email) {
            showInputError(inputGroup, 'Please enter your email');
            return;
        }
        
        if (!validateEmail(email)) {
            showInputError(inputGroup, 'Please enter a valid email address');
            return;
        }
        
        // Show loading state
        nextBtn.classList.add('loading');
        nextBtn.disabled = true;
        
        // Simulate email check (replace with actual API call)
        setTimeout(() => {
            nextBtn.classList.remove('loading');
            nextBtn.disabled = false;
            
            // Redirect to chat page
            window.location.href = 'chat.html';
        }, 1500);
    });
}

// Show input error
function showInputError(inputGroup, message) {
    inputGroup.classList.add('error');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    inputGroup.appendChild(errorDiv);
}

// Handle input focus and blur events for label animation
function handleInputLabels() {
    const inputs = document.querySelectorAll('.input-group input');
    
    inputs.forEach(input => {
        // Check if input has value on page load
        if (input.value) {
            input.setAttribute('data-has-value', 'true');
        }
        
        input.addEventListener('input', function() {
            if (this.value) {
                this.setAttribute('data-has-value', 'true');
            } else {
                this.removeAttribute('data-has-value');
            }
        });
        
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

// Sign out function
function signOut() {
    google.accounts.id.disableAutoSelect();
    localStorage.removeItem('userInfo');
    showMessage('Signed out successfully', 'info');
}

// Check if user is already logged in
function checkExistingLogin() {
    const userInfo = localStorage.getItem('userInfo');
    if (userInfo) {
        const user = JSON.parse(userInfo);
        console.log('User already logged in:', user);
        // Optionally redirect to dashboard
        // window.location.href = '/dashboard.html';
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check for existing login
    checkExistingLogin();
    
    // Handle input labels
    handleInputLabels();
    
    // Handle email form
    handleEmailForm();
    
    // Initialize Google Sign-In when the API is loaded
    if (typeof google !== 'undefined' && google.accounts) {
        initializeGoogleSignIn();
    } else {
        // Wait for Google API to load
        window.addEventListener('load', function() {
            setTimeout(initializeGoogleSignIn, 100);
        });
    }
});

// Add CSS animation for messages
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .input-group.focused label,
    .input-group input[data-has-value] + label {
        transform: translateY(-24px) scale(0.75);
        color: #1a73e8;
    }
`;
document.head.appendChild(style);