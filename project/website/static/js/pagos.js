document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button') || document.querySelector('button[type="submit"]');
    const uploadStatus = document.getElementById('upload-status');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingStep = document.querySelector('.loading-step');

    // Debug logging
    console.log('Elements found:');
    console.log('Form:', form);
    console.log('Submit button:', submitButton);
    console.log('Upload status:', uploadStatus);
    console.log('Loading overlay:', loadingOverlay);
    console.log('Loading step:', loadingStep);

    // Validation flags
    let isSubmitting = false;

    // Ensure loading overlay is hidden on page load
    if (loadingOverlay) {
        loadingOverlay.classList.add('loading-hidden');
        console.log('Loading overlay initialized as hidden');
    }

    // Loading steps for user feedback
    const loadingSteps = [
        'Validando datos del formulario',
        'Subiendo comprobante de pago',
        'Generando reporte PDF',
        'Actualizando información de pago',
        'Enviando confirmaciones por email',
        'Finalizando proceso'
    ];

    let currentStep = 0;

    function showLoadingOverlay() {
        console.log('Attempting to show loading overlay...');
        if (loadingOverlay) {
            console.log('Loading overlay found, showing...');
            loadingOverlay.classList.remove('loading-hidden');
            document.body.style.overflow = 'hidden'; // Prevent scrolling
            currentStep = 0;
            updateLoadingStep();
            // Start cycling through loading steps
            const stepInterval = setInterval(() => {
                currentStep = (currentStep + 1) % loadingSteps.length;
                updateLoadingStep();
            }, 2000); // Change step every 2 seconds
            
            // Store interval for cleanup
            loadingOverlay.stepInterval = stepInterval;
        } else {
            console.error('Loading overlay not found!');
            // Fallback: disable submit button and show text
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Procesando...';
            }
        }
    }

    function hideLoadingOverlay() {
        console.log('Attempting to hide loading overlay...');
        if (loadingOverlay) {
            loadingOverlay.classList.add('loading-hidden');
            document.body.style.overflow = ''; // Restore scrolling
            // Clear the step interval
            if (loadingOverlay.stepInterval) {
                clearInterval(loadingOverlay.stepInterval);
                loadingOverlay.stepInterval = null;
            }
        } else {
            // Fallback: re-enable submit button
            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = 'Subir Comprobante';
            }
        }
    }

    function updateLoadingStep() {
        if (loadingStep && loadingSteps[currentStep]) {
            loadingStep.textContent = loadingSteps[currentStep];
        }
    }

    function showStatus(message, type = 'info', clearAfter = 0) {
        if (uploadStatus) {
            uploadStatus.innerHTML = '';
            uploadStatus.className = '';
            uploadStatus.textContent = message;
            
            if (type === 'success') {
                uploadStatus.classList.add('success');
            } else if (type === 'error') {
                uploadStatus.classList.add('error');
            }

            // Auto-clear after specified time
            if (clearAfter > 0) {
                setTimeout(() => {
                    uploadStatus.innerHTML = '';
                    uploadStatus.className = '';
                }, clearAfter);
            }
        }
    }

    function validateForm() {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        let firstInvalidField = null;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
                // Add visual feedback
                field.style.borderColor = '#f44336';
            } else {
                // Remove error styling
                field.style.borderColor = '#444';
            }
        });

        // Check file input specifically
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput && fileInput.hasAttribute('required') && !fileInput.files.length) {
            isValid = false;
            if (!firstInvalidField) {
                firstInvalidField = fileInput;
            }
            fileInput.style.borderColor = '#f44336';
        }

        if (!isValid && firstInvalidField) {
            firstInvalidField.focus();
            showStatus('Por favor complete todos los campos requeridos', 'error', 5000);
        }

        return isValid;
    }

    function resetFormValidation() {
        const fields = form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            field.style.borderColor = '#444';
        });
    }

    function disableForm() {
        console.log('Disabling form elements...');
        const formElements = form.querySelectorAll('input, select, textarea, button');
        formElements.forEach(element => {
            element.disabled = true;
        });
        
        // Extra safety for submit button
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.style.opacity = '0.6';
            submitButton.style.cursor = 'not-allowed';
        }
    }

    function enableForm() {
        console.log('Enabling form elements...');
        const formElements = form.querySelectorAll('input, select, textarea, button');
        formElements.forEach(element => {
            element.disabled = false;
        });
        
        // Extra safety for submit button
        if (submitButton) {
            submitButton.disabled = false;
            submitButton.style.opacity = '1';
            submitButton.style.cursor = 'pointer';
        }
    }

    // Form submission handler
    if (form && submitButton) {
        console.log('Setting up form submission handler...');
        
        form.addEventListener('submit', function(e) {
            console.log('Form submit event triggered');
            e.preventDefault();

            // Prevent double submission
            if (isSubmitting) {
                console.log('Form submission already in progress, ignoring');
                return;
            }

            console.log('Starting form submission process...');

            // Reset previous validation
            resetFormValidation();

            // Validate form
            if (!validateForm()) {
                console.log('Form validation failed');
                return;
            }

            // Set submission flag
            isSubmitting = true;
            console.log('Set isSubmitting to true');

            // Show loading overlay
            showLoadingOverlay();

            // Disable form elements
            disableForm();

            // Clear previous status
            showStatus('');

            // Prepare form data
            const formData = new FormData(form);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            console.log('Submitting form data...');

            // Submit the form
            fetch(form.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => {
                console.log('Received response:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                hideLoadingOverlay();
                
                if (data.success) {
                    // Success handling
                    let message = data.message || 'Comprobante subido exitosamente.';
                    
                    // Check for warnings (like email issues)
                    if (data.warning) {
                        message += ` ${data.warning}`;
                    }
                    
                    showStatus(message, 'success');
                    
                    // Reset form after successful submission
                    form.reset();
                    resetFormValidation();
                    
                    // Optional: Redirect to dashboard after a delay
                    setTimeout(() => {
                        if (confirm('¿Desea ir al panel de control para ver el estado actualizado?')) {
                            window.location.href = '/dashboard/';
                        }
                    }, 3000);
                    
                } else {
                    // Error handling
                    showStatus('Error al subir el comprobante. Por favor, revise la información e inténtelo de nuevo.', 'error');
                    
                    if (data.errors) {
                        console.error('Form errors:', data.errors);
                        
                        // Clear previous error messages
                        const existingErrors = uploadStatus.querySelectorAll('.error-message');
                        existingErrors.forEach(error => error.remove());
                        
                        // Display field-specific errors
                        Object.keys(data.errors).forEach(key => {
                            const errorDiv = document.createElement('div');
                            errorDiv.className = 'error-message';
                            errorDiv.textContent = `${key}: ${data.errors[key].join(', ')}`;
                            uploadStatus.appendChild(errorDiv);
                            
                            // Highlight the problematic field
                            const field = form.querySelector(`[name="${key}"]`);
                            if (field) {
                                field.style.borderColor = '#f44336';
                                field.focus();
                            }
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Submission error:', error);
                hideLoadingOverlay();
                
                showStatus(
                    'Error de conexión. Por favor verifique su conexión a internet e inténtelo de nuevo.', 
                    'error'
                );
            })
            .finally(() => {
                console.log('Finalizing submission process...');
                // Re-enable form and reset submission flag
                enableForm();
                isSubmitting = false;
                console.log('Set isSubmitting to false');
            });
        });

        // Also handle direct button clicks (in case form submission doesn't trigger)
        submitButton.addEventListener('click', function(e) {
            console.log('Submit button clicked directly');
            if (!isSubmitting) {
                // Let the form submission handler take over
                return;
            } else {
                e.preventDefault();
                console.log('Blocked direct button click - submission in progress');
            }
        });

        // Add real-time validation
        const formFields = form.querySelectorAll('input, select, textarea');
        formFields.forEach(field => {
            field.addEventListener('input', function() {
                if (this.style.borderColor === 'rgb(244, 67, 54)') {
                    this.style.borderColor = '#444';
                }
            });

            field.addEventListener('change', function() {
                if (this.style.borderColor === 'rgb(244, 67, 54)') {
                    this.style.borderColor = '#444';
                }
            });
        });

        // File input specific handling
        const fileInput = form.querySelector('input[type="file"]');
        if (fileInput) {
            fileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    const file = this.files[0];
                    const maxSize = 10 * 1024 * 1024; // 10MB
                    
                    if (file.size > maxSize) {
                        showStatus('El archivo es demasiado grande. Máximo permitido: 10MB', 'error', 5000);
                        this.value = '';
                        this.style.borderColor = '#f44336';
                    } else {
                        this.style.borderColor = '#444';
                        showStatus('');
                    }
                }
            });
        }

        // Prevent page unload during submission
        window.addEventListener('beforeunload', function(e) {
            if (isSubmitting) {
                e.preventDefault();
                e.returnValue = 'Su pago se está procesando. ¿Está seguro de que desea salir de esta página?';
                return e.returnValue;
            }
        });

    } else {
        console.error('Required elements missing:');
        console.error('Form:', form);
        console.error('Submit button:', submitButton);
        console.error('Upload status:', uploadStatus);
        
        // Try to find elements with alternative selectors
        const altForm = document.querySelector('form');
        const altSubmitButton = document.querySelector('button[type="submit"], input[type="submit"]');
        const altUploadStatus = document.querySelector('#upload-status, .upload-status');
        
        console.log('Alternative elements found:');
        console.log('Alt form:', altForm);
        console.log('Alt submit button:', altSubmitButton);
        console.log('Alt upload status:', altUploadStatus);
        
        if (altForm && altSubmitButton) {
            console.log('Using alternative elements...');
            // Use alternative elements if main ones aren't found
            // Re-run the setup with alternative elements
            setupFormWithElements(altForm, altSubmitButton, altUploadStatus);
        }
    }

    // Separate function to set up form handling with any elements
    function setupFormWithElements(formEl, submitEl, statusEl) {
        console.log('Setting up form with provided elements...');
        
        formEl.addEventListener('submit', function(e) {
            console.log('Alternative form submit triggered');
            e.preventDefault();
            
            if (isSubmitting) {
                console.log('Already submitting, ignoring');
                return;
            }
            
            isSubmitting = true;
            console.log('Starting submission with alternative elements');
            
            // Disable submit button immediately
            if (submitEl) {
                submitEl.disabled = true;
                submitEl.textContent = 'Procesando...';
                submitEl.style.opacity = '0.6';
            }
            
            // Show loading overlay or fallback
            showLoadingOverlay();
            
            const formData = new FormData(formEl);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(formEl.action || window.location.href, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                hideLoadingOverlay();
                
                if (statusEl) {
                    if (data.success) {
                        statusEl.textContent = data.message || 'Comprobante subido exitosamente.';
                        statusEl.className = 'success';
                    } else {
                        statusEl.textContent = 'Error al subir el comprobante.';
                        statusEl.className = 'error';
                    }
                }
                
                if (data.success) {
                    setTimeout(() => {
                        if (confirm('¿Desea ir al panel de control?')) {
                            window.location.href = '/dashboard/';
                        }
                    }, 2000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                hideLoadingOverlay();
                if (statusEl) {
                    statusEl.textContent = 'Error de conexión.';
                    statusEl.className = 'error';
                }
            })
            .finally(() => {
                isSubmitting = false;
                if (submitEl) {
                    submitEl.disabled = false;
                    submitEl.textContent = 'Subir Comprobante';
                    submitEl.style.opacity = '1';
                }
            });
        });
    }

    // Add keyboard shortcut for form submission (Ctrl+Enter)
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !isSubmitting) {
            e.preventDefault();
            if (form && submitButton) {
                submitButton.click();
            }
        }
    });
});