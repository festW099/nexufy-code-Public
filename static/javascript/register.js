// Валидация формы регистрации
document.getElementById('registrationForm').addEventListener('submit', function(e) {
    const agreementChecked = document.getElementById('agreement').checked;
    const agreementError = document.getElementById('agreementError');
    
    if (!agreementChecked) {
        e.preventDefault();
        agreementError.style.display = 'block';
    } else {
        agreementError.style.display = 'none';
    }
});

// Основные обработчики после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {
    const closeBtn = document.getElementById('closeBtn');
    const registrationForm = document.getElementById('registrationForm');
    const passwordInput = document.getElementById('password');
    const passwordError = document.getElementById('passwordError');
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
    
    // Валидация пароля
    passwordInput.addEventListener('input', function() {
        if (passwordInput.value.length < 8 && passwordInput.value.length > 0) {
            passwordError.style.display = 'block';
        } else {
            passwordError.style.display = 'none';
        }
    });
    
    // Обработка отправки формы
    registrationForm.addEventListener('submit', function(e) {
        if (passwordInput.value.length < 8) {
            e.preventDefault();
            passwordError.style.display = 'block';
            passwordInput.focus();
            
            // Анимация встряски при ошибке
            registrationForm.style.animation = 'shake 0.5s ease';
            setTimeout(() => {
                registrationForm.style.animation = '';
            }, 500);
        }
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