document.addEventListener('DOMContentLoaded', function() {
    // Announcements functionality
    function handleAnnouncementSubmit(form, action) {
        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        return fetch(form.action, {
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

    // Apartment fees functionality
    const apartmentForms = document.querySelectorAll('.apartment-form');
    apartmentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch(this.action, {
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
        const card = document.querySelector(`#apartment-${apartmentData.id}`);
        if (card) {
            card.querySelector('.total-value').textContent = `$${apartmentData.total_fee}`;
            card.querySelector('.pending-value').textContent = `$${apartmentData.remaining_amount}`;
            card.querySelector('.payment-status').innerHTML = apartmentData.is_paid ? 
                '<span class="status-active">Pagado</span>' : 
                '<span class="status-inactive">No pagado</span>';
            card.querySelector('.is-debtor input').checked = apartmentData.is_debtor;
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