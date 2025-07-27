document.addEventListener('DOMContentLoaded', function() {
    const dateFilter = document.getElementById('date-filter');
    
    // Process payment document titles to distinguish manual payments
    function processPaymentDocuments() {
        const paymentTitles = document.querySelectorAll('#pagos_mantenimiento .document-title[data-title]');
        
        paymentTitles.forEach(titleElement => {
            const fullTitle = titleElement.getAttribute('data-title');
            const uploader = titleElement.getAttribute('data-uploader');
            const date = titleElement.getAttribute('data-date');
            
            // Parse the title to determine if it's a manual payment
            // Expected formats:
            // Regular payment: "Pago de Mantenimiento - username - Month Year"
            // Manual payment: "username - dd/mm/yyyy - admin_name"
            
            let displayText = '';
            let isManualPayment = false;
            
            if (fullTitle.includes('Pago de Mantenimiento')) {
                // Regular user payment
                const titleParts = fullTitle.split(' - ');
                if (titleParts.length >= 2) {
                    const username = titleParts[1].trim();
                    displayText = `${username} - ${date}`;
                    isManualPayment = false;
                }
            } else {
                // Check if it's a manual payment (format: "username - date - admin_name")
                const titleParts = fullTitle.split(' - ');
                if (titleParts.length >= 3) {
                    // This is likely a manual payment
                    const username = titleParts[0].trim();
                    const adminName = titleParts[2].trim();
                    displayText = `${username} - ${date} - ${adminName}`;
                    isManualPayment = true;
                } else if (titleParts.length === 2) {
                    // Check if uploader is different from the username in title
                    const titleUsername = titleParts[0].trim();
                    if (uploader !== titleUsername) {
                        // This is a manual payment
                        displayText = `${titleUsername} - ${date} - ${uploader}`;
                        isManualPayment = true;
                    } else {
                        // Regular payment with different format
                        displayText = `${titleUsername} - ${date}`;
                        isManualPayment = false;
                    }
                } else {
                    // Fallback to simple format
                    displayText = `${uploader} - ${date}`;
                    isManualPayment = false;
                }
            }
            
            // Update the display text
            titleElement.textContent = displayText;
            
            // Add visual indicator for manual payments
            if (isManualPayment) {
                titleElement.classList.add('manual-payment');
                // Don't add JavaScript indicator since CSS ::after will handle it
            } else {
                titleElement.classList.remove('manual-payment');
                // Don't add indicators for regular payments either to keep it clean
            }
        });
    }
    
    // Advanced title parsing for different manual payment formats
    function parsePaymentTitle(title, uploader, date) {
        // Pattern 1: "Pago de Mantenimiento - username - Month Year"
        if (title.includes('Pago de Mantenimiento')) {
            const parts = title.split(' - ');
            if (parts.length >= 2) {
                return {
                    username: parts[1].trim(),
                    isManual: false,
                    adminName: null
                };
            }
        }
        
        // Pattern 2: "username - dd/mm/yyyy - admin_name" (manual payment)
        const dashParts = title.split(' - ');
        if (dashParts.length >= 3) {
            return {
                username: dashParts[0].trim(),
                isManual: true,
                adminName: dashParts[2].trim()
            };
        }
        
        // Pattern 3: "username - dd/mm/yyyy" (check if uploader is different)
        if (dashParts.length === 2) {
            const titleUsername = dashParts[0].trim();
            if (uploader !== titleUsername) {
                return {
                    username: titleUsername,
                    isManual: true,
                    adminName: uploader
                };
            }
        }
        
        // Fallback: assume it's a regular payment
        return {
            username: uploader,
            isManual: false,
            adminName: null
        };
    }
    
    // Enhanced processing function
    function enhancedProcessPaymentDocuments() {
        const paymentTitles = document.querySelectorAll('#pagos_mantenimiento .document-title[data-title]');
        
        paymentTitles.forEach(titleElement => {
            const fullTitle = titleElement.getAttribute('data-title');
            const uploader = titleElement.getAttribute('data-uploader');
            const date = titleElement.getAttribute('data-date');
            
            const parsed = parsePaymentTitle(fullTitle, uploader, date);
            
            let displayText = '';
            if (parsed.isManual) {
                displayText = `${parsed.username} - ${date} - ${parsed.adminName}`;
                titleElement.classList.add('manual-payment');
            } else {
                displayText = `${parsed.username} - ${date}`;
                titleElement.classList.remove('manual-payment');
            }
            
            // Update the display text
            titleElement.textContent = displayText;
        });
    }
    
    // Filter functionality
    if (dateFilter) {
        dateFilter.addEventListener('change', function() {
            window.location.href = `?date=${this.value}`;
        });

        dateFilter.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                window.location.href = `?date=${this.value}`;
            }
        });
    }

    // Process payment documents on page load
    enhancedProcessPaymentDocuments();

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // Document item hover effects
    document.querySelectorAll('.document-item').forEach(item => {
        item.addEventListener('mouseenter', function() {
            if (!window.matchMedia('(hover: none)').matches) {
                this.style.transform = 'translateY(-2px)';
            }
        });
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Delete document functionality
    window.deleteDocument = function(documentId) {
        if (confirm('¿Está seguro que desea eliminar este documento?')) {
            fetch(`/delete_document/${documentId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    const documentItem = document.querySelector(`.document-item[data-document-id="${documentId}"]`);
                    if (documentItem) {
                        documentItem.remove();
                    } else {
                        location.reload();
                    }
                } else {
                    throw new Error(data.message || 'Error al eliminar el documento');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert(error.message || 'Error al eliminar el documento');
            });
        }
    };

    // Lazy loading
    const observer = new IntersectionObserver(
        (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        }
    );

    document.querySelectorAll('.document-section').forEach(section => {
        observer.observe(section);
    });

    // Touch device optimizations
    if (window.matchMedia('(hover: none)').matches) {
        document.querySelectorAll('.delete-document-btn').forEach(btn => {
            btn.style.opacity = '1';
        });
    }

    // Debug function to help identify payment types
    function debugPaymentDocuments() {
        const paymentTitles = document.querySelectorAll('#pagos_mantenimiento .document-title[data-title]');
        console.log('=== Payment Documents Debug ===');
        paymentTitles.forEach((titleElement, index) => {
            const fullTitle = titleElement.getAttribute('data-title');
            const uploader = titleElement.getAttribute('data-uploader');
            const date = titleElement.getAttribute('data-date');
            
            console.log(`Document ${index + 1}:`);
            console.log(`  Title: "${fullTitle}"`);
            console.log(`  Uploader: "${uploader}"`);
            console.log(`  Date: "${date}"`);
            console.log(`  Display: "${titleElement.textContent}"`);
            console.log(`  Is Manual: ${titleElement.classList.contains('manual-payment')}`);
            console.log('---');
        });
    }

    // Uncomment the next line for debugging
    // debugPaymentDocuments();
});