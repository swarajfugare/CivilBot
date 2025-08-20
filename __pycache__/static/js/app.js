/**
 * CivilAI Assistant - Main JavaScript Application
 * Common functionality and utilities for the civil engineering web app
 */

// Global app object for namespace organization
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
        console.log('CivilAI Assistant initialized successfully');
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

    // Bind common event handlers
    bindEvents() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Form submission loading states
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmission.bind(this));
        });

        // File input validation
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', this.validateFileInput.bind(this));
        });

        // Number input validation
        document.querySelectorAll('input[type="number"]').forEach(input => {
            input.addEventListener('input', this.validateNumberInput.bind(this));
        });
    },

    // Setup form validation
    setupFormValidation() {
        // Add Bootstrap validation classes to forms
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    CivilAI.showNotification('Please fill in all required fields correctly.', 'warning');
                }
                form.classList.add('was-validated');
            });
        });

        // Real-time validation for required inputs
        document.querySelectorAll('input[required], select[required], textarea[required]').forEach(input => {
            input.addEventListener('blur', function() {
                if (this.value.trim() === '') {
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                } else {
                    this.classList.add('is-valid');
                    this.classList.remove('is-invalid');
                }
            });
        });
    },

    // Initialize animations and transitions
    initializeAnimations() {
        // Fade in cards on page load
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            setTimeout(() => {
                card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });

        // Add hover effects to interactive elements
        document.querySelectorAll('.card, .btn').forEach(element => {
            element.addEventListener('mouseenter', function() {
                this.style.transition = 'transform 0.2s ease, box-shadow 0.2s ease';
            });
        });
    },

    // Handle form submission with loading states
    handleFormSubmission(event) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn && form.checkValidity()) {
            // Show loading state
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
            submitBtn.disabled = true;

            // Store original state for potential reset
            submitBtn.dataset.originalText = originalText;

            // Reset button after timeout (fallback)
            setTimeout(() => {
                if (submitBtn.disabled) {
                    this.resetSubmitButton(submitBtn);
                }
            }, 30000); // 30 second timeout
        }
    },

    // Reset submit button to original state
    resetSubmitButton(button) {
        if (button && button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            button.disabled = false;
            delete button.dataset.originalText;
        }
    },

    // Validate file input
    validateFileInput(event) {
        const input = event.target;
        const file = input.files[0];
        
        if (!file) return;

        // Check file size
        if (file.size > this.config.maxFileSize) {
            this.showNotification(`File size too large. Maximum allowed size is ${this.formatFileSize(this.config.maxFileSize)}.`, 'error');
            input.value = '';
            return;
        }

        // Check file type for image inputs
        if (input.accept && input.accept.includes('image/*')) {
            if (!this.config.supportedImageTypes.includes(file.type)) {
                this.showNotification('Unsupported file format. Please select a valid image file.', 'error');
                input.value = '';
                return;
            }
        }

        // Show file validation success
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
    },

    // Validate number input
    validateNumberInput(event) {
        const input = event.target;
        const value = parseFloat(input.value);
        const min = parseFloat(input.min);
        const max = parseFloat(input.max);

        let isValid = true;
        let message = '';

        if (isNaN(value)) {
            isValid = false;
            message = 'Please enter a valid number.';
        } else if (min && value < min) {
            isValid = false;
            message = `Value must be at least ${min}.`;
        } else if (max && value > max) {
            isValid = false;
            message = `Value must be at most ${max}.`;
        }

        if (!isValid) {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            this.showFieldError(input, message);
        } else {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
            this.clearFieldError(input);
        }
    },

    // Show field-specific error
    showFieldError(input, message) {
        let errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            input.parentNode.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
    },

    // Clear field-specific error
    clearFieldError(input) {
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    },

    // Setup auto-dismiss alerts
    setupAutoDismissAlerts() {
        document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
            // Don't auto-dismiss error alerts
            if (!alert.classList.contains('alert-danger')) {
                setTimeout(() => {
                    if (alert.parentNode) {
                        const bsAlert = new bootstrap.Alert(alert);
                        bsAlert.close();
                    }
                }, this.config.toastDuration);
            }
        });
    },

    // Show notification (toast-like alert)
    showNotification(message, type = 'info') {
        const alertTypes = {
            'info': 'alert-info',
            'success': 'alert-success',
            'warning': 'alert-warning',
            'error': 'alert-danger'
        };

        const alertClass = alertTypes[type] || 'alert-info';
        const alertHTML = `
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        // Find or create notification container
        let container = document.querySelector('.notification-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notification-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1060';
            document.body.appendChild(container);
        }

        // Add notification
        container.insertAdjacentHTML('beforeend', alertHTML);

        // Auto-dismiss
        const newAlert = container.lastElementChild;
        setTimeout(() => {
            if (newAlert && newAlert.parentNode) {
                const bsAlert = new bootstrap.Alert(newAlert);
                bsAlert.close();
            }
        }, this.config.toastDuration);
    },

    // Get appropriate icon for alert type
    getAlertIcon(type) {
        const icons = {
            'info': 'info-circle',
            'success': 'check-circle',
            'warning': 'exclamation-triangle',
            'error': 'exclamation-circle'
        };
        return icons[type] || 'info-circle';
    },

    // Format file size for display
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Copy text to clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                document.execCommand('copy');
                this.showNotification('Copied to clipboard!', 'success');
            } catch (err) {
                this.showNotification('Failed to copy to clipboard.', 'error');
            }
            document.body.removeChild(textArea);
        });
    },

    // Format numbers with commas
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    // Debounce function for search inputs
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Scroll to top functionality
    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
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

// Feature-specific modules
CivilAI.Chat = {
    init() {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            this.setupChatScroll();
            this.setupMessageInput();
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
        if (messageInput) {
            messageInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.closest('form').submit();
                }
            });
        }
    }
};

CivilAI.Calculator = {
    init() {
        this.setupCalculatorValidation();
        this.setupResultsDisplay();
    },

    setupCalculatorValidation() {
        const form = document.querySelector('form[method="POST"]');
        if (form && document.querySelector('#span')) {
            form.addEventListener('submit', function(e) {
                const span = parseFloat(document.getElementById('span').value);
                const load = parseFloat(document.getElementById('load').value);
                
                if (span <= 0 || load <= 0) {
                    e.preventDefault();
                    CivilAI.showNotification('Please enter valid positive values for span and load.', 'warning');
                }
            });
        }
    },

    setupResultsDisplay() {
        // Add copy functionality to results
        document.querySelectorAll('.card .card-body').forEach(card => {
            if (card.querySelector('h6') && card.querySelector('h6').textContent.includes('Results')) {
                const copyBtn = document.createElement('button');
                copyBtn.className = 'btn btn-sm btn-outline-secondary float-end';
                copyBtn.innerHTML = '<i class="fas fa-copy me-1"></i>Copy';
                copyBtn.addEventListener('click', () => {
                    const text = card.textContent;
                    CivilAI.copyToClipboard(text);
                });
                card.querySelector('h6').appendChild(copyBtn);
            }
        });
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
