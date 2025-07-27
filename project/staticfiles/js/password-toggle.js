// password-toggle.js - FINAL WORKING VERSION
// Handles password toggles on all pages: login, profile, initial_profile_update, password_reset

(function() {
    'use strict';
    
    console.log('🔧 Password Toggle System - FINAL VERSION - Starting...');
    
    let initialized = false;
    let toggleCount = 0;
    const processedInputs = new Set();
    
    function createPasswordToggle(input) {
        // Create unique identifier for this input
        const inputId = input.id || input.name || `password-${Math.random().toString(36).substr(2, 9)}`;
        
        // Skip if already processed
        if (processedInputs.has(inputId)) {
            console.log(`⏭️ Skipping already processed input: ${inputId}`);
            return;
        }
        
        console.log(`🔨 Creating password toggle for: ${inputId}`);
        
        // Mark as processed
        processedInputs.add(inputId);
        input.dataset.toggleProcessed = 'true';
        
        // Check if input is already wrapped
        const existingWrapper = input.closest('.password-field-wrapper');
        if (existingWrapper) {
            console.log(`📦 Input ${inputId} already has wrapper, enhancing...`);
            enhanceExistingWrapper(existingWrapper, input, inputId);
            return;
        }
        
        // Create new wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'password-field-wrapper password-hidden';
        wrapper.id = `wrapper-${inputId}`;
        wrapper.style.cssText = `
            position: relative !important;
            display: block !important;
            width: 100% !important;
        `;
        
        // Insert wrapper and move input inside
        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);
        
        // Ensure input has proper styling
        input.style.paddingRight = '50px';
        input.classList.add('password-input');
        if (!input.id) {
            input.id = inputId;
        }
        
        // Create toggle button
        const toggleBtn = createToggleButton();
        wrapper.appendChild(toggleBtn);
        
        // Set up functionality
        setupToggleEvents(wrapper, input, toggleBtn, inputId);
        
        toggleCount++;
        console.log(`✅ Created password toggle for: ${inputId}`);
    }
    
    function enhanceExistingWrapper(wrapper, input, inputId) {
        // Check if toggle button already exists
        let toggleBtn = wrapper.querySelector('.password-toggle-btn');
        
        if (!toggleBtn) {
            console.log(`🔧 Adding missing toggle button to wrapper for: ${inputId}`);
            toggleBtn = createToggleButton();
            wrapper.appendChild(toggleBtn);
        }
        
        // Ensure proper classes
        wrapper.classList.add('password-field-wrapper');
        if (!wrapper.classList.contains('password-hidden') && !wrapper.classList.contains('password-visible')) {
            wrapper.classList.add('password-hidden');
        }
        
        input.classList.add('password-input');
        input.style.paddingRight = '50px';
        
        // Set up functionality
        setupToggleEvents(wrapper, input, toggleBtn, inputId);
        
        toggleCount++;
        console.log(`✅ Enhanced existing wrapper for: ${inputId}`);
    }
    
    function createToggleButton() {
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle-btn';
        toggleBtn.innerHTML = '👀';
        toggleBtn.setAttribute('aria-label', 'Mostrar contraseña');
        toggleBtn.setAttribute('title', 'Mostrar contraseña');
        
        toggleBtn.style.cssText = `
            position: absolute !important;
            right: 12px !important;
            top: 50% !important;
            transform: translateY(-50%) !important;
            background: transparent !important;
            border: 2px solid transparent !important;
            cursor: pointer !important;
            padding: 6px !important;
            width: 36px !important;
            height: 36px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            z-index: 10 !important;
            border-radius: 6px !important;
            color: #1E90FF !important;
            font-size: 16px !important;
            transition: all 0.2s ease !important;
            user-select: none !important;
        `;
        
        return toggleBtn;
    }
    
    function setupToggleEvents(wrapper, input, toggleBtn, inputId) {
        let autoHideTimeout = null;
        
        function togglePassword() {
            const isHidden = input.type === 'password';
            
            // Clear any existing timeout
            if (autoHideTimeout) {
                clearTimeout(autoHideTimeout);
                autoHideTimeout = null;
            }
            
            if (isHidden) {
                // Show password
                input.type = 'text';
                toggleBtn.innerHTML = '🙈';
                toggleBtn.style.color = '#ffc107';
                toggleBtn.setAttribute('aria-label', 'Ocultar contraseña');
                toggleBtn.setAttribute('title', 'Ocultar contraseña');
                wrapper.classList.remove('password-hidden');
                wrapper.classList.add('password-visible');
                
                console.log(`👀 Password shown for: ${inputId}`);
                
                // Auto-hide after 5 seconds
                autoHideTimeout = setTimeout(() => {
                    if (input.type === 'text') {
                        console.log(`⏰ Auto-hiding password for: ${inputId}`);
                        togglePassword();
                    }
                }, 5000);
                
            } else {
                // Hide password
                input.type = 'password';
                toggleBtn.innerHTML = '👀';
                toggleBtn.style.color = '#1E90FF';
                toggleBtn.setAttribute('aria-label', 'Mostrar contraseña');
                toggleBtn.setAttribute('title', 'Mostrar contraseña');
                wrapper.classList.remove('password-visible');
                wrapper.classList.add('password-hidden');
                
                console.log(`🙈 Password hidden for: ${inputId}`);
            }
            
            // Maintain focus and cursor position
            const cursorPosition = input.selectionStart || input.value.length;
            input.focus();
            setTimeout(() => {
                try {
                    input.setSelectionRange(cursorPosition, cursorPosition);
                } catch (e) {
                    // Ignore selection errors
                }
            }, 0);
        }
        
        // Event listeners
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log(`🖱️ Toggle clicked for: ${inputId}`);
            togglePassword();
        });
        
        toggleBtn.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                e.stopPropagation();
                console.log(`⌨️ Toggle activated via keyboard for: ${inputId}`);
                togglePassword();
            }
        });
        
        toggleBtn.addEventListener('mousedown', function(e) {
            e.preventDefault();
        });
        
        // Hover effects
        toggleBtn.addEventListener('mouseenter', function() {
            this.style.background = 'rgba(30, 144, 255, 0.1)';
            this.style.borderColor = 'rgba(30, 144, 255, 0.3)';
        });
        
        toggleBtn.addEventListener('mouseleave', function() {
            this.style.background = 'transparent';
            this.style.borderColor = 'transparent';
        });
        
        // Cleanup on element removal
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.removedNodes.forEach((node) => {
                    if (node === wrapper && autoHideTimeout) {
                        clearTimeout(autoHideTimeout);
                        processedInputs.delete(inputId);
                    }
                });
            });
        });
        
        if (wrapper.parentNode) {
            observer.observe(wrapper.parentNode, { childList: true });
        }
    }
    
    function scanForPasswordInputs() {
        // Find all password inputs, including those with data-password-toggle attribute
        const selectors = [
            'input[type="password"]:not([data-toggle-processed="true"])',
            'input[data-password-toggle="true"]:not([data-toggle-processed="true"])'
        ];
        
        let foundInputs = [];
        selectors.forEach(selector => {
            const inputs = document.querySelectorAll(selector);
            foundInputs = foundInputs.concat(Array.from(inputs));
        });
        
        // Remove duplicates
        foundInputs = foundInputs.filter((input, index, self) => 
            self.findIndex(i => i === input) === index
        );
        
        console.log(`🔍 Found ${foundInputs.length} password inputs to process`);
        
        foundInputs.forEach(input => {
            // Ensure it's a password type
            if (input.type !== 'password' && input.dataset.passwordToggle === 'true') {
                input.type = 'password';
            }
            createPasswordToggle(input);
        });
        
        return foundInputs.length > 0;
    }
    
    function initPasswordToggles() {
        if (initialized) {
            console.log('ℹ️ Password toggles already initialized, scanning for new inputs...');
            scanForPasswordInputs();
            return;
        }
        
        console.log('🚀 Initializing password toggle system...');
        
        const foundInputs = scanForPasswordInputs();
        
        if (foundInputs || toggleCount > 0) {
            initialized = true;
            console.log(`🎉 Password toggle system initialized! Total toggles: ${toggleCount}`);
        } else {
            console.log('ℹ️ No password inputs found');
        }
    }
    
    // Initialize with retries for dynamic content
    function initWithRetries(attempt = 1, maxAttempts = 5) {
        console.log(`🔄 Initialization attempt ${attempt}/${maxAttempts}`);
        
        try {
            initPasswordToggles();
            
            // If no toggles were created and we have retries left
            if (toggleCount === 0 && attempt < maxAttempts) {
                setTimeout(() => {
                    initWithRetries(attempt + 1, maxAttempts);
                }, 300);
                return;
            }
            
        } catch (error) {
            console.error('❌ Error during initialization:', error);
            
            if (attempt < maxAttempts) {
                setTimeout(() => {
                    initWithRetries(attempt + 1, maxAttempts);
                }, 300);
            }
        }
    }
    
    // Start initialization
    function startInitialization() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                console.log('📄 DOM loaded - starting password toggle initialization');
                setTimeout(() => {
                    initWithRetries();
                }, 200);
            });
        } else {
            console.log('📄 DOM already ready - starting password toggle initialization');
            setTimeout(() => {
                initWithRetries();
            }, 200);
        }
    }
    
    startInitialization();
    
    // Export for debugging and manual control
    window.PasswordToggleSystem = {
        init: initPasswordToggles,
        scan: scanForPasswordInputs,
        count: () => toggleCount,
        processed: () => processedInputs.size,
        version: 'FINAL',
        // Test function
        test: function() {
            console.log('🧪 Manual test - scanning for inputs...');
            return scanForPasswordInputs();
        }
    };
    
    console.log('📋 Password toggle system script loaded successfully');
    
})();