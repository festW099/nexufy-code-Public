// script.js

// Создаем эффект случайных пикселей
function createPixels() {
    const container = document.getElementById('pixels-container');
    const pixelCount = 100;
    
    for (let i = 0; i < pixelCount; i++) {
        const pixel = document.createElement('div');
        pixel.classList.add('pixel');
        
        // Случайная позиция
        pixel.style.left = `${Math.random() * 100}%`;
        pixel.style.top = `${Math.random() * 100}%`;
        
        // Случайная задержка анимации
        pixel.style.animationDelay = `${Math.random() * 5}s`;
        
        container.appendChild(pixel);
        
        // Анимация появления/исчезновения
        gsap.to(pixel, {
            opacity: Math.random() * 0.5,
            duration: 0.1,
            repeat: -1,
            yoyo: true,
            delay: Math.random() * 3,
            ease: "power1.inOut"
        });
        
        // Случайное мерцание
        gsap.to(pixel, {
            x: Math.random() * 10 - 5,
            y: Math.random() * 10 - 5,
            duration: Math.random() * 2 + 1,
            repeat: -1,
            yoyo: true,
            ease: "sine.inOut"
        });
    }
}

// Эффект глитча при наведении на кнопку
document.getElementById('actionBtn').addEventListener('mouseenter', () => {
    const glitch = document.querySelector('.glitch');
    gsap.to(glitch, {
        x: () => Math.random() * 10 - 5,
        y: () => Math.random() * 10 - 5,
        duration: 0.05,
        repeat: 5,
        yoyo: true,
        ease: "power1.inOut",
        onComplete: () => {
            gsap.to(glitch, { x: 0, y: 0, duration: 0.1 });
        }
    });
    
    // Эффект вспышки
    gsap.to("body", {
        backgroundColor: "#1A1A00",
        duration: 0.1,
        repeat: 1,
        yoyo: true
    });
});

// Перенаправление на главную
document.getElementById('actionBtn').addEventListener('click', () => {
    // Эффект затухания перед переходом
    gsap.to(".container", {
        opacity: 0,
        y: 50,
        duration: 0.5,
        ease: "power2.in",
        onComplete: () => {
            window.location.href = "/";
        }
    });
    
    // Эффект помех при переходе
    gsap.to(".noise", {
        opacity: 0.8,
        duration: 0.3,
        yoyo: true,
        repeat: 3
    });
});

// Создаем пиксели при загрузке
document.addEventListener('DOMContentLoaded', () => {
    createPixels();
    
    // Анимация появления контейнера
    gsap.from(".container", {
        opacity: 0,
        y: 50,
        duration: 1,
        ease: "power2.out"
    });
    
    // Случайные вспышки на фоне
    setInterval(() => {
        if (Math.random() > 0.7) {
            gsap.to("body", {
                backgroundColor: "#0F0F00",
                duration: 0.1,
                repeat: 1,
                yoyo: true
            });
        }
    }, 3000);
});

// Эффект CRT-монитора при изменении размера
window.addEventListener('resize', () => {
    gsap.to(".container", {
        scale: 0.98,
        duration: 0.1,
        yoyo: true,
        repeat: 1
    });
});