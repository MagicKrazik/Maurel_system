// Enhanced qys.js - Works with existing backend, provides better UX
document.addEventListener('DOMContentLoaded', function() {
    // Check if enhanced form handler is available
    if (typeof EnhancedFormHandler !== 'undefined') {
        console.log('Enhanced form handler loaded for QYS');
        // Enhanced handler will manage form submission
        setupQYSSpecificFeatures();
        return;
    }

    // Fallback functionality with enhancements
    setupLegacyQYSHandler();
    setupQYSSpecificFeatures();
});

function setupQYSSpecificFeatures() {
    // Set up status update handlers that work with existing backend
    setupStatusUpdateHandlers();
    setupDeleteHandlers();
}

function setupLegacyQYSHandler() {
    const form = document.getElementById('qys-form');
    const submissionStatus = document.getElementById('submission-status') || document.getElementById('upload-status');
    
    if (!form) return;

    let isSubmitting = false;

    const loadingSteps = [
        'Validando información del reporte...',
        'Guardando comunicación en el sistema...',
        'Generando reporte PDF...',
        'Enviando notificaciones a administradores...',
        'Finalizando proceso...'
    ];

    function showEnhancedQYSLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('loading-hidden');
            document.body.style.overflow = 'hidden';
            
            const titleElement = overlay.querySelector('.loading-text h3');
            if (titleElement) {
                titleElement.textContent = 'Procesando Comunicación';
            }
            
            // Start step progression
            let currentStep = 0;
            const updateStep = () => {
                const stepElement = document.querySelector('.loading-step');
                if (stepElement && loadingSteps[currentStep]) {
                    stepElement.textContent = loadingSteps[currentStep];
                }
            };
            
            updateStep();
            const stepInterval = setInterval(() => {
                currentStep = (currentStep + 1) % loadingSteps.length;
                updateStep();
            }, 2000);
            
            // Store interval for cleanup
            overlay._qysStepInterval = stepInterval;
        }
    }

    function hideEnhancedQYSLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('loading-hidden');
            document.body.style.overflow = '';
            
            if (overlay._qysStepInterval) {
                clearInterval(overlay._qysStepInterval);
                overlay._qysStepInterval = null;
            }
        }
    }

    function showQYSStatus(message, type = 'info') {
        if (submissionStatus) {
            submissionStatus.className = `message-container ${type}`;
            submissionStatus.textContent = message;
        }
    }

    function showQYSSuccessNotification(message, warning = null) {
        const notification = document.createElement('div');
        notification.className = 'completion-notification';
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '10001';
        
        notification.innerHTML = `
            <div class="notification-header">
                <span class="notification-icon">📝</span>
                <span class="notification-title">Comunicación Registrada</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="notification-body">
                <div class="notification-message">${message}</div>
                ${warning ? `<div class="notification-warning">${warning}</div>` : ''}
                <div class="notification-details">
                    <span class="status-item">✅ Reporte guardado</span>
                    <span class="status-item">✅ PDF generado</span>
                    <span class="status-item">✅ Notificaciones enviadas</span>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in forwards';
            setTimeout(() => notification.remove(), 300);
        }, 12000);
    }

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (isSubmitting) return;
        
        isSubmitting = true;
        showEnhancedQYSLoading();
        
        const formData = new FormData(form);
        formData.append('submit_qys', '1'); // Required flag for existing backend
        
        fetch('/qys/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            hideEnhancedQYSLoading();
            
            if (data.success) {
                let message = data.message || 'Su comunicación ha sido registrada exitosamente.';
                let warning = data.warning || null;
                
                showQYSStatus(message, 'success');
                showQYSSuccessNotification(message, warning);
                
                form.reset();
                
                // Update QYS table if new record is provided
                if (data.new_qys) {
                    updateQySTable(data.new_qys);
                }
            } else {
                showQYSStatus('Error al enviar. Por favor, intente nuevamente.', 'error');
            }
        })
        .catch(error => {
            console.error('QYS submission error:', error);
            hideEnhancedQYSLoading();
            showQYSStatus('Error de conexión. Por favor, intente nuevamente.', 'error');
        })
        .finally(() => {
            isSubmitting = false;
        });
    });
}

function setupStatusUpdateHandlers() {
    // Handle status updates with enhanced UX
    document.addEventListener('change', function(e) {
        if (e.target.name === 'status' && e.target.closest('.status-update-form')) {
            const form = e.target.closest('form');
            const formData = new FormData(form);
            
            // Show loading state
            const selectElement = e.target;
            const originalBg = selectElement.style.backgroundColor;
            selectElement.style.backgroundColor = 'rgba(74, 144, 226, 0.2)';
            selectElement.disabled = true;
            
            fetch('/qys/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Show mini success notification
                    showMiniNotification('Estado actualizado exitosamente', 'success');
                } else {
                    showMiniNotification('Error al actualizar el estado', 'error');
                    // Revert selection on error
                    selectElement.selectedIndex = 0;
                }
            })
            .catch(error => {
                console.error('Status update error:', error);
                showMiniNotification('Error de conexión', 'error');
                selectElement.selectedIndex = 0;
            })
            .finally(() => {
                selectElement.style.backgroundColor = originalBg;
                selectElement.disabled = false;
            });
        }
    });
}

function setupDeleteHandlers() {
    // Enhanced delete confirmation
    window.deleteQyS = function(qysId) {
        // Create custom confirmation modal
        const modal = document.createElement('div');
        modal.className = 'delete-confirmation-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10002;
        `;
        
        modal.innerHTML = `
            <div style="background: #2A2B2A; padding: 30px; border-radius: 10px; border: 2px solid #f44336; max-width: 400px; text-align: center;">
                <h3 style="color: #ffffff; margin-bottom: 15px;">⚠️ Confirmar Eliminación</h3>
                <p style="color: #cccccc; margin-bottom: 25px;">¿Está seguro de que desea eliminar esta queja/sugerencia? Esta acción no se puede deshacer.</p>
                <div style="display: flex; gap: 15px; justify-content: center;">
                    <button onclick="this.closest('.delete-confirmation-modal').remove()" 
                            style="padding: 10px 20px; background: #666; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        Cancelar
                    </button>
                    <button onclick="confirmDeleteQyS(${qysId}); this.closest('.delete-confirmation-modal').remove()" 
                            style="padding: 10px 20px; background: #f44336; color: white; border: none; border-radius: 5px; cursor: pointer;">
                        Eliminar
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    };
    
    window.confirmDeleteQyS = function(qysId) {
        const formData = new FormData();
        formData.append('qys_id', qysId);
        formData.append('delete_qys', '1');
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

        fetch('/qys/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMiniNotification('Comunicación eliminada exitosamente', 'success');
                // Remove the record card
                const recordCard = document.querySelector(`[data-qys-id="${qysId}"]`);
                if (recordCard) {
                    recordCard.style.animation = 'fadeOut 0.3s ease-out forwards';
                    setTimeout(() => recordCard.remove(), 300);
                }
            } else {
                showMiniNotification('Error al eliminar', 'error');
            }
        })
        .catch(error => {
            console.error('Delete error:', error);
            showMiniNotification('Error de conexión', 'error');
        });
    };
}

function updateQySTable(newQyS) {
    const recordsContainer = document.querySelector('.records-container');
    if (!recordsContainer) return;

    // Remove "no records" message if it exists
    const noRecords = recordsContainer.querySelector('.no-records');
    if (noRecords) {
        noRecords.remove();
    }

    // Create new record card
    const recordCard = document.createElement('div');
    recordCard.className = 'record-card';
    recordCard.style.animation = 'fadeInUp 0.5s ease-out';
    recordCard.setAttribute('data-qys-id', newQyS.id);
    
    recordCard.innerHTML = `
        <div class="record-header">
            <div class="record-type">
                <span class="type-badge type-${newQyS.type.toLowerCase()}">${newQyS.type}</span>
                <span class="category-badge">${newQyS.category}</span>
            </div>
            <div class="record-apartment">
                <span class="apartment-label">Depto</span>
                <span class="apartment-number">${newQyS.apartment_number}</span>
            </div>
        </div>
        <div class="record-body">
            <div class="record-description">
                <p>${newQyS.description}</p>
            </div>
            <div class="record-meta">
                <div class="meta-item">
                    <span class="meta-label">Estado:</span>
                    <span class="status-badge status-${newQyS.status.toLowerCase()}">${newQyS.status}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">Creado:</span>
                    <span class="meta-value">${newQyS.created_at}</span>
                </div>
            </div>
        </div>
    `;
    
    recordsContainer.insertBefore(recordCard, recordsContainer.firstChild);
}

function showMiniNotification(message, type) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : '#f44336'};
        color: white;
        padding: 12px 20px;
        border-radius: 5px;
        z-index: 10000;
        font-size: 14px;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function getCookie(name) {
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

// Add fadeOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(0.95); }
    }
`;
document.head.appendChild(style);