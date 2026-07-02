document.addEventListener('DOMContentLoaded', function() {

    // ---------- MOBILE MENU ----------
    const menuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            const icon = this.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-times');
            }
        });
    }

    // ---------- NAVBAR SHRINK ----------
    const header = document.getElementById('main-header');
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 80) {
            header.classList.add('navbar-shrink');
        } else {
            header.classList.remove('navbar-shrink');
        }
    });

    // ---------- SCROLL ANIMATIONS ----------
    const animated = document.querySelectorAll('.fade-in-up, .fade-in-up-delay-1, .fade-in-up-delay-2, .fade-in-up-delay-3, .fade-in-up-delay-4');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        animated.forEach(el => {
            el.style.animationPlayState = 'paused';
            observer.observe(el);
        });
    } else {
        animated.forEach(el => el.style.animationPlayState = 'running');
    }

    console.log('✅ main.js loaded');
});