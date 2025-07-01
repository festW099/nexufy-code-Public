import pytest
import sqlite3
import os
from app import app, get_db_connection_user

@pytest.fixture
def client():
    # Настройка тестового приложения
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'DATABASE_USER': 'test_users.db'
    })
    
    with app.test_client() as client:
        with app.app_context():
            # Инициализация тестовой БД
            init_test_db()
        yield client
    
    # Удаление тестовой БД после тестов
    if os.path.exists('test_users.db'):
        os.remove('test_users.db')

def init_test_db():
    """Инициализация тестовой базы данных"""
    conn = get_db_connection_user()
    cursor = conn.cursor()
    
    # Удаляем если существует и создаем заново
    cursor.execute('DROP TABLE IF EXISTS users')
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Тесты регистрации
def test_register_page_get(client):
    """Тест GET запроса страницы регистрации"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

def test_register_success(client):
    """Тест успешной регистрации"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'Testpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert 'Вы успешно зарегистрировались' in response.data
    
    # Проверка записи в БД
    conn = get_db_connection_user()
    user = conn.execute('SELECT * FROM users WHERE username = ?', ('newuser',)).fetchone()
    conn.close()
    
    assert user is not None
    assert user['email'] == 'new@example.com'

# Тесты входа
def test_login_success(client):
    """Тест успешного входа"""
    # Сначала регистрируем пользователя
    client.post('/register', data={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'Loginpass123'
    })
    
    # Тестируем вход
    response = client.post('/login', data={
        'email': 'login@example.com',
        'password': 'Loginpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'successfully logged in' in response.data

def test_login_wrong_password(client):
    """Тест входа с неверным паролем"""
    client.post('/register', data={
        'username': 'wrongpass',
        'email': 'wrongpass@example.com',
        'password': 'Rightpass123'
    })
    
    response = client.post('/login', data={
        'email': 'wrongpass@example.com',
        'password': 'Wrongpass123'
    }, follow_redirects=True)
    
    assert b'Invalid email or password' in response.data

# Тесты выхода
def test_logout(client):
    """Тест выхода из системы"""
    client.post('/register', data={
        'username': 'logoutuser',
        'email': 'logout@example.com',
        'password': 'Logoutpass123'
    })
    client.post('/login', data={
        'email': 'logout@example.com',
        'password': 'Logoutpass123'
    })
    
    response = client.get('/logout', follow_redirects=True)
    assert b'successfully logged out' in response.data
    assert b'Login' in response.data  # Проверяем редирект на страницу входа

# python -m pytest -v test/
# python -m pytest test/