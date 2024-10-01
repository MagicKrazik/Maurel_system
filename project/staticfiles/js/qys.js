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
            <td data-label="Tipo">${newQyS.type}</td>
            <td data-label="Categoría">${newQyS.category}</td>
            <td data-label="Apartamento">${newQyS.apartment_number}</td>
            <td data-label="Descripción">${newQyS.description}</td>
            <td data-label="Estado">${newQyS.status}</td>
            <td data-label="Fecha de Creación">${newQyS.created_at}</td>
            <td data-label="Fecha de Atención">-</td>
            ${newQyS.is_staff ? `
            <td data-label="Acciones">
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
                <button class="delete-btn" onclick="deleteQyS(${newQyS.id})">Eliminar</button>
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

    window.updateStatus = function(selectElement) {
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

    window.deleteQyS = function(qysId) {
        if (confirm('¿Está seguro de que desea eliminar esta queja o sugerencia?')) {
            const formData = new FormData();
            formData.append('qys_id', qysId);
            formData.append('delete_qys', '1');

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
                    const rowToDelete = document.querySelector(`tr[data-qys-id="${qysId}"]`);
                    if (rowToDelete) {
                        rowToDelete.remove();
                    }
                    if (qysTableBody.children.length === 0) {
                        const noQysRow = document.createElement('tr');
                        noQysRow.id = 'no-qys-row';
                        noQysRow.innerHTML = '<td colspan="8">No hay quejas o sugerencias registradas.</td>';
                        qysTableBody.appendChild(noQysRow);
                    }
                } else {
                    submissionStatus.textContent = 'Error al eliminar. Por favor, intente nuevamente.';
                    submissionStatus.className = 'submission-status error';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                submissionStatus.textContent = 'Error al eliminar. Por favor, intente nuevamente.';
                submissionStatus.className = 'submission-status error';
            });
        }
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