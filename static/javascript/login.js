
document.addEventListener('DOMContentLoaded', function() {
    const closeBtn = document.getElementById('closeBtn');
    const loginForm = document.getElementById('loginForm');
    const spotlight = document.getElementById('spotlight');
    const particlesContainer = document.getElementById('particles');
    
    // Эффект прожектора, следующий за курсором
    document.addEventListener('mousemove', (e) => {
        const x = e.clientX;
        const y = e.clientY;
        spotlight.style.setProperty('--x', `${x}px`);
        spotlight.style.setProperty('--y', `${y}px`);
    });
    
    // Создание частиц
    function createParticles() {
        const particleCount = 30;
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.classList.add('particle');
            
            // Случайные параметры
            const size = Math.random() * 5 + 1;
            const posX = Math.random() * window.innerWidth;
            const duration = Math.random() * 10 + 5;
            const delay = Math.random() * 5;
            
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.left = `${posX}px`;
            particle.style.bottom = `-10px`;
            particle.style.animationDuration = `${duration}s`;
            particle.style.animationDelay = `${delay}s`;
            
            particlesContainer.appendChild(particle);
        }
    }
    
    createParticles();
    
    // Обработчик кнопки закрытия
    closeBtn.addEventListener('click', function() {
        window.location.href = '/';
    });
    
    // Анимация при фокусе на полях ввода
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.querySelector('label').style.color = 'var(--gold)';
            this.parentElement.querySelector('label').style.transform = 'scale(1.05)';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.querySelector('label').style.color = '#aaa';
            this.parentElement.querySelector('label').style.transform = 'scale(1)';
        });
    });
});