document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('contactBtn').addEventListener('click', function() {
        window.open('https://t.me/oooohioooooo', '_blank');
    });

    // Инициализация AOS
    AOS.init({
        once: true
    });

    // Создаем звездный фон
    function createStars() {
        const starsContainer = document.getElementById('stars');
        const starsCount = 100;

        for (let i = 0; i < starsCount; i++) {
            const star = document.createElement('div');
            star.className = 'star';

            const size = Math.random() * 3;
            const posX = Math.random() * 100;
            const posY = Math.random() * 100;
            const duration = 2 + Math.random() * 5 + 's';
            const delay = Math.random() * 5 + 's';

            star.style.width = `${size}px`;
            star.style.height = `${size}px`;
            star.style.left = `${posX}%`;
            star.style.top = `${posY}%`;
            star.style.setProperty('--duration', duration);
            star.style.animationDelay = delay;

            starsContainer.appendChild(star);
        }
    }

    // Анимация кнопки с помощью GSAP
    function animateButton() {
        const btn = document.getElementById('contactBtn');

        btn.addEventListener('mouseenter', () => {
            gsap.to(btn, {
                scale: 1.05,
                duration: 0.3,
                ease: "power2.out"
            });
        });

        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, {
                scale: 1,
                duration: 0.3,
                ease: "power2.out"
            });
        });

        btn.addEventListener('click', () => {
            gsap.to(btn, {
                scale: 0.9,
                duration: 0.2,
                yoyo: true,
                repeat: 1,
                ease: "power2.inOut"
            });

            setTimeout(() => {
                alert("Система поддержки временно недоступна. Попробуйте позже.");
            }, 500);
        });
    }

    // Анимация кода ошибки с помощью Anime.js
    function animateErrorCode() {
        const errorCode = document.getElementById('errorCode');

        setInterval(() => {
            anime({
                targets: errorCode,
                scale: [1, 1.2, 1],
                duration: 1000,
                easing: 'easeInOutQuad'
            });

            anime({
                targets: errorCode,
                color: ['#FFD700', '#FF0000', '#FFD700'],
                duration: 1500,
                easing: 'easeInOutQuad'
            });
        }, 3000);
    }

    // Анимация мерцания границы контейнера
    function animateBorder() {
        const container = document.querySelector('.error-container');

        setInterval(() => {
            anime({
                targets: container,
                boxShadow: ['0 0 20px rgba(255, 215, 0, 0.3)', '0 0 30px rgba(255, 215, 0, 0.7)', '0 0 20px rgba(255, 215, 0, 0.3)'],
                duration: 2000,
                easing: 'easeInOutQuad'
            });
        }, 2500);
    }

    // Инициализация всех анимаций после загрузки страницы
    createStars();
    animateButton();
    animateErrorCode();
    animateBorder();

    anime({
        targets: '.warning-icon',
        rotate: [0, 10, -10, 0],
        duration: 1000,
        loop: true,
        easing: 'easeInOutSine'
    });

    const texts = document.querySelectorAll('p');
    texts.forEach((text, index) => {
        anime({
            targets: text,
            opacity: [0, 1],
            translateY: [20, 0],
            duration: 800,
            delay: 500 + index * 300,
            easing: 'easeOutExpo'
        });
    });
});