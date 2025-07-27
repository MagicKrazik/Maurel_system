// initial_profile_update.js - Enhanced Version for Torres del Maurel
// Version: 2.1 - Removed progress indicator, kept all other functionalities

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Initial Profile Update v2.1 - Starting enhanced initialization...');
    
    const form = document.getElementById('profile-update-form');
    if (!form) {
        console.warn('⚠️ Profile update form not found');
        return;
    }
    
    // Configuration
    const CONFIG = {
        AUTO_HIDE_DELAY: 5000,
        VALIDATION_DELAY: 300,
        MIN_PASSWORD_LENGTH: 8,
        FOCUS_HIGHLIGHT_COLOR: '#1896d1',
        ERROR_COLOR: '#ff6b6b',
        SUCCESS_COLOR: '#4CAF50',
        WARNING_COLOR: '#ffc107'
    };
    
    // Enhanced form field management with onboarding guidance
    function initializeFormFields() {
        const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        console.log(`📋 Found ${inputs.length} form inputs for initial profile setup`);
        
        inputs.forEach((input, index) => {
            // Add unique IDs if missing
            if (!input.id) {
                input.id = `initial-profile-input-${index + 1}`;
            }
            
            // Enhanced focus handling with onboarding hints
            input.addEventListener('focus', function() {
                console.log(`🔍 Focus on: ${this.id} (Step ${getCurrentStep(this)})`);
                this.style.boxShadow = `0 0 8px ${CONFIG.FOCUS_HIGHLIGHT_COLOR}`;
                this.style.borderColor = CONFIG.FOCUS_HIGHLIGHT_COLOR;
                
                // Show contextual help
                showContextualHelp(this);
                
                // Clear any previous error states
                this.setAttribute('aria-invalid', 'false');
            });
            
            input.addEventListener('blur', function() {
                console.log(`👁️ Blur from: ${this.id}`);
                this.style.boxShadow = 'none';
                
                // Validate on blur
                validateField(this);
                
                // Hide contextual help
                hideContextualHelp();
            });
            
            // Real-time validation for email and passwords
            if (input.type === 'email' || input.type === 'password') {
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
    
    // Determine which step a field belongs to
    function getCurrentStep(field) {
        const passwordSection = field.closest('.form-section');
        if (!passwordSection) return 1;
        
        const sectionHeading = passwordSection.querySelector('h3');
        if (sectionHeading && sectionHeading.textContent.includes('Contraseña')) {
            return 1;
        }
        return 2;
    }
    
    // Show contextual help for onboarding
    function showContextualHelp(field) {
        hideContextualHelp(); // Remove any existing help
        
        let helpText = '';
        const fieldType = field.type;
        const fieldName = field.name;
        
        if (fieldType === 'password') {
            if (fieldName.includes('old') || fieldName.includes('current')) {
                helpText = '🔐 Ingrese la contraseña temporal que se le proporcionó';
            } else if (fieldName.includes('new')) {
                helpText = '🆕 Cree una contraseña segura (mínimo 8 caracteres, combine letras y números)';
            } else {
                helpText = '🔄 Confirme su nueva contraseña';
            }
        } else if (fieldType === 'email') {
            helpText = '📧 Ingrese su dirección de email para recibir notificaciones importantes';
        } else if (fieldName.includes('phone')) {
            helpText = '📱 Número de teléfono para contacto de emergencia';
        }
        
        if (helpText) {
            const helpElement = document.createElement('div');
            helpElement.className = 'contextual-help';
            helpElement.style.cssText = `
                position: absolute;
                top: -45px;
                left: 0;
                right: 0;
                background: rgba(30, 144, 255, 0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 0.85rem;
                z-index: 100;
                animation: helpSlideDown 0.3s ease-out;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
            `;
            helpElement.textContent = helpText;
            
            // Position relative to field wrapper
            const wrapper = field.closest('.password-field-wrapper') || field.parentNode;
            if (wrapper) {
                wrapper.style.position = 'relative';
                wrapper.appendChild(helpElement);
            }
            
            // Add animation keyframes
            if (!document.querySelector('#help-animations')) {
                const style = document.createElement('style');
                style.id = 'help-animations';
                style.textContent = `
                    @keyframes helpSlideDown {
                        from { opacity: 0; transform: translateY(-10px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                `;
                document.head.appendChild(style);
            }
        }
    }
    
    // Hide contextual help
    function hideContextualHelp() {
        const existingHelp = document.querySelector('.contextual-help');
        if (existingHelp) {
            existingHelp.style.animation = 'helpSlideDown 0.3s ease-out reverse';
            setTimeout(() => {
                if (existingHelp.parentNode) {
                    existingHelp.remove();
                }
            }, 300);
        }
    }
    
    // Enhanced field validation with onboarding-specific checks
    function validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        const fieldName = field.name;
        const isRequired = field.hasAttribute('required');
        
        let isValid = true;
        let errorMessage = '';
        let warningMessage = '';
        
        // Required field check
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'Este campo es requerido para completar la configuración inicial';
        }
        
        // Email validation
        else if (fieldType === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Ingrese un email válido (ejemplo: usuario@dominio.com)';
            }
        }
        
        // Password validation with onboarding context
        else if (fieldType === 'password' && value) {
            if (fieldName.includes('new')) {
                if (value.length < CONFIG.MIN_PASSWORD_LENGTH) {
                    isValid = false;
                    errorMessage = `Su nueva contraseña debe tener al menos ${CONFIG.MIN_PASSWORD_LENGTH} caracteres`;
                } else {
                    // Check password strength
                    const strength = checkPasswordStrength(value);
                    if (strength.score < 60) {
                        warningMessage = `Contraseña ${strength.label}: considere usar mayúsculas, números y símbolos`;
                    }
                }
            }
        }
        
        // Update field appearance
        updateFieldValidationState(field, isValid, errorMessage, warningMessage);
        
        return isValid;
    }
    
    // Password strength checker
    function checkPasswordStrength(password) {
        if (!password) return { score: 0, label: 'Sin contraseña' };
        
        let score = 0;
        const checks = {
            length: password.length >= CONFIG.MIN_PASSWORD_LENGTH,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            numbers: /\d/.test(password),
            special: /[!@#$%^&*(),.?":{}|<>]/.test(password)
        };
        
        Object.values(checks).forEach(check => check && score++);
        
        if (score < 2) return { score: 20, label: 'Débil' };
        if (score < 4) return { score: 60, label: 'Media' };
        return { score: 100, label: 'Fuerte' };
    }
    
    // Update field validation state with warning support
    function updateFieldValidationState(field, isValid, errorMessage = '', warningMessage = '') {
        // Remove existing messages
        const existingError = field.parentNode.querySelector('.field-error-message');
        const existingWarning = field.parentNode.querySelector('.field-warning-message');
        
        if (existingError) existingError.remove();
        if (existingWarning) existingWarning.remove();
        
        if (isValid) {
            field.style.borderColor = warningMessage ? CONFIG.WARNING_COLOR : '#333';
            field.setAttribute('aria-invalid', 'false');
            
            // Show warning if exists
            if (warningMessage) {
                const warningElement = document.createElement('div');
                warningElement.className = 'field-warning-message';
                warningElement.style.cssText = `
                    color: ${CONFIG.WARNING_COLOR};
                    font-size: 0.85rem;
                    margin-top: 5px;
                    padding: 5px;
                    background: rgba(255, 193, 7, 0.1);
                    border-radius: 4px;
                    border-left: 3px solid ${CONFIG.WARNING_COLOR};
                `;
                warningElement.textContent = '⚠️ ' + warningMessage;
                field.parentNode.appendChild(warningElement);
            }
            
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
                errorElement.textContent = '❌ ' + errorMessage;
                
                const errorId = `error-${field.id}`;
                errorElement.id = errorId;
                field.setAttribute('aria-describedby', errorId);
                
                field.parentNode.appendChild(errorElement);
            }
        }
    }
    
    // Enhanced form submission with onboarding completion
    function handleFormSubmission() {
        form.addEventListener('submit', function(e) {
            console.log('📝 Initial profile update submission attempt');
            
            let isFormValid = true;
            const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
            
            // Hide any contextual help
            hideContextualHelp();
            
            // Validate all fields
            inputs.forEach(input => {
                const fieldValid = validateField(input);
                if (!fieldValid) {
                    isFormValid = false;
                }
            });
            
            // Password confirmation check
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
                console.log('❌ Initial profile validation failed');
                
                // Focus on first error field
                const firstError = form.querySelector('input[aria-invalid="true"]');
                if (firstError) {
                    firstError.focus();
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                
                // Show onboarding-specific error message
                showOnboardingNotification('Por favor, complete todos los campos requeridos para finalizar la configuración.', 'error');
                return;
            }
            
            console.log('✅ Initial profile validation passed');
            
            // Show completion message
            showOnboardingNotification('¡Excelente! Configurando su perfil...', 'success');
        });
    }
    
    // Onboarding-specific notification system
    function showOnboardingNotification(message, type = 'info') {
        const existingNotification = document.querySelector('.onboarding-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        const notification = document.createElement('div');
        notification.className = 'onboarding-notification';
        
        const colors = {
            info: { bg: 'rgba(30, 144, 255, 0.95)', border: '#1E90FF', text: '#ffffff' },
            success: { bg: 'rgba(40, 167, 69, 0.95)', border: '#28a745', text: '#ffffff' },
            error: { bg: 'rgba(220, 53, 69, 0.95)', border: '#dc3545', text: '#ffffff' },
            warning: { bg: 'rgba(255, 193, 7, 0.95)', border: '#ffc107', text: '#000000' }
        };
        
        const color = colors[type] || colors.info;
        
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1001;
            padding: 15px 25px;
            background: ${color.bg};
            border: 2px solid ${color.border};
            color: ${color.text};
            border-radius: 25px;
            font-weight: 500;
            font-size: 1rem;
            text-align: center;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
            max-width: 400px;
            animation: onboardingBounce 0.5s ease-out;
        `;
        
        notification.textContent = message;
        
        // Add bounce animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes onboardingBounce {
                0% { transform: translateX(-50%) translateY(-20px) scale(0.8); opacity: 0; }
                60% { transform: translateX(-50%) translateY(5px) scale(1.05); opacity: 1; }
                100% { transform: translateX(-50%) translateY(0) scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'onboardingBounce 0.3s ease-out reverse';
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        }, 5000);
    }
    
    // Initialize everything
    function initialize() {
        try {
            initializeFormFields();
            handleFormSubmission();
            
            console.log('✅ Initial Profile Update v2.1 initialized successfully');
            
            // Welcome message
            setTimeout(() => {
                showOnboardingNotification('¡Bienvenido! Complete estos pasos para configurar su cuenta.', 'info');
            }, 500);
            
        } catch (error) {
            console.error('❌ Error initializing initial_profile_update.js:', error);
            showOnboardingNotification('Error al cargar el sistema de configuración', 'error');
        }
    }
    
    // Start initialization
    initialize();
    
    // Export for debugging/testing
    window.InitialProfileSystem = {
        validateField,
        showOnboardingNotification,
        version: '2.1'
    };
});