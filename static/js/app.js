
/**
 * CivilAI Assistant - Main JavaScript Application
 * Common functionality and utilities for the civil engineering web app
 */

const CivilAI = {
    // Configuration
    config: {
        animationDuration: 300,
        toastDuration: 5000,
        maxFileSize: 16 * 1024 * 1024, // 16MB
        supportedImageTypes: ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/bmp']
    },

    // Initialize the application
    init() {
        this.initializeComponents();
        this.bindEvents();
        this.setupFormValidation();
        this.initializeAnimations();
        this.initializeTheme();
        console.log('CivilAI Assistant initialized successfully');
    },

    // Initialize theme system
    initializeTheme() {
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const html = document.documentElement;
        
        // Load saved theme or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        html.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                
                html.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                this.updateThemeIcon(newTheme);
            });
        }
    },

    updateThemeIcon(theme) {
        const themeIcon = document.getElementById('themeIcon');
        if (themeIcon) {
            themeIcon.className = theme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
        }
    },

    // Initialize Bootstrap components and common UI elements
    initializeComponents() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });

        // Auto-dismiss alerts after delay
        this.setupAutoDismissAlerts();
    },

    // Setup form validation
    setupFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    },

    // Setup auto-dismiss alerts
    setupAutoDismissAlerts() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(alert => {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, this.config.toastDuration);
        });
    },

    // Setup entrance animations
    initializeAnimations() {
        const animatedElements = document.querySelectorAll('.animate-on-scroll');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        });

        animatedElements.forEach(el => observer.observe(el));
    },

    // Common event bindings
    bindEvents() {
        // Handle file upload previews
        document.addEventListener('change', (e) => {
            if (e.target.type === 'file') {
                this.handleFilePreview(e.target);
            }
        });

        // Handle form submissions with loading states
        document.addEventListener('submit', (e) => {
            if (e.target.tagName === 'FORM') {
                this.handleFormSubmission(e.target);
            }
        });
    },

    // Handle file upload previews
    handleFilePreview(input) {
        if (input.files && input.files[0]) {
            const file = input.files[0];
            const preview = document.querySelector(`#${input.id}-preview`);
            
            if (preview && this.config.supportedImageTypes.includes(file.type)) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        }
    },

    // Handle form submissions
    handleFormSubmission(form) {
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            this.setLoadingState(submitBtn, true);
        }
    },

    // Set loading state for buttons
    setLoadingState(button, loading) {
        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            button.disabled = true;
        } else {
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            button.disabled = false;
        }
    },

    // Reset submit button state
    resetSubmitButton(button) {
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            button.disabled = false;
        }
    },

    // Show notification
    showNotification(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, this.config.toastDuration);
    },

    // Smooth scroll to element
    scrollToElement(element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },

    // Scroll to top
    scrollToTop() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    },

    // Check if element is in viewport
    isInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// Enhanced Chat functionality
CivilAI.Chat = {
    init() {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            this.setupChatScroll();
            this.setupMessageInput();
            this.setupChatForm();
        }
    },

    setupChatScroll() {
        const container = document.querySelector('.chat-container');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    },

    setupMessageInput() {
        const messageInput = document.getElementById('messageInput');
        const imageUpload = document.getElementById('imageUpload');
        
        if (messageInput) {
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const form = this.closest('form');
                    if (form) {
                        CivilAI.Chat.submitMessage(form);
                    }
                }
            });
        }
        
        if (imageUpload) {
            imageUpload.addEventListener('change', function(e) {
                CivilAI.Chat.handleImageUpload(e);
            });
        }
    },

    handleImageUpload(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('previewImg').src = e.target.result;
                document.getElementById('imagePreview').classList.remove('d-none');
            };
            reader.readAsDataURL(file);
        }
    },

    removeImage() {
        document.getElementById('imageUpload').value = '';
        document.getElementById('imagePreview').classList.add('d-none');
    },

    setupChatForm() {
        const chatForm = document.querySelector('#chatForm');
        if (chatForm) {
            chatForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.submitMessage(chatForm);
            });
        }
    },

    async submitMessage(form) {
        const messageInput = form.querySelector('#messageInput');
        const submitBtn = form.querySelector('button[type="submit"]');
        const chatContainer = document.querySelector('.chat-container');
        
        if (!messageInput.value.trim()) return;
        
        const userMessage = messageInput.value.trim();
        
        // Add user message to chat
        this.addMessage(userMessage, 'user');
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Clear input and disable submit
        messageInput.value = '';
        CivilAI.setLoadingState(submitBtn, true);
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userMessage })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            if (data.success) {
                this.addMessage(data.ai_response, 'bot');
            } else {
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                CivilAI.showNotification(data.error || 'Chat error', 'error');
            }
            
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Network error. Please check your connection and try again.', 'bot');
            CivilAI.showNotification('Network error', 'error');
        } finally {
            CivilAI.setLoadingState(submitBtn, false);
        }
    },

    addMessage(message, type) {
        const chatContainer = document.querySelector('.chat-container');
        if (!chatContainer) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${type}`;
        
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${type}`;
        
        // Check if message is long and should have "More Details" option
        const isLongMessage = message.length > 300;
        let displayMessage = message;
        let extraContent = '';
        
        if (isLongMessage && type === 'bot') {
            const sentences = message.split('. ');
            const firstPart = sentences.slice(0, 2).join('. ') + '.';
            const remainingPart = sentences.slice(2).join('. ');
            
            displayMessage = firstPart;
            extraContent = remainingPart;
        }
        
        bubble.innerHTML = `
            <div class="message-content">${this.formatMessage(displayMessage)}</div>
            ${extraContent ? `
                <button class="more-details-btn" onclick="CivilAI.Chat.toggleDetails(this)">
                    More Details <i class="fas fa-chevron-down"></i>
                </button>
                <div class="more-details-content" style="display: none;">
                    ${this.formatMessage(extraContent)}
                </div>
            ` : ''}
            <div class="message-timestamp">${new Date().toLocaleTimeString()}</div>
        `;
        
        messageDiv.appendChild(bubble);
        chatContainer.appendChild(messageDiv);
        
        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    },

    toggleDetails(button) {
        const content = button.nextElementSibling;
        const icon = button.querySelector('i');
        
        if (content.style.display === 'none') {
            content.style.display = 'block';
            button.innerHTML = 'Less Details <i class="fas fa-chevron-up"></i>';
        } else {
            content.style.display = 'none';
            button.innerHTML = 'More Details <i class="fas fa-chevron-down"></i>';
        }
    },

    showTypingIndicator() {
        const chatContainer = document.querySelector('.chat-container');
        if (!chatContainer) return;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message bot typing-indicator-message';
        typingDiv.innerHTML = `
            <div class="message-bubble bot">
                <div class="typing-indicator">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                    <span style="margin-left: 0.5rem;">CivilBot is typing...</span>
                </div>
            </div>
        `;
        
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    },

    hideTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator-message');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    },

    formatMessage(message) {
        // Convert newlines to <br> and preserve formatting
        return message.replace(/\n/g, '<br>');
    }
};

CivilAI.Calculator = {
    init() {
        this.setupCalculatorValidation();
        this.setupResultsDisplay();
    },

    setupCalculatorValidation() {
        const forms = document.querySelectorAll('.calculator-form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const inputs = form.querySelectorAll('input[required]');
                let isValid = true;
                
                inputs.forEach(input => {
                    if (!input.value || parseFloat(input.value) <= 0) {
                        isValid = false;
                        input.classList.add('is-invalid');
                    } else {
                        input.classList.remove('is-invalid');
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    CivilAI.showNotification('Please fill all required fields with valid values', 'warning');
                }
            });
        });
    },

    setupResultsDisplay() {
        const resultsSection = document.querySelector('.results-section');
        if (resultsSection) {
            CivilAI.scrollToElement(resultsSection);
        }
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize main app
    CivilAI.init();

    // Initialize page-specific modules based on current page
    const currentPage = document.body.getAttribute('data-page') || 
                       window.location.pathname.split('/').pop() || 
                       window.location.pathname;

    switch(currentPage) {
        case 'chat':
        case '/chat':
            CivilAI.Chat.init();
            break;
        case 'calculator':
        case '/calculator':
            CivilAI.Calculator.init();
            break;
    }

    // Add scroll to top button
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'btn btn-primary position-fixed bottom-0 end-0 m-4';
    scrollBtn.style.zIndex = '1050';
    scrollBtn.style.display = 'none';
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.addEventListener('click', CivilAI.scrollToTop);
    document.body.appendChild(scrollBtn);

    // Show/hide scroll to top button
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
});

// Handle page unload
window.addEventListener('beforeunload', function() {
    // Reset any loading states
    document.querySelectorAll('button[disabled]').forEach(btn => {
        CivilAI.resetSubmitButton(btn);
    });
});

// Export for global access
window.CivilAI = CivilAI;
