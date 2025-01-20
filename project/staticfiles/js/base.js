document.addEventListener('DOMContentLoaded', function() {
    const navbarToggle = document.querySelector('.navbar-toggle');
    const navbarMenu = document.querySelector('.navbar-menu');
    const navLinks = document.querySelectorAll('.navbar-link');
    const dropdowns = document.querySelectorAll('.navbar-dropdown');

    // Toggle mobile menu
    navbarToggle.addEventListener('click', toggleMobileMenu);

    // Close menu when clicking on a nav link
    navLinks.forEach(link => link.addEventListener('click', closeMenu));

    // Toggle dropdowns on mobile
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('click', function(e) {
            if (window.innerWidth < 960) {
                e.preventDefault();
                this.classList.toggle('active');
            }
        });
    });

    function toggleMobileMenu() {
        navbarToggle.classList.toggle('active');
        navbarMenu.classList.toggle('active');
        
        // Toggle between hamburger and X icon
        navbarToggle.innerHTML = navbarToggle.classList.contains('active') 
            ? '<span class="bar"></span><span class="bar"></span><span class="bar"></span>'
            : '<span class="bar"></span><span class="bar"></span><span class="bar"></span>';
    }

    function closeMenu() {
        navbarToggle.classList.remove('active');
        navbarMenu.classList.remove('active');
        
        // Reset to hamburger icon
        navbarToggle.innerHTML = '<span class="bar"></span><span class="bar"></span><span class="bar"></span>';
    }
});