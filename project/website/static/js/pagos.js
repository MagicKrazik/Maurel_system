document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');
    const uploadStatus = document.getElementById('upload-status');

    if (form && submitButton && uploadStatus) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitButton.disabled = true;
            uploadStatus.textContent = 'Subiendo comprobante...';

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    uploadStatus.textContent = data.message || 'Comprobante subido exitosamente.';
                    // Optionally redirect to dashboard or clear form
                    // window.location.href = '/dashboard/';
                } else {
                    uploadStatus.textContent = 'Error al subir el comprobante. Por favor, inténtelo de nuevo.';
                    if (data.errors) {
                        console.error('Form errors:', data.errors);
                        // Display errors to the user
                        Object.keys(data.errors).forEach(key => {
                            const errorElement = document.createElement('p');
                            errorElement.textContent = `${key}: ${data.errors[key].join(', ')}`;
                            errorElement.className = 'error-message';
                            uploadStatus.appendChild(errorElement);
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                uploadStatus.textContent = 'Error al subir el comprobante. Por favor, inténtelo de nuevo.';
            })
            .finally(() => {
                submitButton.disabled = false;
            });
        });
    } else {
        console.error('One or more required elements are missing from the page.');
    }
});