// panel.js

document.addEventListener('DOMContentLoaded', function() {
    // Announcement form submission
    const announcementForm = document.querySelector('.announcement-form');
    if (announcementForm) {
        announcementForm.addEventListener('submit', function(e) {
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
                    location.reload();
                } else {
                    alert('Error creating announcement: ' + JSON.stringify(data.errors));
                }
            });
        });
    }

    // Edit announcement
    const editButtons = document.querySelectorAll('.edit-announcement');
    editButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const announcementId = this.dataset.id;
            const form = document.querySelector(`#edit-form-${announcementId}`);
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        });
    });

    // Delete announcement
    const deleteButtons = document.querySelectorAll('.delete-announcement');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to delete this announcement?')) {
                const form = this.closest('form');
                form.submit();
            }
        });
    });

    // Update apartment fees
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
                    alert('Apartment fees updated successfully');
                    updateApartmentCard(data.apartment);
                } else {
                    alert('Error updating apartment fees: ' + JSON.stringify(data.errors));
                }
            });
        });
    });

    // Update apartment card with new data
    function updateApartmentCard(apartmentData) {
        const card = document.querySelector(`#apartment-${apartmentData.id}`);
        if (card) {
            card.querySelector('.total-value').textContent = `$${apartmentData.total_fee}`;
            card.querySelector('.pending-value').textContent = `$${apartmentData.remaining_amount}`;
            card.querySelector('.payment-status').innerHTML = apartmentData.is_paid ? '<span class="status-active">Pagado</span>' : '<span class="status-inactive">No pagado</span>';
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
            
            // Generate the report
            window.location.href = `/generate_monthly_balance_report/?year=${year}&month=${month}`;
        });

        // Set default values for month and year
        const currentDate = new Date();
        document.getElementById('report-month').value = currentDate.getMonth() + 1; // JavaScript months are 0-indexed
        document.getElementById('report-year').value = currentDate.getFullYear();
    }

    // Responsive design adjustments
    function handleResize() {
        const width = window.innerWidth;
        if (width <= 768) {
            // Adjustments for mobile view
            document.querySelectorAll('.apartment-card').forEach(card => {
                card.classList.add('mobile-view');
            });
        } else {
            // Reset for larger screens
            document.querySelectorAll('.apartment-card').forEach(card => {
                card.classList.remove('mobile-view');
            });
        }
    }

    // Initial call and event listener for resize
    handleResize();
    window.addEventListener('resize', handleResize);
});