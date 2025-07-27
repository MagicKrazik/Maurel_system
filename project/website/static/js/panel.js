document.addEventListener('DOMContentLoaded', function() {
    // Date filter functionality
    const dateFilterForm = document.getElementById('date-filter-form');
    const dateSelect = document.getElementById('date-select');
    
    if (dateFilterForm && dateSelect) {
        dateSelect.addEventListener('change', function() {
            dateFilterForm.submit();
        });
    }

    // FIXED: Helper function to get clean current date parameter
    function getCurrentDateParam() {
        const urlParams = new URLSearchParams(window.location.search);
        let currentDate = urlParams.get('date');
        
        // Clean the date parameter if it contains duplicates or invalid characters
        if (currentDate && currentDate.includes('?')) {
            currentDate = currentDate.split('?')[0];
        }
        
        // Validate the date format (YYYY-MM)
        if (currentDate && /^\d{4}-\d{2}$/.test(currentDate)) {
            return currentDate;
        }
        
        return null;
    }

    // FIXED: Helper function to build clean URLs
    function buildCleanURL(baseUrl, dateParam = null) {
        // Remove any existing query parameters from base URL
        const cleanBaseUrl = baseUrl.split('?')[0];
        
        if (dateParam) {
            return `${cleanBaseUrl}?date=${dateParam}`;
        }
        
        return cleanBaseUrl;
    }

    // NEW: Manual Payment Form Handler
    const manualPaymentForm = document.getElementById('manual-payment-form');
    const manualPaymentSubmit = document.getElementById('manual-payment-submit');
    const manualPaymentStatus = document.getElementById('manual-payment-status');

    if (manualPaymentForm && manualPaymentSubmit) {
        console.log('Setting up manual payment form handler...');
        
        manualPaymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Manual payment form submitted');
            
            // FIX: Enhanced button loading state
            manualPaymentSubmit.disabled = true;
            manualPaymentSubmit.innerHTML = '<span class="loading-spinner"></span>Procesando...';
            
            // Clear previous status
            manualPaymentStatus.style.display = 'none';
            manualPaymentStatus.className = 'status-container';
            
            // Prepare form data
            const formData = new FormData(manualPaymentForm);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Get current date parameter for URL building
            const currentDate = getCurrentDateParam();
            const requestUrl = buildCleanURL(manualPaymentForm.action || window.location.href, currentDate);
            
            fetch(requestUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('Manual payment response:', data);
                
                if (data.success) {
                    // Success handling
                    manualPaymentStatus.className = 'status-container success';
                    manualPaymentStatus.textContent = data.message;
                    manualPaymentStatus.style.display = 'block';
                    
                    // Show warning if emails failed
                    if (data.warning) {
                        manualPaymentStatus.textContent += ' ' + data.warning;
                    }
                    
                    // Reset form
                    manualPaymentForm.reset();
                    
                    // Optional: Reload page after delay to update apartment cards
                    setTimeout(() => {
                        if (confirm('¿Desea recargar la página para ver los cambios actualizados?')) {
                            window.location.reload();
                        }
                    }, 3000);
                    
                } else {
                    // Error handling
                    manualPaymentStatus.className = 'status-container error';
                    
                    if (data.errors) {
                        // Display field-specific errors
                        let errorMessage = 'Error en el formulario:\n';
                        Object.keys(data.errors).forEach(key => {
                            errorMessage += `• ${key}: ${data.errors[key].join(', ')}\n`;
                        });
                        manualPaymentStatus.textContent = errorMessage;
                    } else {
                        manualPaymentStatus.textContent = data.message || 'Error al procesar el pago manual.';
                    }
                    manualPaymentStatus.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Manual payment error:', error);
                manualPaymentStatus.className = 'status-container error';
                manualPaymentStatus.textContent = 'Error de conexión. Por favor, inténtelo de nuevo.';
                manualPaymentStatus.style.display = 'block';
            })
            .finally(() => {
                // Re-enable submit button
                manualPaymentSubmit.disabled = false;
                manualPaymentSubmit.innerHTML = 'Registrar Pago Manual';
            });
        });
        
        // Add real-time validation for manual payment form
        const manualPaymentFields = manualPaymentForm.querySelectorAll('input, select, textarea');
        manualPaymentFields.forEach(field => {
            field.addEventListener('input', function() {
                // Clear error styling on input
                if (this.style.borderColor === 'rgb(244, 67, 54)') {
                    this.style.borderColor = '#4a4a4a';
                }
            });
            
            field.addEventListener('change', function() {
                // Clear error styling on change
                if (this.style.borderColor === 'rgb(244, 67, 54)') {
                    this.style.borderColor = '#4a4a4a';
                }
            });
        });
        
        // File input specific handling for manual payment
        const manualFileInput = manualPaymentForm.querySelector('input[type="file"]');
        if (manualFileInput) {
            manualFileInput.addEventListener('change', function() {
                if (this.files.length > 0) {
                    const file = this.files[0];
                    const maxSize = 10 * 1024 * 1024; // 10MB
                    
                    if (file.size > maxSize) {
                        manualPaymentStatus.className = 'status-container error';
                        manualPaymentStatus.textContent = 'El archivo es demasiado grande. Máximo permitido: 10MB';
                        manualPaymentStatus.style.display = 'block';
                        this.value = '';
                        this.style.borderColor = '#f44336';
                    } else {
                        this.style.borderColor = '#4a4a4a';
                        manualPaymentStatus.style.display = 'none';
                    }
                }
            });
        }
    }

    // Cleanup functionality - EXISTING SECTION
    const cleanupForm = document.getElementById('cleanup-form');
    const previewBtn = document.getElementById('preview-btn');
    const resetBtn = document.getElementById('reset-btn');
    const deleteBtn = document.getElementById('delete-btn');
    const previewResults = document.getElementById('preview-results');
    const previewContent = document.getElementById('preview-content');
    const confirmResetBtn = document.getElementById('confirm-reset-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const cancelPreviewBtn = document.getElementById('cancel-preview-btn');

    let currentPreviewData = null;

    function showStatus(message, type = 'info') {
        const statusDiv = document.createElement('div');
        statusDiv.className = `status-message status-${type}`;
        statusDiv.textContent = message;
        
        // Remove any existing status messages
        const existingStatus = document.querySelector('.status-message');
        if (existingStatus) {
            existingStatus.remove();
        }
        
        // Insert status message
        cleanupForm.insertAdjacentElement('afterend', statusDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (statusDiv.parentNode) {
                statusDiv.remove();
            }
        }, 5000);
    }

    function getCleanupFormData() {
        const formData = new FormData(cleanupForm);
        formData.append('cleanup_action', 'preview'); // Default action
        return formData;
    }

    function submitCleanupRequest(action) {
        const formData = getCleanupFormData();
        formData.set('cleanup_action', action);
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // FIXED: Use clean URL building
        const currentDate = getCurrentDateParam();
        const requestUrl = buildCleanURL(window.location.href, currentDate);
        
        return fetch(requestUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .catch(error => {
            console.error('Error:', error);
            throw new Error('Error de conexión');
        });
    }

    function displayPreviewResults(data) {
        let html = '';
        
        if (data.monthly_fees_count > 0 || data.payment_reports_count > 0) {
            html += `<div class="preview-summary">
                Se procesarían: ${data.monthly_fees_count} cuotas mensuales y ${data.payment_reports_count} reportes de pago
            </div>`;
            
            if (data.monthly_fees && data.monthly_fees.length > 0) {
                html += '<h4>Cuotas Mensuales (primeras 10):</h4>';
                data.monthly_fees.forEach(fee => {
                    html += `<div class="preview-item">
                        <strong>${fee.username}</strong> - Apto ${fee.apartment} - 
                        ${fee.month} - Pagado: $${fee.paid_amount}
                    </div>`;
                });
                if (data.monthly_fees_count > 10) {
                    html += `<div class="preview-item">... y ${data.monthly_fees_count - 10} más</div>`;
                }
            }
            
            if (data.payment_reports && data.payment_reports.length > 0) {
                html += '<h4>Reportes de Pago (primeras 10):</h4>';
                data.payment_reports.forEach(report => {
                    html += `<div class="preview-item">
                        <strong>${report.username}</strong> - ${report.month} - 
                        $${report.amount} - ${report.date}
                    </div>`;
                });
                if (data.payment_reports_count > 10) {
                    html += `<div class="preview-item">... y ${data.payment_reports_count - 10} más</div>`;
                }
            }
        } else {
            html = '<div class="preview-summary">No se encontraron registros para procesar con los filtros seleccionados.</div>';
        }
        
        previewContent.innerHTML = html;
        previewResults.style.display = 'block';
        previewResults.scrollIntoView({ behavior: 'smooth' });
    }

    // Preview button click handler
    if (previewBtn) {
        previewBtn.addEventListener('click', function() {
            previewBtn.disabled = true;
            previewBtn.innerHTML = '<span class="loading-spinner"></span> Cargando...';
            
            submitCleanupRequest('preview')
                .then(data => {
                    if (data.success) {
                        currentPreviewData = data.preview;
                        displayPreviewResults(data.preview);
                    } else {
                        showStatus(data.message || 'Error al generar previsualización', 'error');
                    }
                })
                .catch(error => {
                    showStatus('Error al procesar la solicitud: ' + error.message, 'error');
                })
                .finally(() => {
                    previewBtn.disabled = false;
                    previewBtn.innerHTML = 'Previsualizar';
                });
        });
    }

    // Reset button click handler
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (confirm('¿Está seguro de que desea reiniciar el estado de pago? Esta acción cambiará el estado a "no pagado" pero mantendrá los registros.')) {
                resetBtn.disabled = true;
                resetBtn.innerHTML = '<span class="loading-spinner"></span> Procesando...';
                
                submitCleanupRequest('reset')
                    .then(data => {
                        if (data.success) {
                            showStatus(data.message, 'success');
                            // Reload page to update statistics
                            setTimeout(() => {
                                window.location.reload();
                            }, 2000);
                        } else {
                            showStatus(data.message || 'Error al reiniciar los datos', 'error');
                        }
                    })
                    .catch(error => {
                        showStatus('Error al procesar la solicitud: ' + error.message, 'error');
                    })
                    .finally(() => {
                        resetBtn.disabled = false;
                        resetBtn.innerHTML = 'Reiniciar Estado de Pago';
                    });
            }
        });
    }

    // Delete button click handler
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function() {
            if (confirm('¿Está seguro de que desea eliminar permanentemente estos registros? Esta acción NO se puede deshacer.')) {
                deleteBtn.disabled = true;
                deleteBtn.innerHTML = '<span class="loading-spinner"></span> Eliminando...';
                
                submitCleanupRequest('delete')
                    .then(data => {
                        if (data.success) {
                            showStatus(data.message, 'success');
                            // Reload page to update statistics
                            setTimeout(() => {
                                window.location.reload();
                            }, 2000);
                        } else {
                            showStatus(data.message || 'Error al eliminar los datos', 'error');
                        }
                    })
                    .catch(error => {
                        showStatus('Error al procesar la solicitud: ' + error.message, 'error');
                    })
                    .finally(() => {
                        deleteBtn.disabled = false;
                        deleteBtn.innerHTML = 'Eliminar Registros';
                    });
            }
        });
    }

    // Confirm reset button (from preview)
    if (confirmResetBtn) {
        confirmResetBtn.addEventListener('click', function() {
            if (confirm('¿Confirma que desea reiniciar el estado de pago de estos registros?')) {
                confirmResetBtn.disabled = true;
                confirmResetBtn.innerHTML = '<span class="loading-spinner"></span> Procesando...';
                
                submitCleanupRequest('reset')
                    .then(data => {
                        if (data.success) {
                            showStatus(data.message, 'success');
                            previewResults.style.display = 'none';
                            setTimeout(() => {
                                window.location.reload();
                            }, 2000);
                        } else {
                            showStatus(data.message || 'Error al reiniciar los datos', 'error');
                        }
                    })
                    .catch(error => {
                        showStatus('Error al procesar la solicitud: ' + error.message, 'error');
                    })
                    .finally(() => {
                        confirmResetBtn.disabled = false;
                        confirmResetBtn.innerHTML = 'Confirmar Reinicio';
                    });
            }
        });
    }

    // Confirm delete button (from preview)
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            if (confirm('¿Confirma que desea eliminar permanentemente estos registros?')) {
                confirmDeleteBtn.disabled = true;
                confirmDeleteBtn.innerHTML = '<span class="loading-spinner"></span> Eliminando...';
                
                submitCleanupRequest('delete')
                    .then(data => {
                        if (data.success) {
                            showStatus(data.message, 'success');
                            previewResults.style.display = 'none';
                            setTimeout(() => {
                                window.location.reload();
                            }, 2000);
                        } else {
                            showStatus(data.message || 'Error al eliminar los datos', 'error');
                        }
                    })
                    .catch(error => {
                        showStatus('Error al procesar la solicitud: ' + error.message, 'error');
                    })
                    .finally(() => {
                        confirmDeleteBtn.disabled = false;
                        confirmDeleteBtn.innerHTML = 'Confirmar Eliminación';
                    });
            }
        });
    }

    // Cancel preview button
    if (cancelPreviewBtn) {
        cancelPreviewBtn.addEventListener('click', function() {
            previewResults.style.display = 'none';
            currentPreviewData = null;
        });
    }

    // FIXED: Announcements functionality with clean URL handling
    function handleAnnouncementSubmit(form, action) {
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // FIXED: Use clean URL building
        const currentDate = getCurrentDateParam();
        const requestUrl = buildCleanURL(form.action, currentDate);

        return fetch(requestUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.text())
        .then(text => {
            try {
                return JSON.parse(text);
            } catch (e) {
                console.error('Server response:', text);
                throw new Error('Invalid JSON response');
            }
        });
    }

    // Create Announcement Handler
    const createAnnouncementForm = document.querySelector('form[name="create_announcement"]');
    if (createAnnouncementForm) {
        createAnnouncementForm.addEventListener('submit', function(e) {
            e.preventDefault();
            handleAnnouncementSubmit(this, 'create')
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Error al crear el anuncio: ' + JSON.stringify(data.errors));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al procesar la solicitud');
                });
        });
    }

    // Edit Announcement Handlers
    document.querySelectorAll('form[name="edit_announcement"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            handleAnnouncementSubmit(this, 'edit')
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert('Error al actualizar el anuncio: ' + JSON.stringify(data.errors));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Error al procesar la solicitud');
                });
        });
    });

    // Delete Announcement Handlers
    document.querySelectorAll('form[name="delete_announcement"]').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            if (confirm('¿Está seguro de que desea eliminar este anuncio?')) {
                handleAnnouncementSubmit(this, 'delete')
                    .then(data => {
                        if (data.success) {
                            window.location.reload();
                        } else {
                            alert('Error al eliminar el anuncio');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Error al procesar la solicitud');
                    });
            }
        });
    });

    // Toggle edit form visibility
    document.querySelectorAll('.edit-announcement').forEach(button => {
        button.addEventListener('click', function() {
            const announcementId = this.getAttribute('data-id');
            const form = document.getElementById(`edit-form-${announcementId}`);
            if (form) {
                form.style.display = form.style.display === 'none' ? 'block' : 'none';
            }
        });
    });

    // FIXED: Apartment fees functionality with proper URL handling
    const apartmentForms = document.querySelectorAll('.apartment-card form');
    apartmentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            // FIXED: Get clean date parameter and build proper URL
            const currentDate = getCurrentDateParam();
            const requestUrl = buildCleanURL(this.action, currentDate);
            
            fetch(requestUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Datos actualizados exitosamente');
                    updateApartmentCard(data.apartment);
                } else {
                    alert('Error al actualizar: ' + JSON.stringify(data.errors));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al procesar la solicitud');
            });
        });
    });

    function updateApartmentCard(apartmentData) {
        const card = document.querySelector(`[data-apartment-id="${apartmentData.id}"]`);
        if (card) {
            const totalValue = card.querySelector('.total-value');
            const pendingValue = card.querySelector('.pending-value');
            const paymentStatus = card.querySelector('.payment-status input[type="checkbox"]');
            const debtorStatus = card.querySelector('.is-debtor input[type="checkbox"]');
            
            if (totalValue) totalValue.textContent = apartmentData.total_fee;
            if (pendingValue) pendingValue.textContent = apartmentData.remaining_amount;
            if (paymentStatus) paymentStatus.checked = apartmentData.is_paid;
            if (debtorStatus) debtorStatus.checked = apartmentData.is_debtor;
        }
    }

    // Monthly Balance Report
    const balanceReportForm = document.getElementById('balance-report-form');
    if (balanceReportForm) {
        balanceReportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const month = document.getElementById('report-month').value;
            const year = document.getElementById('report-year').value;
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            const formData = new FormData();
            formData.append('year', year);
            formData.append('month', month);
            formData.append('csrfmiddlewaretoken', csrftoken);

            fetch('/generate_monthly_balance_report/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                }
                throw new Error('Network response was not ok');
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `balance_mensual_${year}_${month}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al generar el reporte. Por favor, inténtelo de nuevo.');
            });
        });

        const currentDate = new Date();
        document.getElementById('report-month').value = currentDate.getMonth() + 1;
        document.getElementById('report-year').value = currentDate.getFullYear();
    }

    // Real-time calculation for apartment fees
    document.querySelectorAll('.apartment-card').forEach(card => {
        const feeInputs = card.querySelectorAll('.fee-input');
        const totalValue = card.querySelector('.total-value');
        const paidAmountInput = card.querySelector('.paid-amount-input');
        const pendingValue = card.querySelector('.pending-value');

        function updateTotals() {
            let total = 0;
            feeInputs.forEach(input => {
                if (!input.classList.contains('paid-amount-input')) {
                    total += parseFloat(input.value) || 0;
                }
            });
            
            if (totalValue) {
                totalValue.textContent = total.toFixed(2);
            }
            
            const paidAmount = parseFloat(paidAmountInput.value) || 0;
            const pending = total - paidAmount;
            
            if (pendingValue) {
                pendingValue.textContent = pending.toFixed(2);
            }
        }

        feeInputs.forEach(input => {
            input.addEventListener('input', updateTotals);
        });
        
        if (paidAmountInput) {
            paidAmountInput.addEventListener('input', updateTotals);
        }
    });

    // Responsive design
    function handleResize() {
        const width = window.innerWidth;
        if (width <= 768) {
            document.querySelectorAll('.apartment-card').forEach(card => {
                card.classList.add('mobile-view');
            });
        } else {
            document.querySelectorAll('.apartment-card').forEach(card => {
                card.classList.remove('mobile-view');
            });
        }
    }

    handleResize();
    window.addEventListener('resize', handleResize);
});