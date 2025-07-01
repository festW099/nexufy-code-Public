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
    
    // Обработчик для кнопки закрытия (если нужно)
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            // Ваш код для закрытия
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const telegramInput = document.getElementById('telegram');
    const telegramError = document.getElementById('telegramError');

    telegramInput.addEventListener('input', function() {
        const value = telegramInput.value;
        if (value.includes('@') || value.includes('http')) {
            telegramError.classList.remove('hidden');
        } else {
            telegramError.classList.add('hidden');
        }
    });

    const form = document.getElementById('editProfileForm');
    form.addEventListener('submit', function(event) {
        if (telegramInput.value.includes('@') || telegramInput.value.includes('http')) {
            event.preventDefault();
            telegramError.classList.remove('hidden');
        }
    });
});

// Particles.js initialization with more visible particles
document.addEventListener('DOMContentLoaded', function() {
    particlesJS('particles-js', {
        "particles": {
            "number": {
                "value": 50,
                "density": {
                    "enable": true,
                    "value_area": 800
                }
            },
            "color": {
                "value": "#fef08a"
            },
            "shape": {
                "type": "circle",
                "stroke": {
                    "width": 0,
                    "color": "#000000"
                }
            },
            "opacity": {
                "value": 0.7,
                "random": true,
                "anim": {
                    "enable": true,
                    "speed": 1,
                    "opacity_min": 0.3,
                    "sync": false
                }
            },
            "size": {
                "value": 4,
                "random": true,
                "anim": {
                    "enable": true,
                    "speed": 4,
                    "size_min": 0.3,
                    "sync": false
                }
            },
            "line_linked": {
                "enable": true,
                "distance": 120,
                "color": "#fef08a",
                "opacity": 0.4,
                "width": 1
            },
            "move": {
                "enable": true,
                "speed": 2,
                "direction": "none",
                "random": true,
                "straight": false,
                "out_mode": "out",
                "bounce": false,
                "attract": {
                    "enable": true,
                    "rotateX": 600,
                    "rotateY": 1200
                }
            }
        },
        "interactivity": {
            "detect_on": "window",
            "events": {
                "onhover": {
                    "enable": true,
                    "mode": "repulse"
                },
                "onclick": {
                    "enable": true,
                    "mode": "push"
                },
                "resize": true
            },
            "modes": {
                "repulse": {
                    "distance": 100,
                    "duration": 0.4
                },
                "push": {
                    "particles_nb": 6
                }
            }
        },
        "retina_detect": true
    });
});

// Glow effect on interactive elements
document.querySelectorAll('button, input, .profile-image').forEach(el => {
    el.addEventListener('mouseenter', () => {
        el.style.boxShadow = '0 0 15px rgba(254, 240, 138, 0.5)';
        el.style.transition = 'box-shadow 0.3s ease';
    });
    
    el.addEventListener('mouseleave', () => {
        el.style.boxShadow = '';
    });
});