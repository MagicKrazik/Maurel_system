/**
 * Enhanced form handler that works with existing backend
 * Provides better loading states and user feedback
 * Does not modify any backend functionality
 */

class EnhancedFormHandler {
    constructor() {
        this.isSubmitting = false;
        this.loadingSteps = {
            payment: [
                'Validando información del pago...',
                'Guardando datos en el sistema...',
                'Generando comprobante PDF...',
                'Actualizando estado de pago...',
                'Enviando confirmaciones por email...',
                'Finalizando proceso...'
            ],
            qys: [
                'Validando información del reporte...',
                'Guardando comunicación...',
                'Generando reporte PDF...',
                'Enviando notificaciones...',
                'Finalizando proceso...'
            ]
        };
        this.currentStep = 0;
        this.stepInterval = null;
    }

    init() {
        this.setupPaymentForm();
        this.setupQYSForm();
        this.setupLoadingOverlay();
    }

    setupPaymentForm() {
        const form = document.getElementById('payment-form');
        const submitButton = document.getElementById('submit-button') || form?.querySelector('button[type="submit"]');
        
        if (form && submitButton) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmission(form, 'payment');
            });
        }
    }

    setupQYSForm() {
        const form = document.getElementById('qys-form');
        const submitButton = form?.querySelector('button[type="submit"]');
        
        if (form && submitButton) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmission(form, 'qys');
            });
        }
    }

    setupLoadingOverlay() {
        // Ensure loading overlay exists
        if (!document.getElementById('loading-overlay')) {
            this.createLoadingOverlay();
        }
    }

    createLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.className = 'loading-overlay loading-hidden';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="loading-spinner"></div>
                <div class="loading-text">
                    <h3>Procesando información</h3>
                    <p>Por favor espere, estamos procesando su solicitud...</p>
                    <p class="loading-step">Validando datos del formulario</p>
                </div>
            </div>
        `;
        document.body.appendChild(overlay);
    }

    async handleFormSubmission(form, formType) {
        if (this.isSubmitting) {
            return;
        }

        try {
            // Validate form
            if (!this.validateForm(form)) {
                return;
            }

            this.isSubmitting = true;
            this.showEnhancedLoading(formType);
            this.disableForm(form);

            // Prepare form data
            const formData = new FormData(form);
            
            // Add specific flags for QYS form
            if (formType === 'qys') {
                formData.append('submit_qys', '1');
            }

            // Submit to existing backend (no changes to backend required)
            const response = await fetch(form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            const data = await response.json();

            // Handle response
            if (data.success) {
                this.handleSuccess(form, formType, data);
            } else {
                this.handleError(form, data);
            }

        } catch (error) {
            console.error('Form submission error:', error);
            this.handleError(form, { message: 'Error de conexión. Por favor, inténtelo de nuevo.' });
        } finally {
            this.isSubmitting = false;
            this.hideEnhancedLoading();
            this.enableForm(form);
        }
    }

    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        let firstInvalidField = null;

        // Reset previous validation styling
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
            this.showMessage('Por favor complete todos los campos requeridos', 'error');
        }

        return isValid;
    }

    showEnhancedLoading(formType) {
        const overlay = document.getElementById('loading-overlay');
        if (!overlay) return;

        // Reset step counter
        this.currentStep = 0;
        const steps = this.loadingSteps[formType] || this.loadingSteps.payment;

        // Show overlay
        overlay.classList.remove('loading-hidden');
        document.body.style.overflow = 'hidden';

        // Update loading text based on form type
        const loadingText = overlay.querySelector('.loading-text h3');
        if (loadingText) {
            loadingText.textContent = formType === 'payment' ? 'Procesando Pago' : 'Procesando Comunicación';
        }

        // Start step progression
        this.updateLoadingStep(steps);
        this.stepInterval = setInterval(() => {
            this.currentStep = (this.currentStep + 1) % steps.length;
            this.updateLoadingStep(steps);
        }, 2000);
    }

    updateLoadingStep(steps) {
        const stepElement = document.querySelector('.loading-step');
        if (stepElement && steps[this.currentStep]) {
            stepElement.textContent = steps[this.currentStep];
        }
    }

    hideEnhancedLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('loading-hidden');
            document.body.style.overflow = '';
            
            // Clear step interval
            if (this.stepInterval) {
                clearInterval(this.stepInterval);
                this.stepInterval = null;
            }
        }
    }

    handleSuccess(form, formType, data) {
        // Show success message
        let message = data.message || 'Proceso completado exitosamente';
        
        // Add warning if provided
        if (data.warning) {
            message += ` ${data.warning}`;
        }
        
        this.showMessage(message, 'success');

        // Show processing completion notification
        this.showCompletionNotification(formType, data);

        // Reset form
        form.reset();
        this.clearValidationErrors(form);

        // Handle form-specific success actions
        if (formType === 'payment') {
            setTimeout(() => {
                if (confirm('¿Desea ir al panel de control para ver el estado actualizado?')) {
                    window.location.href = '/dashboard/';
                }
            }, 3000);
        } else if (formType === 'qys' && data.new_qys) {
            // Update QYS list if applicable
            this.updateQYSList(data.new_qys);
        }
    }

    handleError(form, data) {
        let message = data.message || 'Error al procesar la información';
        this.showMessage(message, 'error');

        // Handle field-specific errors
        if (data.errors) {
            this.displayFieldErrors(form, data.errors);
        }
    }

    showCompletionNotification(formType, data) {
        // Create floating notification
        const notification = document.createElement('div');
        notification.className = 'completion-notification';
        
        const title = formType === 'payment' ? 'Pago Procesado' : 'Comunicación Registrada';
        const icon = formType === 'payment' ? '💰' : '📝';
        
        notification.innerHTML = `
            <div class="notification-header">
                <span class="notification-icon">${icon}</span>
                <span class="notification-title">${title}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="notification-body">
                <div class="notification-message">${data.message}</div>
                ${data.warning ? `<div class="notification-warning">${data.warning}</div>` : ''}
                <div class="notification-details">
                    <span class="status-item">✅ Datos guardados</span>
                    <span class="status-item">📄 PDF generado</span>
                    <span class="status-item">📧 Emails enviados</span>
                </div>
            </div>
        `;

        // Position notification
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '10001';
        
        document.body.appendChild(notification);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => notification.remove(), 300);
        }, 10000);
    }

    updateQYSList(newQyS) {
        // Update QYS records if the container exists
        const recordsContainer = document.querySelector('.records-container');
        if (recordsContainer) {
            // Check if there's a "no records" message and remove it
            const noRecords = recordsContainer.querySelector('.no-records');
            if (noRecords) {
                noRecords.remove();
            }

            // Create new record card
            const recordCard = this.createQYSRecordCard(newQyS);
            recordsContainer.insertBefore(recordCard, recordsContainer.firstChild);
        }
    }

    createQYSRecordCard(qys) {
        const card = document.createElement('div');
        card.className = 'record-card';
        card.style.animation = 'fadeInUp 0.5s ease-out';
        
        card.innerHTML = `
            <div class="record-header">
                <div class="record-type">
                    <span class="type-badge type-${qys.type}">${qys.type}</span>
                    <span class="category-badge">${qys.category}</span>
                </div>
                <div class="record-apartment">
                    <span class="apartment-label">Depto</span>
                    <span class="apartment-number">${qys.apartment_number}</span>
                </div>
            </div>
            <div class="record-body">
                <div class="record-description">
                    <p>${qys.description}</p>
                </div>
                <div class="record-meta">
                    <div class="meta-item">
                        <span class="meta-label">Estado:</span>
                        <span class="status-badge status-${qys.status}">${qys.status}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Creado:</span>
                        <span class="meta-value">${qys.created_at}</span>
                    </div>
                </div>
            </div>
        `;
        
        return card;
    }

    showMessage(message, type) {
        // Find status containers
        const statusContainers = [
            document.getElementById('upload-status'),
            document.getElementById('submission-status'),
            document.querySelector('.status-message')
        ].filter(el => el);

        if (statusContainers.length === 0) {
            // Create status container if none exists
            const container = document.createElement('div');
            container.id = 'upload-status';
            container.className = `message-container ${type}`;
            container.textContent = message;
            
            // Insert after form or at top of main content
            const form = document.querySelector('form');
            if (form && form.parentNode) {
                form.parentNode.insertBefore(container, form.nextSibling);
            }
        } else {
            // Update existing containers
            statusContainers.forEach(container => {
                container.className = `message-container ${type}`;
                container.textContent = message;
            });
        }
    }

    displayFieldErrors(form, errors) {
        // Clear previous field errors
        form.querySelectorAll('.field-error').forEach(el => el.remove());

        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                field.classList.add('error-highlight');
                
                // Create error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'field-error';
                errorDiv.textContent = Array.isArray(errors[fieldName]) 
                    ? errors[fieldName].join(', ') 
                    : errors[fieldName];
                
                // Insert error message after field
                field.parentNode.insertBefore(errorDiv, field.nextSibling);
            }
        });
    }

    clearValidationErrors(form) {
        form.querySelectorAll('.error-highlight').forEach(el => {
            el.classList.remove('error-highlight');
        });
        form.querySelectorAll('.field-error').forEach(el => el.remove());
    }

    disableForm(form) {
        const elements = form.querySelectorAll('input, select, textarea, button');
        elements.forEach(el => {
            el.disabled = true;
            el.classList.add('form-disabled');
        });
    }

    enableForm(form) {
        const elements = form.querySelectorAll('input, select, textarea, button');
        elements.forEach(el => {
            el.disabled = false;
            el.classList.remove('form-disabled');
        });
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const enhancedHandler = new EnhancedFormHandler();
    enhancedHandler.init();
});

// Export for potential use in other scripts
window.EnhancedFormHandler = EnhancedFormHandler;