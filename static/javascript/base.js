document.addEventListener('DOMContentLoaded', function() {
    // Элементы меню
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    // Проверка существования элементов
    if (!mobileMenuButton || !mobileMenu) {
        console.error('Mobile menu elements not found');
        return;
    }

    // Функция для переключения меню
    function toggleMenu() {
        mobileMenu.classList.toggle('open');
        
        // Блокировка скролла при открытом меню
        if (mobileMenu.classList.contains('open')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }

    // Функция для закрытия меню
    function closeMenu(e) {
        // Проверяем, что клик был вне меню и кнопки
        if (mobileMenu.classList.contains('open') && 
            !mobileMenu.contains(e.target) && 
            !mobileMenuButton.contains(e.target)) {
            mobileMenu.classList.remove('open');
            document.body.style.overflow = '';
        }
    }

    // Обработчики для кнопки меню
    mobileMenuButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleMenu();
    });
    
    // Touch-события для мобильных устройств
    mobileMenuButton.addEventListener('touchstart', function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleMenu();
    });

    // Обработчики для закрытия меню
    document.addEventListener('click', closeMenu);
    document.addEventListener('touchstart', closeMenu);
    
    // Обработчики для ссылок внутри меню (чтобы меню закрывалось при клике)
    const mobileLinks = mobileMenu.querySelectorAll('a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            mobileMenu.classList.remove('open');
            document.body.style.overflow = '';
        });
    });

    // Загрузчик (только для главной страницы)
    function initLoader() {
        const loaderContainer = document.getElementById('loader-container');
        if (!loaderContainer || loaderContainer.style.display === 'none') return;
        
        const progressBar = document.getElementById('progress-bar');
        let progress = 0;
        
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
                hideLoader();
            }
            progressBar.style.width = `${progress}%`;
        }, 40);
        
        // На всякий случай устанавливаем таймаут
        setTimeout(() => {
            if (progress < 100) {
                clearInterval(interval);
                progressBar.style.width = '100%';
                setTimeout(hideLoader, 300);
            }
        }, 7000);
    }
    
    function hideLoader() {
        const loader = document.getElementById('loader-container');
        const content = document.getElementById('content');
        
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
                if (content) {
                    content.style.display = 'block';
                    content.style.opacity = '0';
                    content.style.transition = 'opacity 0.5s ease';
                    setTimeout(() => {
                        content.style.opacity = '1';
                    }, 10);
                }
            }, 500);
        } else if (content) {
            content.style.display = 'block';
        }
    }
    
    // Проверяем, нужно ли запускать загрузчик
    if (document.getElementById('loader-container') && 
        document.getElementById('loader-container').style.display !== 'none') {
        window.addEventListener('load', initLoader);
    } else {
        document.getElementById('content').style.display = 'block';
    }
});

// Предотвращение перехода по ссылкам с # (если нужно)
document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', function(e) {
        if (e.target.tagName === 'A' && e.target.getAttribute('href') === '#') {
            e.preventDefault();
        }
    });
});