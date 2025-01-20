document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        // Here you would typically send the login data to your backend
        // For now, we'll just log it to the console
        console.log('Login attempt:', { username, password });

        // TODO: Add actual login logic here
        // This might involve sending a POST request to your backend
        // and handling the response (success, error messages, etc.)

        // Example of how you might handle a successful login:
        // if (loginSuccessful) {
        //     window.location.href = '/dashboard';
        // } else {
        //     // Show error message
        // }
    });
});