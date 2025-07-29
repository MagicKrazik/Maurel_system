// Enhanced pagos.js - Works with existing backend, provides better UX
document.addEventListener('DOMContentLoaded', function() {
    // Check if enhanced form handler is available
    if (typeof EnhancedFormHandler !== 'undefined') {
        // Enhanced form handler will take over
        console.log('Enhanced form handler loaded for payments');
        return;
    }

    // Fallback to existing functionality with improvements
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button') || document.querySelector('button[type="submit"]');
    const uploadStatus = document.getElementById('upload-status');
    
    if (!form || !submitButton) {
        console.warn('Payment form elements not found');
        return;
    }

    let isSubmitting = false;

    // Enhanced loading steps for better user feedback
    const loadingSteps = [
        'Validando información del pago...',
        'Guardando datos en el sistema...',
        'Generando comprobante PDF...',
        'Actualizando estado de pago...',
        'Enviando confirmaciones por email...',
        'Finalizando proceso...'
    ];

    let currentStep = 0;
    let stepInterval = null;

    function showEnhancedLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('loading-hidden');
            document.body.style.overflow = 'hidden';
            
            // Update title
            const titleElement = overlay.querySelector('.loading-text h3');
            if (titleElement) {
                titleElement.textContent = 'Procesando Pago';
            }
            
            // Start step progression
            currentStep = 0;
            updateLoadingStep();
            stepInterval = setInterval(() => {
                currentStep = (currentStep + 1) % loadingSteps.length;
                updateLoadingStep();
            }, 2500); // Slower progression for longer processes
        }
    }

    function updateLoadingStep() {
        const stepElement = document.querySelector('.loading-step');
        if (stepElement && loadingSteps[currentStep]) {
            stepElement.textContent = loadingSteps[currentStep];
        }
    }

    function hideEnhancedLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('loading-hidden');
            document.body.style.overflow = '';
            
            if (stepInterval) {
                clearInterval(stepInterval);
                stepInterval = null;
            }
        }
    }

    function validateForm() {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        let firstInvalidField = null;

        // Clear previous validation
        form.querySelectorAll('.error-highlight').forEach(el => {
            el.classList.remove('error-highlight');
        });

        requiredFields.forEach(field => {
            const value = field.type === 'file' ? field.files.length > 0 : field.value.trim();
            
            if (!value) {
                isValid = false;
                field.classList.add('error-highlight');
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
            }
        });

        if (!isValid && firstInvalidField) {
            firstInvalidField.focus();
            showStatus('Por favor complete todos los campos requeridos', 'error');
        }

        return isValid;
    }

    function showStatus(message, type = 'info') {
        if (uploadStatus) {
            uploadStatus.className = `message-container ${type}`;
            uploadStatus.textContent = message;
        }
    }

    function disableForm() {
        const elements = form.querySelectorAll('input, select, textarea, button');
        elements.forEach(el => {
            el.disabled = true;
            el.classList.add('form-disabled');
        });
    }

    function enableForm() {
        const elements = form.querySelectorAll('input, select, textarea, button');
        elements.forEach(el => {
            el.disabled = false;
            el.classList.remove('form-disabled');
        });
    }

    function showSuccessNotification(message, warning = null) {
        // Create floating success notification
        const notification = document.createElement('div');
        notification.className = 'completion-notification';
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '10001';
        
        notification.innerHTML = `
            <div class="notification-header">
                <span class="notification-icon">💰</span>
                <span class="notification-title">Pago Procesado Exitosamente</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="notification-body">
                <div class="notification-message">${message}</div>
                ${warning ? `<div class="notification-warning">${warning}</div>` : ''}
                <div class="notification-details">
                    <span class="status-item">✅ Pago registrado</span>
                    <span class="status-item">✅ PDF generado</span>
                    <span class="status-item">✅ Emails enviados</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 12 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => notification.remove(), 300);
        }, 12000);
    }

    // Form submission handler
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (isSubmitting) {
            return;
        }

        // Validate form
        if (!validateForm()) {
            return;
        }

        isSubmitting = true;
        showEnhancedLoadingOverlay();
        disableForm();
        showStatus('');

        // Prepare form data
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Submit to existing backend (no changes required)
        fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            hideEnhancedLoadingOverlay();
            
            if (data.success) {
                let message = data.message || 'Comprobante subido exitosamente.';
                let warning = data.warning || null;
                
                showStatus(message, 'success');
                showSuccessNotification(message, warning);
                
                // Reset form
                form.reset();
                
                // Optional redirect
                setTimeout(() => {
                    if (confirm('¿Desea ir al panel de control para ver el estado actualizado?')) {
                        window.location.href = '/dashboard/';
                    }
                }, 4000);
                
            } else {
                showStatus('Error al subir el comprobante. Por favor, revise la información.', 'error');
                
                if (data.errors) {
                    // Handle field-specific errors
                    Object.keys(data.errors).forEach(key => {
                        const field = form.querySelector(`[name="${key}"]`);
                        if (field) {
                            field.classList.add('error-highlight');
                        }
                    });
                }
            }
        })
        .catch(error => {
            console.error('Payment submission error:', error);
            hideEnhancedLoadingOverlay();
            showStatus('Error de conexión. Por favor, inténtelo de nuevo.', 'error');
        })
        .finally(() => {
            enableForm();
            isSubmitting = false;
        });
    });

    // Real-time field validation
    form.addEventListener('input', function(e) {
        if (e.target.classList.contains('error-highlight')) {
            e.target.classList.remove('error-highlight');
        }
    });

    form.addEventListener('change', function(e) {
        if (e.target.classList.contains('error-highlight')) {
            e.target.classList.remove('error-highlight');
        }
    });

    // File validation
    const fileInput = form.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                const file = this.files[0];
                const maxSize = 10 * 1024 * 1024; // 10MB
                
                if (file.size > maxSize) {
                    showStatus('El archivo es demasiado grande. Máximo permitido: 10MB', 'error');
                    this.value = '';
                    this.classList.add('error-highlight');
                } else {
                    this.classList.remove('error-highlight');
                    showStatus('');
                }
            }
        });
    }

    // Prevent page unload during submission
    window.addEventListener('beforeunload', function(e) {
        if (isSubmitting) {
            e.preventDefault();
            e.returnValue = 'Su pago se está procesando. ¿Está seguro de que desea salir?';
            return e.returnValue;
        }
    });
});