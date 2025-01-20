// initial_profile_update.js

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('profile-update-form');
    const inputs = form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');

    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 5px #1896d1';
        });

        input.addEventListener('blur', function() {
            this.style.boxShadow = 'none';
        });
    });

    form.addEventListener('submit', function(e) {
        let isValid = true;
        inputs.forEach(input => {
            if (!input.value.trim()) {
                isValid = false;
                input.style.borderColor = '#ff6b6b';
            } else {
                input.style.borderColor = '#333';
            }
        });

        if (!isValid) {
            e.preventDefault();
            alert('Por favor, complete todos los campos requeridos.');
        }
    });
});