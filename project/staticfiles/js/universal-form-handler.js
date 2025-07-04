/**
 * Universal Form Handler with Loading Overlay
 * 
 * Usage:
 * 1. Add the CSS classes to your stylesheet
 * 2. Add the loading overlay HTML to your template
 * 3. Initialize with: new UniversalFormHandler('form-id', options)
 */

class UniversalFormHandler {
    constructor(formId, options = {}) {
        this.formId = formId;
        this.form = document.getElementById(formId);
        this.isSubmitting = false;
        
        // Default options
        this.options = {
            loadingSteps: [
                'Validando datos del formulario',
                'Procesando información',
                'Guardando datos',
                'Generando documentos',
                'Enviando confirmaciones',
                'Finalizando proceso'
            ],
            stepInterval: 2000,
            successRedirect: null,
            successRedirectDelay: 3000,
            confirmRedirect: true,
            validateOnBlur: true,
            fileMaxSize: 10 * 1024 * 1024, // 10MB
            allowedFileTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'],
            fieldTranslations: {
                'amount_paid': 'Monto pagado',
                'payment_date': 'Fecha de pago',
                'payment_method': 'Método de pago',
                'proof_of_payment': 'Comprobante de pago',
                'comments': 'Comentarios',
                'amount': 'Monto',
                'expense_date': 'Fecha del gasto',
                'expense_concept': 'Concepto del gasto',
                'proof_of_expense': 'Comprobante del gasto',
                'apartment_number': 'Número de departamento',
                'type': 'Tipo de reporte',
                'category': 'Categoría',
                'description': 'Descripción',
                'attachment': 'Adjunto'
            },
            ...options
        };

        this.init();
    }

    init() {
        if (!this.form) {
            console.error(`Form with ID '${this.formId}' not found`);
            return;
        }

        this.submitButton = this.form.querySelector('button[type="submit"], input[type="submit"]');
        this.uploadStatus = document.getElementById('upload-status') || 
                           document.querySelector('.upload-status, .form-status');
        this.loadingOverlay = document.getElementById('loading-overlay') || 
                             document.querySelector('.loading-overlay');
        this.loadingStep = document.querySelector('.loading-step');

        // Ensure loading overlay starts hidden
        this.hideLoadingOverlay();

        this.setupEventListeners();
        this.setupValidation();
        
        console.log('UniversalFormHandler initialized for form:', this.form.id);
    }

    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Prevent page unload during submission
        window.addEventListener('beforeunload', (e) => {
            if (this.isSubmitting) {
                e.preventDefault();
                e.returnValue = 'Su información se está procesando. ¿Está seguro de que desea salir?';
                return e.returnValue;
            }
        });

        // Keyboard shortcut (Ctrl+Enter)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !this.isSubmitting) {
                e.preventDefault();
                if (this.submitButton) {
                    this.submitButton.click();
                }
            }
        });
    }

    setupValidation() {
        const formFields = this.form.querySelectorAll('input, select, textarea');
        
        formFields.forEach(field => {
            // Clear error styling on input
            field.addEventListener('input', () => this.clearFieldError(field));
            field.addEventListener('change', () => this.clearFieldError(field));
            
            // Validate on blur if enabled
            if (this.options.validateOnBlur) {
                field.addEventListener('blur', () => this.validateField(field));
            }
        });

        // File input specific validation
        const fileInputs = this.form.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => this.validateFile(e.target));
        });
    }

    clearFieldError(field) {
        if (field.style.borderColor === 'rgb(244, 67, 54)') {
            field.style.borderColor = '#555';
        }
        if (this.uploadStatus && this.uploadStatus.classList.contains('error')) {
            this.showStatus('');
        }
    }

    validateField(field) {
        if (!field.hasAttribute('required')) return true;

        let fieldValue = this.getFieldValue(field);
        let isValid = !!fieldValue;

        if (!isValid) {
            field.style.borderColor = '#f44336';
        } else {
            field.style.borderColor = '#555';
        }

        return isValid;
    }

    validateFile(fileInput) {
        if (!fileInput.files.length) return true;

        const file = fileInput.files[0];
        
        // Size validation
        if (file.size > this.options.fileMaxSize) {
            const sizeMB = (this.options.fileMaxSize / (1024 * 1024)).toFixed(0);
            this.showStatus(`El archivo es demasiado grande. Máximo permitido: ${sizeMB}MB`, 'error', 5000);
            fileInput.value = '';
            fileInput.style.borderColor = '#f44336';
            return false;
        }

        // Type validation (skip for QYS form to allow all file types)
        if (this.formId !== 'qys-form' && this.options.allowedFileTypes.length > 0 && 
            !this.options.allowedFileTypes.includes(file.type)) {
            this.showStatus('Tipo de archivo no válido. Solo se permiten imágenes.', 'error', 5000);
            fileInput.value = '';
            fileInput.style.borderColor = '#f44336';
            return false;
        }

        fileInput.style.borderColor = '#555';
        this.showStatus('');
        return true;
    }

    getFieldValue(field) {
        if (field.type === 'file') {
            return field.files && field.files.length > 0 ? 'file_selected' : '';
        } else if (field.type === 'checkbox' || field.type === 'radio') {
            return field.checked ? field.value : '';
        } else {
            return field.value ? field.value.trim() : '';
        }
    }

    validateForm() {
        console.log('=== FORM VALIDATION START ===');
        const requiredFields = this.form.querySelectorAll('[required]');
        console.log(`Found ${requiredFields.length} required fields`);
        
        let isValid = true;
        let firstInvalidField = null;
        const errors = [];

        requiredFields.forEach((field, index) => {
            let fieldValue = this.getFieldValue(field);
            console.log(`Field ${index + 1}: ${field.name || field.id} = "${fieldValue}" (type: ${field.type})`);
            
            if (!fieldValue) {
                isValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
                
                field.style.borderColor = '#f44336';
                
                // Get field label for error message
                const label = this.form.querySelector(`label[for="${field.id}"]`) || 
                             this.form.querySelector(`label[for="${field.name}"]`);
                const fieldName = label ? label.textContent.replace(':', '') : 
                                 this.options.fieldTranslations[field.name] || field.name;
                errors.push(`${fieldName} es requerido`);
                console.log(`  -> INVALID: ${fieldName}`);
            } else {
                field.style.borderColor = '#555';
                console.log(`  -> VALID`);
            }
        });

        console.log(`=== VALIDATION RESULT: ${isValid ? 'VALID' : 'INVALID'} ===`);
        if (!isValid) {
            console.log('Errors:', errors);
        }

        if (!isValid && firstInvalidField) {
            firstInvalidField.focus();
            const errorMessage = errors.length > 0 ? 
                                 errors.slice(0, 3).join(', ') + (errors.length > 3 ? '...' : '') : 
                                 'Por favor complete todos los campos requeridos';
            this.showStatus(errorMessage, 'error', 8000);
        }

        return isValid;
    }

    async handleSubmit(e) {
        e.preventDefault();
        console.log('=== FORM SUBMIT EVENT ===');

        if (this.isSubmitting) {
            console.log('Form submission already in progress, ignoring');
            return;
        }

        console.log('Starting form submission process...');

        // Reset previous validation
        this.resetFormValidation();

        // Validate form
        if (!this.validateForm()) {
            console.log('Form validation failed - stopping submission');
            return;
        }

        console.log('Form validation passed - proceeding with submission');

        try {
            this.isSubmitting = true;
            this.showLoadingOverlay();
            this.disableForm();
            this.showStatus('');

            // FIXED: More robust FormData construction
            const formData = new FormData();
            
            // Add CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            formData.append('csrfmiddlewaretoken', csrfToken);
            
            // Add form-specific data FIRST
            if (this.formId === 'qys-form') {
                formData.append('submit_qys', '1');
                console.log('Added submit_qys flag for QYS form');
            }
            
            // Add all form fields manually to ensure they're included
            const formElements = this.form.querySelectorAll('input, select, textarea');
            formElements.forEach(element => {
                if (element.name && element.name !== 'csrfmiddlewaretoken') {
                    if (element.type === 'file') {
                        if (element.files && element.files.length > 0) {
                            formData.append(element.name, element.files[0]);
                            console.log(`Added file: ${element.name} = ${element.files[0].name}`);
                        } else if (element.hasAttribute('required')) {
                            console.log(`Required file field ${element.name} is empty`);
                        }
                    } else if (element.type === 'checkbox') {
                        if (element.checked) {
                            formData.append(element.name, element.value);
                            console.log(`Added checkbox: ${element.name} = ${element.value}`);
                        }
                    } else if (element.type === 'radio') {
                        if (element.checked) {
                            formData.append(element.name, element.value);
                            console.log(`Added radio: ${element.name} = ${element.value}`);
                        }
                    } else {
                        // For all other input types (text, select, textarea, etc.)
                        const value = element.value || '';
                        formData.append(element.name, value);
                        console.log(`Added field: ${element.name} = "${value}"`);
                    }
                }
            });

            // Debug form data
            console.log('=== FINAL FORM DATA DEBUG ===');
            for (let pair of formData.entries()) {
                console.log(`${pair[0]}: ${pair[1]}`);
            }

            console.log('Submitting form data...');

            const response = await fetch(this.form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });

            console.log('Received response:', response.status, response.statusText);

            if (!response.ok) {
                // Try to get error details from response
                let errorText = '';
                try {
                    const responseText = await response.text();
                    console.error('Response error text:', responseText);
                    errorText = responseText.substring(0, 200); // First 200 chars
                } catch (e) {
                    console.error('Could not read error response:', e);
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}${errorText ? ' - ' + errorText : ''}`);
            }

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const responseText = await response.text();
                console.error('Non-JSON response:', responseText);
                throw new Error('Server returned non-JSON response');
            }

            const data = await response.json();
            console.log('Response data:', data);

            this.hideLoadingOverlay();

            if (data.success) {
                this.handleSuccess(data);
            } else {
                this.handleError(data);
            }

        } catch (error) {
            console.error('Submission error:', error);
            this.hideLoadingOverlay();
            this.showStatus(
                'Error de conexión. Por favor verifique su conexión a internet e inténtelo de nuevo.', 
                'error'
            );
        } finally {
            this.enableForm();
            this.isSubmitting = false;
            console.log('Form submission process completed');
        }
    }

    handleSuccess(data) {
        let message = data.message || 'Información enviada exitosamente.';
        
        if (data.warning) {
            message += ` ${data.warning}`;
        }
        
        this.showStatus(message, 'success');
        this.form.reset();
        this.resetFormValidation();
        
        // Handle QYS-specific success actions
        if (this.formId === 'qys-form' && data.new_qys) {
            this.addNewQysRecord(data.new_qys);
            
            // Scroll to records section after a brief delay
            setTimeout(() => {
                const recordsSection = document.querySelector('.qys-records-section');
                if (recordsSection) {
                    recordsSection.scrollIntoView({ behavior: 'smooth' });
                }
            }, 1000);
        }
        
        // Handle redirect with appropriate message
        if (this.options.successRedirect) {
            setTimeout(() => {
                let confirmMessage = '';
                
                // Different messages based on redirect destination
                if (this.options.successRedirect.includes('/dashboard/')) {
                    confirmMessage = '¿Desea ir al panel de control para ver el estado actualizado?';
                } else if (this.options.successRedirect.includes('/documentos/')) {
                    confirmMessage = '¿Desea ir a la sección de documentos para ver el comprobante generado?';
                } else if (this.options.successRedirect.includes('/qys/')) {
                    confirmMessage = '¿Desea ir a la sección de comunicación para ver su reporte?';
                } else {
                    confirmMessage = '¿Desea continuar a la siguiente página?';
                }
                
                if (!this.options.confirmRedirect || confirm(confirmMessage)) {
                    window.location.href = this.options.successRedirect;
                }
            }, this.options.successRedirectDelay);
        }
    }

    handleError(data) {
        console.log('Form submission failed:', data);
        this.showStatus('Error al enviar la información. Por favor, revise los datos e inténtelo de nuevo.', 'error');
        
        if (data.errors) {
            console.error('Form errors:', data.errors);
            
            // Clear previous error messages
            if (this.uploadStatus) {
                const existingErrors = this.uploadStatus.querySelectorAll('.error-message');
                existingErrors.forEach(error => error.remove());
            }
            
            // Display field-specific errors
            Object.keys(data.errors).forEach(key => {
                if (this.uploadStatus) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-message';
                    
                    const fieldName = this.options.fieldTranslations[key] || key;
                    const errorMessages = Array.isArray(data.errors[key]) ? data.errors[key] : [data.errors[key]];
                    
                    errorDiv.textContent = `${fieldName}: ${errorMessages.join(', ')}`;
                    this.uploadStatus.appendChild(errorDiv);
                }
                
                // Highlight the problematic field
                const field = this.form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.style.borderColor = '#f44336';
                    field.focus();
                }
            });
        }
    }

    showLoadingOverlay() {
        console.log('Attempting to show loading overlay...');
        if (this.loadingOverlay) {
            console.log('Loading overlay found, showing...');
            this.loadingOverlay.classList.remove('loading-hidden');
            document.body.style.overflow = 'hidden';
            
            this.currentStep = 0;
            this.updateLoadingStep();
            
            this.stepInterval = setInterval(() => {
                this.currentStep = (this.currentStep + 1) % this.options.loadingSteps.length;
                this.updateLoadingStep();
            }, this.options.stepInterval);
            
        } else {
            console.error('Loading overlay not found!');
            if (this.submitButton) {
                this.submitButton.disabled = true;
                this.submitButton.textContent = 'Procesando...';
            }
        }
    }

    hideLoadingOverlay() {
        console.log('Attempting to hide loading overlay...');
        if (this.loadingOverlay) {
            this.loadingOverlay.classList.add('loading-hidden');
            document.body.style.overflow = '';
            
            if (this.stepInterval) {
                clearInterval(this.stepInterval);
                this.stepInterval = null;
            }
        } else {
            if (this.submitButton) {
                this.submitButton.disabled = false;
                this.submitButton.textContent = 'Enviar';
            }
        }
    }

    updateLoadingStep() {
        if (this.loadingStep && this.options.loadingSteps[this.currentStep]) {
            this.loadingStep.textContent = this.options.loadingSteps[this.currentStep];
        }
    }

    disableForm() {
        console.log('Disabling form elements...');
        const formElements = this.form.querySelectorAll('input, select, textarea, button');
        formElements.forEach(element => {
            element.disabled = true;
        });
        
        if (this.submitButton) {
            this.submitButton.disabled = true;
            this.submitButton.style.opacity = '0.6';
            this.submitButton.style.cursor = 'not-allowed';
        }
    }

    enableForm() {
        console.log('Enabling form elements...');
        const formElements = this.form.querySelectorAll('input, select, textarea, button');
        formElements.forEach(element => {
            element.disabled = false;
        });
        
        if (this.submitButton) {
            this.submitButton.disabled = false;
            this.submitButton.style.opacity = '1';
            this.submitButton.style.cursor = 'pointer';
        }
    }

    resetFormValidation() {
        const fields = this.form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            field.style.borderColor = '#555';
        });
    }

    showStatus(message, type = 'info', clearAfter = 0) {
        if (this.uploadStatus) {
            this.uploadStatus.innerHTML = '';
            this.uploadStatus.className = '';
            this.uploadStatus.textContent = message;
            
            if (type === 'success') {
                this.uploadStatus.classList.add('success');
            } else if (type === 'error') {
                this.uploadStatus.classList.add('error');
            }

            if (clearAfter > 0) {
                setTimeout(() => {
                    this.uploadStatus.innerHTML = '';
                    this.uploadStatus.className = '';
                }, clearAfter);
            }
        }
    }

    addNewQysRecord(newQys) {
        const recordsContainer = document.querySelector('.records-container');
        const noRecords = document.querySelector('.no-records');
        
        // Remove "no records" message if it exists
        if (noRecords) {
            noRecords.remove();
        }
        
        // Create records container if it doesn't exist
        if (!recordsContainer) {
            const recordsSection = document.querySelector('.qys-records-section');
            if (recordsSection) {
                const newContainer = document.createElement('div');
                newContainer.className = 'records-container';
                recordsSection.appendChild(newContainer);
                this.addNewQysRecord(newQys); // Retry after creating container
            }
            return;
        }
        
        // Create new record card
        const newCard = document.createElement('div');
        newCard.className = 'record-card';
        newCard.setAttribute('data-qys-id', newQys.id);
        
        // Build the new card HTML
        newCard.innerHTML = `
            <div class="record-header">
                <div class="record-type">
                    <span class="type-badge type-${newQys.type.toLowerCase()}">${newQys.type}</span>
                    <span class="category-badge">${newQys.category}</span>
                </div>
                <div class="record-apartment">
                    <span class="apartment-label">Apto</span>
                    <span class="apartment-number">${newQys.apartment_number}</span>
                </div>
            </div>
            
            <div class="record-body">
                <div class="record-description">
                    <p>${newQys.description}</p>
                </div>
                
                <div class="record-meta">
                    <div class="meta-item">
                        <span class="meta-label">Estado:</span>
                        <span class="status-badge status-${newQys.status.toLowerCase()}">${newQys.status}</span>
                    </div>
                    <div class="meta-item">
                        <span class="meta-label">Creado:</span>
                        <span class="meta-value">${newQys.created_at}</span>
                    </div>
                </div>
            </div>
            
            ${newQys.is_staff ? `
            <div class="record-actions">
                <div class="status-update">
                    <form method="post" action="/qys/" class="status-update-form">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${this.getCookie('csrftoken')}">
                        <input type="hidden" name="qys_id" value="${newQys.id}">
                        <select name="status" class="status-select" onchange="updateStatus(this)">
                            ${newQys.status_choices ? newQys.status_choices.map(([value, label]) => 
                                `<option value="${value}" ${newQys.status === value ? 'selected' : ''}>${label}</option>`
                            ).join('') : ''}
                        </select>
                        <input type="hidden" name="update_status" value="1">
                    </form>
                </div>
                <button class="delete-btn" onclick="deleteQyS(${newQys.id})" title="Eliminar reporte">
                    🗑️
                </button>
            </div>
            ` : ''}
        `;
        
        // Add to top of container with animation
        newCard.style.opacity = '0';
        newCard.style.transform = 'translateY(-20px)';
        recordsContainer.insertBefore(newCard, recordsContainer.firstChild);
        
        // Animate in
        setTimeout(() => {
            newCard.style.transition = 'all 0.3s ease';
            newCard.style.opacity = '1';
            newCard.style.transform = 'translateY(0)';
        }, 100);
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Auto-initialize for common forms
document.addEventListener('DOMContentLoaded', function() {
    console.log('Universal Form Handler: DOM loaded, looking for forms...');
    
    // Payment form
    if (document.getElementById('payment-form')) {
        console.log('Payment form found, initializing...');
        new UniversalFormHandler('payment-form', {
            successRedirect: '/dashboard/',
            loadingSteps: [
                'Validando datos del formulario',
                'Subiendo comprobante de pago',
                'Generando reporte PDF',
                'Actualizando información de pago',
                'Enviando confirmaciones por email',
                'Finalizando proceso'
            ]
        });
    }

    // Expense form
    if (document.getElementById('expense-form')) {
        console.log('Expense form found, initializing...');
        new UniversalFormHandler('expense-form', {
            successRedirect: '/documentos/',
            loadingSteps: [
                'Validando datos del formulario',
                'Subiendo comprobante de gasto',
                'Generando reporte PDF',
                'Actualizando información contable',
                'Finalizando proceso'
            ]
        });
    }

    // QyS form
    if (document.getElementById('qys-form')) {
        console.log('QyS form found, initializing...');
        new UniversalFormHandler('qys-form', {
            successRedirect: null, // Don't redirect, stay on same page
            confirmRedirect: false,
            loadingSteps: [
                'Validando datos del formulario',
                'Procesando queja/sugerencia',
                'Guardando información',
                'Enviando notificaciones',
                'Finalizando proceso'
            ],
            allowedFileTypes: [], // Allow all file types for QYS attachments
            fieldTranslations: {
                'apartment_number': 'Número de departamento',
                'type': 'Tipo de reporte',
                'category': 'Categoría',
                'description': 'Descripción',
                'attachment': 'Adjunto'
            }
        });
    }

    // Generic form handler for any other forms
    const otherForms = document.querySelectorAll('form[data-universal-handler="true"]');
    otherForms.forEach(form => {
        if (form.id) {
            console.log(`Generic form found: ${form.id}, initializing...`);
            new UniversalFormHandler(form.id, {
                loadingSteps: [
                    'Validando datos del formulario',
                    'Procesando información',
                    'Guardando datos',
                    'Finalizando proceso'
                ]
            });
        }
    });
    
    console.log('Universal Form Handler: Initialization complete');
});