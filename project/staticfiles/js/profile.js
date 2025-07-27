// profile.js - Enhanced Version for Torres del Maurel
// Version: 2.0 - Improved error handling, accessibility, and user experience

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Profile.js v2.0 - Enhanced initialization starting...');
    
    const form = document.getElementById('profile-form');
    if (!form) {
        console.warn('⚠️ Profile form not found');
        return;
    }
    
    // Configuration
    const CONFIG = {
        AUTO_HIDE_DELAY: 5000,
        VALIDATION_DELAY: 300,
        MIN_PASSWORD_LENGTH: 8,
        FOCUS_HIGHLIGHT_COLOR: '#1896d1',
        ERROR_COLOR: '#ff6b6b',
        SUCCESS_COLOR: '#4CAF50'
    };
    
    // Enhanced form field management
    function initializeFormFields() {
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        console.log(`📋 Found ${inputs.length} form inputs`);
        
        inputs.forEach((input, index) => {
            // Add unique IDs if missing
            if (!input.id) {
                input.id = `profile-input-${index + 1}`;
            }
            
            // Enhanced focus handling
            input.addEventListener('focus', function() {
                console.log(`🔍 Focus on: ${this.id}`);
                this.style.boxShadow = `0 0 8px ${CONFIG.FOCUS_HIGHLIGHT_COLOR}`;
                this.style.borderColor = CONFIG.FOCUS_HIGHLIGHT_COLOR;
                
                // Clear any previous error states
                this.style.borderColor = this.style.borderColor || '#333';
                this.setAttribute('aria-invalid', 'false');
            });
            
            input.addEventListener('blur', function() {
                console.log(`👁️ Blur from: ${this.id}`);
                this.style.boxShadow = 'none';
                
                // Validate on blur
                validateField(this);
            });
            
            // Real-time validation for certain fields
            if (input.type === 'email') {
                let validationTimeout;
                input.addEventListener('input', function() {
                    clearTimeout(validationTimeout);
                    validationTimeout = setTimeout(() => {
                        validateField(this);
                    }, CONFIG.VALIDATION_DELAY);
                });
            }
        });
    }
    
    // Enhanced field validation
    function validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        const isRequired = field.hasAttribute('required');
        
        let isValid = true;
        let errorMessage = '';
        
        // Required field check
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'Este campo es requerido';
        }
        
        // Email validation
        else if (fieldType === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Ingrese un email válido';
            }
        }
        
        // Password validation
        else if (fieldType === 'password' && value) {
            if (value.length < CONFIG.MIN_PASSWORD_LENGTH) {
                isValid = false;
                errorMessage = `La contraseña debe tener al menos ${CONFIG.MIN_PASSWORD_LENGTH} caracteres`;
            }
        }
        
        // Update field appearance
        updateFieldValidationState(field, isValid, errorMessage);
        
        return isValid;
    }
    
    // Update field validation state
    function updateFieldValidationState(field, isValid, errorMessage = '') {
        // Remove existing error displays
        const existingError = field.parentNode.querySelector('.field-error-message');
        if (existingError) {
            existingError.remove();
        }
        
        if (isValid) {
            field.style.borderColor = '#333';
            field.setAttribute('aria-invalid', 'false');
            field.removeAttribute('aria-describedby');
        } else {
            field.style.borderColor = CONFIG.ERROR_COLOR;
            field.setAttribute('aria-invalid', 'true');
            
            // Add error message
            if (errorMessage) {
                const errorElement = document.createElement('div');
                errorElement.className = 'field-error-message';
                errorElement.style.cssText = `
                    color: ${CONFIG.ERROR_COLOR};
                    font-size: 0.85rem;
                    margin-top: 5px;
                    padding: 5px;
                    background: rgba(255, 107, 107, 0.1);
                    border-radius: 4px;
                    border-left: 3px solid ${CONFIG.ERROR_COLOR};
                `;
                errorElement.textContent = errorMessage;
                
                // For accessibility
                const errorId = `error-${field.id}`;
                errorElement.id = errorId;
                field.setAttribute('aria-describedby', errorId);
                
                field.parentNode.appendChild(errorElement);
            }
        }
    }
    
    // Enhanced form submission
    function handleFormSubmission() {
        form.addEventListener('submit', function(e) {
            console.log('📝 Form submission attempt');
            
            let isFormValid = true;
            const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
            
            // Validate all fields
            inputs.forEach(input => {
                const fieldValid = validateField(input);
                if (!fieldValid) {
                    isFormValid = false;
                }
            });
            
            // Password confirmation check (if applicable)
            const newPassword = form.querySelector('input[name*="new_password1"]');
            const confirmPassword = form.querySelector('input[name*="new_password2"]');
            
            if (newPassword && confirmPassword) {
                if (newPassword.value !== confirmPassword.value) {
                    isFormValid = false;
                    updateFieldValidationState(confirmPassword, false, 'Las contraseñas no coinciden');
                }
            }
            
            if (!isFormValid) {
                e.preventDefault();
                console.log('❌ Form validation failed');
                
                // Focus on first error field
                const firstError = form.querySelector('input[aria-invalid="true"]');
                if (firstError) {
                    firstError.focus();
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                // Show notification
                showNotification('Por favor, corrija los errores antes de continuar.', 'error');
                return;
            }
            
            console.log('✅ Form validation passed');
            showNotification('Actualizando perfil...', 'info');
        });
    }
    
    // Enhanced notification system
    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotification = document.querySelector('.profile-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        const notification = document.createElement('div');
        notification.className = 'profile-notification';
        
        const colors = {
            info: { bg: 'rgba(30, 144, 255, 0.2)', border: '#1E90FF', text: '#87ceeb' },
            success: { bg: 'rgba(40, 167, 69, 0.2)', border: '#28a745', text: '#98fb98' },
            error: { bg: 'rgba(220, 53, 69, 0.2)', border: '#dc3545', text: '#ff6b6b' },
            warning: { bg: 'rgba(255, 193, 7, 0.2)', border: '#ffc107', text: '#fff3cd' }
        };
        
        const color = colors[type] || colors.info;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            padding: 12px 20px;
            background: ${color.bg};
            border: 1px solid ${color.border};
            color: ${color.text};
            border-radius: 6px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            max-width: 350px;
            animation: slideInRight 0.3s ease-out;
        `;
        
        notification.textContent = message;
        
        // Add slide-in animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideInRight 0.3s ease-out reverse';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 4000);
        
        // Make it clickable to dismiss
        notification.addEventListener('click', function() {
            this.remove();
        });
        
        notification.style.cursor = 'pointer';
        notification.title = 'Click para cerrar';
    }
    
    // Enhanced accessibility features
    function enhanceAccessibility() {
        // Add live region for form status
        const liveRegion = document.createElement('div');
        liveRegion.id = 'profile-live-region';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        document.body.appendChild(liveRegion);
        
        // Announce form validation status
        window.announceToScreenReader = function(message) {
            liveRegion.textContent = message;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        };
        
        // Enhanced keyboard navigation
        const inputs = form.querySelectorAll('input, button');
        inputs.forEach((element, index) => {
            element.addEventListener('keydown', function(e) {
                // Enhanced Enter key handling
                if (e.key === 'Enter' && element.tagName === 'INPUT') {
                    const nextElement = inputs[index + 1];
                    if (nextElement) {
                        e.preventDefault();
                        nextElement.focus();
                    }
                }
            });
        });
    }
    
    // Initialize everything
    function initialize() {
        try {
            initializeFormFields();
            handleFormSubmission();
            enhanceAccessibility();
            
            console.log('✅ Profile.js v2.0 initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing profile.js:', error);
        }
    }
    
    // Start initialization
    initialize();
    
    // Export for debugging/testing
    window.ProfileSystem = {
        validateField,
        showNotification,
        version: '2.0'
    };
});