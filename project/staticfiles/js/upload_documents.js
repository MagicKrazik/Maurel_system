document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const fileInput = document.querySelector('input[type="file"]');
    const submitButton = document.querySelector('.btn-primary');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        if (validateForm()) {
            this.submit();
        }
    });

    fileInput.addEventListener('change', function() {
        const fileName = this.files[0].name;
        const fileSize = this.files[0].size;
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (fileSize > maxSize) {
            alert('El archivo es demasiado grande. El tamaño máximo permitido es 5MB.');
            this.value = '';
        } else {
            this.nextElementSibling.textContent = `Archivo seleccionado: ${fileName}`;
        }
    });

    function validateForm() {
        let isValid = true;
        const requiredFields = form.querySelectorAll('input[required], select[required], textarea[required]');

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('error');
                const errorMessage = document.createElement('span');
                errorMessage.classList.add('error-message');
                errorMessage.textContent = 'Este campo es obligatorio';
                field.parentNode.appendChild(errorMessage);
            } else {
                field.classList.remove('error');
                const existingError = field.parentNode.querySelector('.error-message');
                if (existingError) {
                    existingError.remove();
                }
            }
        });

        return isValid;
    }

    // Add visual feedback when form is being submitted
    submitButton.addEventListener('click', function() {
        if (validateForm()) {
            this.textContent = 'Subiendo...';
            this.disabled = true;
            this.style.opacity = '0.7';
        }
    });
});