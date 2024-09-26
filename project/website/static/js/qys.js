document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('qys-form');
    const submissionStatus = document.getElementById('submission-status');
    const qysTableBody = document.getElementById('qys-table-body');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        submitQyS();
    });

    function submitQyS() {
        const formData = new FormData(form);
        formData.append('submit_qys', '1');

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
                submissionStatus.textContent = data.message;
                submissionStatus.className = 'submission-status success';
                form.reset();
                updateQySTable(data.new_qys);
            } else {
                submissionStatus.textContent = 'Error al enviar. Por favor, intente nuevamente.';
                submissionStatus.className = 'submission-status error';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            submissionStatus.textContent = 'Error al enviar. Por favor, intente nuevamente.';
            submissionStatus.className = 'submission-status error';
        });
    }

    function updateQySTable(newQyS) {
        const noQysRow = document.getElementById('no-qys-row');
        if (noQysRow) {
            noQysRow.remove();
        }

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${newQyS.type}</td>
            <td>${newQyS.category}</td>
            <td>${newQyS.apartment_number}</td>
            <td>${newQyS.description}</td>
            <td>${newQyS.status}</td>
            <td>${newQyS.created_at}</td>
            ${newQyS.is_staff ? `
            <td>
                <form method="post" action="/qys/">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                    <input type="hidden" name="qys_id" value="${newQyS.id}">
                    <select name="status" onchange="updateStatus(this)">
                        ${newQyS.status_choices.map(([value, label]) => 
                            `<option value="${value}" ${newQyS.status === value ? 'selected' : ''}>${label}</option>`
                        ).join('')}
                    </select>
                    <input type="hidden" name="update_status" value="1">
                </form>
            </td>
            ` : ''}
        `;
        qysTableBody.insertBefore(row, qysTableBody.firstChild);
    }

    // Add event delegation for status update
    qysTableBody.addEventListener('change', function(e) {
        if (e.target.name === 'status') {
            updateStatus(e.target);
        }
    });

    function updateStatus(selectElement) {
        const form = selectElement.closest('form');
        const formData = new FormData(form);

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
                submissionStatus.textContent = data.message;
                submissionStatus.className = 'submission-status success';
            } else {
                submissionStatus.textContent = 'Error al actualizar el estado. Por favor, intente nuevamente.';
                submissionStatus.className = 'submission-status error';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            submissionStatus.textContent = 'Error al actualizar el estado. Por favor, intente nuevamente.';
            submissionStatus.className = 'submission-status error';
        });
    }

    // Helper function to get CSRF token
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
});