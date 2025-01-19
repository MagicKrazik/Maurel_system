document.addEventListener('DOMContentLoaded', function() {
    const dateFilter = document.getElementById('date-filter');
    
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
});