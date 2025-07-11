from flask import Flask, request, render_template, redirect, url_for, session, flash, get_flashed_messages, send_file, send_from_directory
from user_agents import parse
import sqlite3
import secrets
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import zipfile
from io import BytesIO
import uuid
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)  # Генерируем секретный ключ

# Путь к базе данных
DATABASE_USER = 'Database/users.db'
DATABASE_EVENTS = 'Database/events.db'
#тест
# Функция для подключения к базе данных
def get_db_connection_user():
    conn = sqlite3.connect(DATABASE_USER)
    conn.row_factory = sqlite3.Row
    return conn

def init_events_db():
    conn = sqlite3.connect('Database/events.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            long TEXT NOT NULL,
            price INTEGER NOT NULL,
            prize INTEGER NOT NULL,
            start NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

init_events_db()

def get_db_connection_event():
    conn = sqlite3.connect(DATABASE_EVENTS)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db_connection_user()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                date TEXT NOT NULL,
                block TEXT,
                raiting INTEGER NOT NULL,
                photo_path TEXT,
                awards TEXT,
                telegram TEXT,
                Country TEXT,
                City TEXT
            )
        ''')
        db.commit()
        db.close()

init_db()

def init_tasks_db():
    os.makedirs('Database', exist_ok=True)
    conn = sqlite3.connect('Database/tasks.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            test_cases TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_events_db()
init_tasks_db()

# Настройка загрузки файлов
UPLOAD_FOLDER = 'static/photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Создаем папку для фото, если ее нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/admin/content', methods=['GET', 'POST'])
def admin_content1():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        # Получаем данные из формы
        event_type = request.form['type']
        name = request.form['name']
        description = request.form['description']
        start_datetime = request.form['start']  # Получаем дату и время начала
        long_text = request.form['long']
        price = int(request.form['price'])
        prize = int(request.form['prize'])
        
        # Разделяем дату и время из поля start
        start_parts = start_datetime.split(' ')
        date = start_parts[0]  # Дата (Y-m-d)
        start_time = start_parts[1] if len(start_parts) > 1 else '00:00'  # Время (H:i)
        
        # Сохраняем в базу данных событий
        conn = sqlite3.connect('Database/events.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (type, name, description, date, long, price, prize, start)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_type, name, description, date, long_text, price, prize, start_time))

        last_inserted_id = cursor.lastrowid
        participants_table_name = f"event_{last_inserted_id}_participants"
        
        if event_type in ['ctf', 'sportprogramming']:
            cursor.execute(f'''
                CREATE TABLE {participants_table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
        elif event_type == 'gamejam':
            cursor.execute(f'''
                CREATE TABLE {participants_table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    task_0 INTEGER DEFAULT 0
                )
            ''')

        conn.commit()
        conn.close()
            
        return redirect(url_for('admin_content', event_id=last_inserted_id))
    
    return render_template('admin/admin_content.html')

@app.route('/admin/content/<int:event_id>', methods=['GET', 'POST'])
def admin_content(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Получаем информацию о событии
    conn = sqlite3.connect('Database/events.db')
    cursor = conn.cursor()
    cursor.execute('SELECT type FROM events WHERE id = ?', (event_id,))
    event_type = cursor.fetchone()[0]
    conn.close()
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Собираем все тест-кейсы
        test_cases = []
        i = 1
        while True:
            input_data = request.form.get(f'input_{i}', '').strip()
            output_data = request.form.get(f'output_{i}', '').strip()
            if not input_data and not output_data and i > 1:
                break
            if input_data or output_data:
                test_cases.append(f"{input_data}|||{output_data}")
            i += 1
        
        # Сохраняем задачу в базу данных
        conn = sqlite3.connect('Database/tasks.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (event_id, name, description, test_cases)
            VALUES (?, ?, ?, ?)
        ''', (event_id, name, description, ';;;'.join(test_cases)))
        
        # Для CTF/SportProgramming обновляем таблицу участников
        if event_type in ['ctf', 'sportprogramming']:
            # Получаем текущее количество задач
            conn_events = sqlite3.connect('Database/events.db')
            cursor_events = conn_events.cursor()
            
            # Получаем список всех столбцов
            cursor_events.execute(f"PRAGMA table_info(event_{event_id}_participants)")
            columns = cursor_events.fetchall()
            existing_tasks = [col[1] for col in columns if col[1].startswith('task_')]
            
            # Определяем следующий номер задачи
            if existing_tasks:
                last_task_num = max([int(task.split('_')[1]) for task in existing_tasks])
                new_task_num = last_task_num + 1
            else:
                new_task_num = 0
            
            # Добавляем новый столбец
            cursor_events.execute(f'''
                ALTER TABLE event_{event_id}_participants
                ADD COLUMN task_{new_task_num} INTEGER DEFAULT 0
            ''')
            
            conn_events.commit()
            conn_events.close()
        
        conn.commit()
        conn.close()
        
        return redirect(url_for('admin_content', event_id=event_id))
    
    # Получаем задачи из базы данных
    conn = sqlite3.connect('Database/tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE event_id = ?', (event_id,))
    tasks = []
    for row in cursor.fetchall():
        test_cases = []
        if row[4]:  # Проверяем наличие test_cases
            for case in row[4].split(';;;'):
                parts = case.split('|||', 1)
                input_data = parts[0] if len(parts) > 0 else ''
                output_data = parts[1] if len(parts) > 1 else ''
                test_cases.append({'input': input_data, 'output': output_data})
        tasks.append({
            'id': row[0],
            'name': row[2],
            'description': row[3],
            'test_cases': test_cases
        })
    conn.close()
    
    # Получаем количество задач из таблицы участников (для CTF/SportProgramming)
    task_count = 0
    if event_type in ['ctf', 'sportprogramming']:
        conn = sqlite3.connect('Database/events.db')
        cursor = conn.cursor()
        try:
            cursor.execute(f"PRAGMA table_info(event_{event_id}_participants)")
            columns = cursor.fetchall()
            task_count = len([col for col in columns if col[1].startswith('task_')])
        except:
            pass
        conn.close()
    
    return render_template('admin/task_content.html', 
                         event_id=event_id, 
                         tasks=tasks,
                         event_type=event_type,
                         task_count=task_count)

@app.route('/admin/content/<int:event_id>/delete_task/<int:task_id>', methods=['POST'])
def delete_task(event_id, task_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('Database/tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_content', event_id=event_id))

@app.route('/teach', methods=['GET', 'POST'])
def teach():
    db = get_db_connection_user()
        
    try:
        current_user = db.execute('SELECT block FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if current_user is None:
            db.close()
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))  
            
        if current_user['block'] == 'True':
            db.close()
            flash('Ваш аккаунт заблокирован. Доступ к профилям ограничен.', 'danger')
            return redirect(url_for('ban'))
    except Exception as e:
        pass

    user_id = session.get('user_id')
    if user_id == None:
        username = session.get('username')
    else:
        username = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        username = username['username']
    is_authenticated = 'username' in session
    db.close()
    return render_template('teach/main.html', is_authenticated=is_authenticated, username=username, current_user_id=user_id, user_id=user_id)

@app.route('/contests')
def contests():
    db = get_db_connection_user()
        
    try:
        # Проверяем, не забанен ли текущий пользователь
        current_user = db.execute('SELECT block FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if current_user is None:
            db.close()
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))
            
        if current_user['block'] == 'True':
            db.close()
            flash('Ваш аккаунт заблокирован. Доступ к профилям ограничен.', 'danger')
            return redirect(url_for('ban'))
    except Exception as e:
        pass

    user_agent = parse(request.headers.get('User-Agent'))
    user_id = session.get('user_id')
    if user_id == None:
        username = session.get('username')
    else:
        username = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        username = username['username']
    is_authenticated = 'username' in session
    db.close()

    conn = db = get_db_connection_event()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    conn.close()
    formatted_events = []
    moscow_tz = pytz.timezone('Europe/Moscow')

    for event in events:
        event_dict = {
            'id': event[0],
            'name': event[2],
            'date': event[4],
            'duration': event[5],
            'price': event[6],
            'prize': event[7],
            'start': event[8]
        }

        # Преобразование даты и времени в объект datetime с учетом московского времени
        date_str = event[4].split('/')
        start_time_str = event[8]
        duration_str = event[5] or "02:00"  # Значение по умолчанию, если поле пустое

        try:
            # Создаем объекты для сортировки
            event_year = int(date_str[2])
            event_month = int(date_str[0])
            event_day = int(date_str[1])
            event_hour = int(start_time_str.split(':')[0])
            event_minute = int(start_time_str.split(':')[1])
            
            # Сохраняем datetime для сортировки
            sort_datetime = datetime(
                event_year, event_month, event_day,
                event_hour, event_minute
            )
            event_dict['sort_datetime'] = moscow_tz.localize(sort_datetime)
            
            # Обработка для отображения статуса
            naive_datetime = datetime(
                event_year, event_month, event_day,
                event_hour, event_minute
            )
            start_time = moscow_tz.localize(naive_datetime)
            
            # Парсим длительность
            if ':' in duration_str:
                duration_parts = duration_str.split(':')
                if len(duration_parts) == 2 and duration_parts[0].isdigit() and duration_parts[1].isdigit():
                    duration_hours = int(duration_parts[0])
                    duration_minutes = int(duration_parts[1])
                else:
                    duration_hours, duration_minutes = 2, 0
            else:
                duration_hours, duration_minutes = 2, 0
            
            duration = timedelta(hours=duration_hours, minutes=duration_minutes)
            end_time = start_time + duration
            
            current_time = datetime.now(moscow_tz)

            if current_time < start_time:
                time_diff = start_time - current_time
                event_dict['status'] = 'Регистрация'
                days = time_diff.days
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                if days > 0:
                    event_dict['time_remaining'] = f"{days} д {hours} ч {minutes} м"
                else:
                    event_dict['time_remaining'] = f"{hours} ч {minutes} м"
            elif start_time <= current_time <= end_time:
                time_diff = end_time - current_time
                event_dict['status'] = 'В процессе'
                hours, remainder = divmod(time_diff.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                event_dict['time_remaining'] = f"{hours} ч {minutes} м"
            else:
                event_dict['status'] = 'Завершен'
                event_dict['time_remaining'] = 'Завершен'

        except (ValueError, IndexError, AttributeError) as e:
            event_dict['sort_datetime'] = datetime.min.replace(tzinfo=moscow_tz)
            event_dict['status'] = 'Регистрация'
            event_dict['time_remaining'] = 'Время не указано'

        formatted_events.append(event_dict)

    # Сортируем события по дате и времени (новые сначала)
    formatted_events.sort(key=lambda x: x['sort_datetime'], reverse=True)

    return render_template('contests.html', 
                         events=formatted_events, 
                         is_authenticated=is_authenticated, 
                         username=username, 
                         current_user_id=user_id, 
                         user_id=user_id)

@app.route('/ban')
def ban():
    return render_template('ban.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    db = get_db_connection_user()
        
    try:
        current_user = db.execute('SELECT block FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if current_user is None:
            db.close()
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))  
            
        if current_user['block'] == 'True':
            db.close()
            flash('Ваш аккаунт заблокирован. Доступ к профилям ограничен.', 'danger')
            return redirect(url_for('ban'))
    except Exception as e:
        pass

    current_user_id = session.get('user_id')
    if current_user_id == None:
        username = session.get('username')
    else:
        username = db.execute('SELECT username FROM users WHERE id = ?', (current_user_id,)).fetchone()
        username = username['username']
    db.close()
    user_agent = parse(request.headers.get('User-Agent'))
    is_authenticated = 'username' in session

    if 'user_id' not in session:
        flash('Пожалуйста, войдите для просмотра профиля', 'warning')
        return redirect(url_for('login'))
    
    db = get_db_connection_user()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()
    
    if user is None:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('index'))
    
    is_owner = session.get('user_id') == user_id
    
    if request.method == 'POST' and is_owner:
        new_username = request.form.get('username')
        country = request.form.get('country')
        city = request.form.get('city')
        telegram = request.form.get('telegram')
        
        if 'photo' in request.files:
            file = request.files['photo']
            if file and allowed_file(file.filename):
                if user['photo_path']:
                    try:
                        old_photo = os.path.join(app.config['UPLOAD_FOLDER'], user['photo_path'])
                        if os.path.exists(old_photo):
                            os.remove(old_photo)
                    except OSError:
                        pass
                
                extension = file.filename.rsplit('.', 1)[1].lower()
                filename = f"user_{user_id}.{extension}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                db = get_db_connection_user()
                db.execute('UPDATE users SET photo_path = ? WHERE id = ?', (filename, user_id))
                db.commit()
                db.close()
        
        db = get_db_connection_user()
        try:
            db.execute('''
                UPDATE users 
                SET username = ?, Country = ?, City = ?, telegram = ?
                WHERE id = ?
            ''', (new_username, country or None, city or None, telegram or None, user_id))
            db.commit()
            flash('Профиль успешно обновлен', 'success')
        except db.IntegrityError:
            flash('Это имя пользователя уже занято', 'danger')
        finally:
            db.close()
        return redirect(url_for('profile', user_id=user_id))
    
    photo_path = None
    if user['photo_path']:
        photo_path = f"/static/photos/{user['photo_path']}"
    else:
        for ext in ['png', 'jpg', 'jpeg', 'gif']:
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], f"user_{user_id}.{ext}")):
                photo_path = f"/static/photos/user_{user_id}.{ext}"
                break

    return render_template('profile.html', 
                         user=user, 
                         is_owner=is_owner, 
                         is_authenticated=is_authenticated, 
                         username=username, 
                         user_id=user_id, 
                         current_user_id=current_user_id,
                         photo_path=photo_path)

@app.route('/photo/<int:user_id>')
def user_photo(user_id):
    db = get_db_connection_user()
        
    try:
        # Проверяем, не забанен ли текущий пользователь
        current_user = db.execute('SELECT block FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if current_user is None:
            db.close()
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))  # или на другую подходящую страницу
            
        if current_user['block'] == 'True':
            db.close()
            flash('Ваш аккаунт заблокирован. Доступ к профилям ограничен.', 'danger')
            return redirect(url_for('ban'))  # или на специальную страницу с информацией о блокировке
    except Exception as e:
        pass

    user = db.execute('SELECT photo_path FROM users WHERE id = ?', (user_id,)).fetchone()
    db.close()
    
    if user and user['photo_path']:
        return send_from_directory(app.config['UPLOAD_FOLDER'], user['photo_path'])
    else:
        # Возвращаем фото по умолчанию, если своего нет
        return send_from_directory('static', 'default_avatar.png')

@app.route('/register', methods=['GET', 'POST'])
def register():
    user_agent = parse(request.headers.get('User-Agent'))
    is_authenticated = 'username' in session

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Валидация данных
        if not username or not email or not password:
            error = "Все поля обязательны для заполнения"
        elif len(password) < 6:
            error = "Пароль должен содержать не менее 6 символов"
        else:
            try:
                db = get_db_connection_user()
                # Проверка на существующего пользователя перед вставкой
                existing_user = db.execute(
                    'SELECT * FROM users WHERE username = ? OR email = ?', 
                    (username, email)
                ).fetchone()
                
                if existing_user:
                    if existing_user['username'] == username:
                        error = "Пользователь с таким именем уже существует"
                    else:
                        error = "Пользователь с такой электронной почтой уже существует"
                else:
                    hashed_password = generate_password_hash(password)
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    raiting = 0

                    db.execute(
                        'INSERT INTO users (username, email, password, date, block, raiting) VALUES (?, ?, ?, ?, ?, ?)', 
                        (username, email, hashed_password, current_date, False, raiting)
                    )
                    db.commit()
                    return redirect(url_for('login'))
            except sqlite3.Error as e:
                error = "Произошла ошибка при регистрации. Пожалуйста, попробуйте позже."
                app.logger.error(f"Ошибка регистрации: {e}")
            finally:
                db.close()

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_agent = parse(request.headers.get('User-Agent'))
    is_authenticated = 'username' in session
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            error = "Пожалуйста, введите email и пароль"
        else:
            db = get_db_connection_user()
            try:
                user = db.execute(
                    'SELECT * FROM users WHERE email = ?', 
                    (email,)
                ).fetchone()
                
                if user and check_password_hash(user['password'], password):
                    session['username'] = user['username']
                    session['email'] = user['email']
                    session['user_id'] = user['id']
                    flash("Вы успешно вошли в систему.", "success")
                    return redirect(url_for('index'))
                else:
                    error = "Неверный email или пароль"
            except sqlite3.Error as e:
                error = "Произошла ошибка при входе. Пожалуйста, попробуйте позже."
                app.logger.error(f"Ошибка входа: {e}")
            finally:
                db.close()

    return render_template('login.html', error=error)

@app.route('/')
def index():
    db = get_db_connection_user()
        
    try:
        # Проверяем, не забанен ли текущий пользователь
        current_user = db.execute('SELECT block FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if current_user is None:
            db.close()
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))  # или на другую подходящую страницу
            
        if current_user['block'] == 'True':
            db.close()
            flash('Ваш аккаунт заблокирован. Доступ к профилям ограничен.', 'danger')
            return redirect(url_for('ban'))  # или на специальную страницу с информацией о блокировке
    except Exception as e:
        pass

    user_agent = parse(request.headers.get('User-Agent'))
    user_id = session.get('user_id')
    if user_id == None:
        username = session.get('username')
    else:
        username = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        username = username['username']
    is_authenticated = 'username' in session
    db.close()

    if user_agent.is_mobile:
        return "Mobile"
    elif user_agent.is_tablet:
        return "Tablet"
    else:
        return render_template('main.html', is_authenticated=is_authenticated, username=username, user_id=user_id)

@app.route('/raiting')
def raiting():
    db = get_db_connection_user()
        
    try:
        # Проверяем, не забанен ли текущий пользователь
        current_user = db.execute('SELECT block FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if current_user is None:
            db.close()
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))  # или на другую подходящую страницу
            
        if current_user['block'] == 'True':
            db.close()
            flash('Ваш аккаунт заблокирован. Доступ к профилям ограничен.', 'danger')
            return redirect(url_for('ban'))  # или на специальную страницу с информацией о блокировке
    except Exception as e:
        pass


    username = session.get('username')
    user_agent = parse(request.headers.get('User-Agent'))
    user_id = session.get('user_id')
    is_authenticated = 'username' in session

    # Получаем топ 10 пользователей по рейтингу
    db = get_db_connection_user()
    top_users = db.execute('''
        SELECT id, username, raiting, photo_path 
        FROM users 
        ORDER BY raiting DESC 
        LIMIT 10
    ''').fetchall()
    db.close()

    return render_template(
        'raiting.html', 
        is_authenticated=is_authenticated, 
        username=username, 
        user_id=user_id,
        top_users=top_users
    )

@app.route('/agreements')
def agreements():
    db = get_db_connection_user()
        
    try:
        # Проверяем, не забанен ли текущий пользователь
        current_user = db.execute('SELECT block FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if current_user is None:
            db.close()
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))  # или на другую подходящую страницу
            
        if current_user['block'] == 'True':
            db.close()
            flash('Ваш аккаунт заблокирован. Доступ к профилям ограничен.', 'danger')
            return redirect(url_for('ban'))  # или на специальную страницу с информацией о блокировке
    except Exception as e:
        pass

    return render_template('agreements.html')

@app.route('/faq')
def faq():
    db = get_db_connection_user()
        
    try:
        # Проверяем, не забанен ли текущий пользователь
        current_user = db.execute('SELECT block FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        
        if current_user is None:
            db.close()
            flash('Пользователь не найден', 'danger')
            return redirect(url_for('index'))  
            
        if current_user['block'] == 'True':
            db.close()
            flash('Ваш аккаунт заблокирован. Доступ к профилям ограничен.', 'danger')
            return redirect(url_for('ban'))  # или на специальную страницу с информацией о блокировке
    except Exception as e:
        pass

    user_agent = parse(request.headers.get('User-Agent'))
    user_id = session.get('user_id')
    if user_id == None:
        username = session.get('username')
    else:
        username = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        username = username['username']
    is_authenticated = 'username' in session
    db.close()
    return render_template('faq.html', is_authenticated=is_authenticated, username=username, current_user_id=user_id, user_id=user_id)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('email', None)
    session.pop('user_id', None)
    flash("Вы успешно вышли из системы.", "success")
    return redirect(url_for('login'))

# Маршрут для входа в админ панель
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'root' and password == '00000000': # в будующем исправить это, тк тот, кто увидит код сможет узнать пароль
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin/main.html', error="Неверное имя пользователя или пароль")
    
    return render_template('admin/main.html')

# Маршрут для выхода из админ панели
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Маршрут для админ панели
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    db = get_db_connection_user()
    
    # Получаем 10 последних пользователей
    users = db.execute('''
        SELECT id, username, email, date, block 
        FROM users 
        ORDER BY date DESC 
        LIMIT 10
    ''').fetchall()
    
    # Статистика
    # Всего пользователей
    total_users = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]

    # Новые регистрации за последнюю неделю
    new_registrations = db.execute('''
        SELECT COUNT(*) FROM users 
        WHERE date > datetime('now', '-7 days')
    ''').fetchone()[0]
    
    # Всего забанено
    banned_users = db.execute('SELECT COUNT(*) FROM users WHERE block = "True"').fetchone()[0]
    
    # Сравнения с предыдущим периодом
    # Для пользователей - сравнение с месяцем назад
    prev_month_users = db.execute('''
        SELECT COUNT(*) FROM users 
        WHERE date > datetime('now', '-60 days') AND date < datetime('now', '-30 days')
    ''').fetchone()[0]
    users_change = ((total_users - prev_month_users) / prev_month_users * 100) if prev_month_users else 0
    
    # Для регистраций - сравнение с предыдущей неделей
    prev_week_registrations = db.execute('''
        SELECT COUNT(*) FROM users 
        WHERE date > datetime('now', '-14 days') AND date < datetime('now', '-7 days')
    ''').fetchone()[0]
    registrations_change = ((new_registrations - prev_week_registrations) / prev_week_registrations * 100) if prev_week_registrations else 0
    
    db.close()
    
    return render_template('admin/main.html', 
                         users=users,
                         stats={
                             'total_users': total_users,
                             'new_registrations': new_registrations,
                             'banned_users': banned_users,
                             'users_change': users_change,
                             'registrations_change': registrations_change
                         })

@app.route('/admin/static')
def admin_users():
    # Получаем список пользователей из базы данных
    db = get_db_connection_user()
    users = db.execute('SELECT * FROM users').fetchall()
    db.close()
    
    # Рассчитываем статистику
    total_users = len(users)
    active_users = len([u for u in users if u['block'] == 'False'])
    banned_users = len([u for u in users if u['block'] == 'True'])
    pending_users = len([u for u in users if u['block'] == 'Modern'])
    
    stats = {
        'total_users': total_users,
        'active_users': active_users,
        'banned_users': banned_users,
        'pending_users': pending_users,
        'active_percentage': round((active_users / total_users) * 100) if total_users else 0,
        'pending_percentage': round((pending_users / total_users) * 100) if total_users else 0,
        'new_last_week': 0,  # Здесь нужно добавить реальную логику
        'new_bans_last_week': 0  # Здесь нужно добавить реальную логику
    }
    
    return render_template('admin/user_static.html', 
                         users=users, 
                         stats=stats)

@app.route('/admin/setting')
def admin_setting():
    
    return render_template('admin/setting.html')

@app.route('/toggle_user_block/<int:user_id>', methods=['POST'])
def toggle_user_block(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    db = get_db_connection_user()
    # Получаем текущее состояние блокировки
    user = db.execute('SELECT block FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user:
        new_block_status = 'True' if user['block'] == 'False' else 'False'
        db.execute('UPDATE users SET block = ? WHERE id = ?', (new_block_status, user_id))
        db.commit()
    
    db.close()
    
    return redirect(request.referrer)

@app.route('/admin/backup')
def backup_database():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Путь к папке с базами данных
    database_dir = 'Database'
    
    # Создаем временный zip-архив в памяти
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Добавляем все файлы из папки database в архив
        for root, dirs, files in os.walk(database_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(database_dir))
                zipf.write(file_path, arcname)
    
    # Перемещаем указатель в начало файла
    memory_file.seek(0)

    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Отправляем архив пользователю
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'database_backup-{current_date}.zip'
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)