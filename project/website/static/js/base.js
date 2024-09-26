document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const navbarDropdown = document.querySelector('.navbar-dropdown');

    navbarToggle.addEventListener('click', function() {
        navbarMenu.classList.toggle('active');
        navbarToggle.classList.toggle('active');
    });

    dropdownToggle.addEventListener('click', function(e) {
        e.preventDefault();
        navbarDropdown.classList.toggle('active');
    });
});