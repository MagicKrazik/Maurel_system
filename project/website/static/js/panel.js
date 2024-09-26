document.addEventListener('DOMContentLoaded', function() {
    // Announcement form submission
    const announcementForm = document.getElementById('announcement-form');
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

    // ... (rest of the existing JavaScript) ...
});