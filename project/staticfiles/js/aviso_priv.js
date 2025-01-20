// aviso_priv.js

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Highlight current section in navigation (if you add a navigation menu)
    window.addEventListener('scroll', function() {
        let scrollPosition = window.scrollY;

        document.querySelectorAll('section').forEach(section => {
            if (scrollPosition >= section.offsetTop - 100 && 
                scrollPosition < (section.offsetTop + section.offsetHeight - 100)) {
                let id = section.getAttribute('id');
                document.querySelector(`nav a[href="#${id}"]`)?.classList.add('active');
            } else {
                let id = section.getAttribute('id');
                document.querySelector(`nav a[href="#${id}"]`)?.classList.remove('active');
            }
        });
    });

    // Add 'back to top' functionality
    const backToTopButton = document.createElement('button');
    backToTopButton.textContent = 'Back to Top';
    backToTopButton.classList.add('back-to-top');
    backToTopButton.style.display = 'none';
    document.body.appendChild(backToTopButton);

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });

    backToTopButton.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});