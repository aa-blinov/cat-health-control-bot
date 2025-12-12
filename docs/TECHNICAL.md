# Cat Health Control — Техническая документация

## 🏗️ Архитектура системы

### Общая схема

```
┌─────────────────┐
│   Пользователь  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Telegram│ │  Web  │
│  Bot   │ │Browser│
└───┬────┘ └───┬───┘
    │          │
    │   ┌──────▼──────┐
    │   │   Flask     │
    │   │   Web App   │
    │   │ (port 5000) │
    │   └──────┬──────┘
    │          │
┌───▼──────────▼───┐
│  Python Backend  │
│   (bot/db.py)    │
└────────┬─────────┘
         │
    ┌────▼─────┐
    │ MongoDB  │
    │(port 27017)│
    └──────────┘
```

### Принципы архитектуры

1. **Микросервисная архитектура**: три независимых сервиса (Bot, Web, DB)
2. **Общая база данных**: единый источник истины для всех клиентов
3. **Stateless API**: веб-приложение не хранит состояние между запросами
4. **Контейнеризация**: все компоненты работают в Docker-контейнерах
5. **Разделение ответственности**: бот — быстрый ввод, веб — детальный анализ

## 💻 Технологический стек

### Backend

| Компонент | Технология | Версия | Назначение |
|-----------|------------|--------|------------|
| Язык программирования | Python | 3.x | Основной язык разработки |
| Telegram Bot API | python-telegram-bot | latest | Интеграция с Telegram |
| Web Framework | Flask | latest | HTTP-сервер и API |
| База данных | MongoDB | latest | Хранение данных |
| MongoDB Driver | pymongo | latest | Драйвер для работы с БД |
| Security | werkzeug | latest | Хеширование паролей |
| WSGI Server | Gunicorn | (опционально) | Production-сервер |

### Frontend

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Шаблонизатор | Jinja2 | Рендеринг HTML |
| CSS | Custom CSS | Стилизация интерфейса |
| JavaScript | Vanilla JS | Интерактивность |
| UI Components | Custom | Формы и таблицы |

### Infrastructure

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Контейнеризация | Docker | Изоляция сервисов |
| Оркестрация | Docker Compose | Управление контейнерами |
| OS | Alpine Linux | Базовый образ контейнеров |

## 📦 Компоненты системы

### 1. Telegram Bot (bot/)

**Файлы**:
- `main.py` — точка входа, конфигурация conversation handler
- `handlers.py` — обработчики команд и сообщений
- `db.py` — работа с базой данных
- `config.py` — конфигурация из переменных окружения

**Основные функции**:

#### ConversationHandler States
```python
MAIN_MENU = 0                    # Главное меню
ASK_EVENT_DATETIME = 20          # Запрос времени события (астма)
HANDLE_EVENT_DATE = 22           # Обработка даты (астма)
HANDLE_EVENT_TIME = 23           # Обработка времени (астма)
ASK_ASTHMA_DURATION = 1          # Запрос длительности приступа
ASK_ASTHMA_REASON = 2            # Запрос причины
ASK_ASTHMA_INHALATION = 3        # Запрос об ингаляции
SAVE_ASTHMA_COMMENT = 4          # Сохранение комментария
ASK_DEFE_EVENT_DATETIME = 21     # Запрос времени (дефекация)
HANDLE_DEFE_EVENT_DATE = 24      # Обработка даты (дефекация)
HANDLE_DEFE_EVENT_TIME = 25      # Обработка времени (дефекация)
ASK_DEFE_STOOL_TYPE = 5          # Запрос типа стула
SAVE_DEFE_COMMENT = 6            # Сохранение комментария (дефекация)
CHOOSE_EXPORT_TYPE = 7           # Выбор типа экспорта
CHOOSE_EXPORT_FORMAT = 8         # Выбор формата экспорта
```

#### Ключевые обработчики
- `start()` — команда /start, проверка whitelist
- `ask_type()` — выбор действия (астма/дефекация/экспорт)
- `asthma_*()` — цепочка обработчиков для приступа астмы
- `ask_defe_*()` — цепочка обработчиков для дефекации
- `ask_export_type()` — выбор данных для экспорта
- `export_format()` — формирование и отправка файла

**Механизм работы**:
1. Пользователь отправляет команду или нажимает кнопку
2. ConversationHandler определяет текущее состояние
3. Вызывается соответствующий handler
4. Данные сохраняются в `context.user_data`
5. Переход в следующее состояние
6. Финальный handler сохраняет данные в БД

### 2. Web Application (web/)

**Файлы**:
- `main.py` — точка входа, запуск Flask-приложения
- `app.py` — Flask application, маршруты, API endpoints
- `templates/` — HTML-шаблоны
  - `base.html` — базовый шаблон с навигацией
  - `login.html` — страница входа
  - `dashboard.html` — главная панель управления
- `static/` — статические файлы
  - `css/style.css` — стили интерфейса

**Архитектура Flask-приложения**:

```python
Flask App
│
├── Routes (Pages)
│   ├── / (index) → redirect
│   ├── /login → authentication
│   ├── /logout → clear session
│   └── /dashboard → main UI
│
├── API Routes (JSON)
│   ├── /api/asthma [POST, GET]
│   ├── /api/asthma/<id> [PUT, DELETE]
│   ├── /api/defecation [POST, GET]
│   ├── /api/defecation/<id> [PUT, DELETE]
│   ├── /api/weight [POST, GET]
│   ├── /api/weight/<id> [PUT, DELETE]
│   └── /api/export/<type>/<format> [GET]
│
└── Middleware
    └── @login_required decorator
```

**Session Management**:
- Flask sessions (encrypted cookies)
- Хранение: `user_id`, `username`, `telegram_id`
- Secret key из переменной окружения `FLASK_SECRET_KEY`

**API Endpoints подробно**:

#### POST /api/asthma
Создание записи о приступе астмы.

**Request Body**:
```json
{
  "date": "2024-12-25",
  "time": "14:30",
  "duration": "Короткий",
  "reason": "Пил после сна",
  "inhalation": true,
  "comment": "Комментарий"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "Приступ астмы записан"
}
```

#### GET /api/asthma
Получение списка приступов астмы текущего пользователя.

**Query Parameters**: нет

**Response** (200 OK):
```json
{
  "attacks": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "date_time": "2024-12-25 14:30",
      "duration": "Короткий",
      "reason": "Пил после сна",
      "inhalation": "Да",
      "comment": "Комментарий"
    }
  ]
}
```

#### PUT /api/asthma/<record_id>
Обновление записи о приступе.

**Request Body**: аналогично POST

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Приступ астмы обновлен"
}
```

#### DELETE /api/asthma/<record_id>
Удаление записи о приступе.

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Приступ астмы удален"
}
```

#### GET /api/export/<export_type>/<format_type>
Экспорт данных в различных форматах.

**Parameters**:
- `export_type`: `asthma`, `defecation`, `weight`
- `format_type`: `csv`, `tsv`, `html`, `md`

**Response**: файл с соответствующим MIME-типом

**Headers**:
```
Content-Type: text/csv | text/html | text/markdown | text/tab-separated-values
Content-Disposition: attachment; filename*=UTF-8''<filename>
```

### 3. Database Layer (bot/db.py)

**MongoDB Collections**:

| Collection | Назначение | Индексы |
|------------|------------|---------|
| `asthma_attacks` | Приступы астмы | user_id, date_time |
| `defecations` | Дефекации | user_id, date_time |
| `weights` | Измерения веса | user_id, date_time |
| `whitelist_users` | Авторизованные пользователи | telegram_id (unique) |
| `user_context` | Временные данные бота | user_id |

**Функции для работы с БД**:

```python
# Контекст пользователя (для Telegram-бота)
save_user_context(user_id, key, value) → None
get_user_context(user_id) → Dict
clear_user_context(user_id) → None

# Whitelist
is_whitelisted(user_id) → bool
init_db() → None  # Загрузка whitelist.txt в БД

# Сохранение событий
save_asthma_attack(user_id, data) → None
save_defecation(user_id, data) → None
```

**Подключение к MongoDB**:
```python
mongo_uri = f"mongodb://{user}:{pass}@{host}:{port}/{db}?authSource=admin"
client = MongoClient(mongo_uri)
db = client[MONGO_DB]
```

## 📊 Схема базы данных

### Collection: asthma_attacks

```json
{
  "_id": ObjectId("..."),
  "user_id": 123456789,
  "date_time": ISODate("2024-12-25T14:30:00Z"),
  "duration": "Короткий",
  "reason": "Пил после сна",
  "inhalation": true,
  "comment": "Дополнительная информация"
}
```

**Поля**:
- `_id` — уникальный идентификатор (ObjectId)
- `user_id` — идентификатор пользователя (integer)
- `date_time` — дата и время события (datetime)
- `duration` — длительность приступа (string: "Короткий" | "Длительный")
- `reason` — причина приступа (string)
- `inhalation` — применение ингаляции (boolean)
- `comment` — комментарий пользователя (string, optional)

### Collection: defecations

```json
{
  "_id": ObjectId("..."),
  "user_id": 123456789,
  "date_time": ISODate("2024-12-25T10:00:00Z"),
  "stool_type": "Обычный",
  "food": "Royal Canin",
  "comment": "Всё в норме"
}
```

**Поля**:
- `_id` — уникальный идентификатор (ObjectId)
- `user_id` — идентификатор пользователя (integer)
- `date_time` — дата и время (datetime)
- `stool_type` — тип стула (string: "Обычный" | "Твердый" | "Жидкий")
- `food` — тип корма (string)
- `comment` — комментарий (string, optional)

### Collection: weights

```json
{
  "_id": ObjectId("..."),
  "user_id": 123456789,
  "date_time": ISODate("2024-12-25T09:00:00Z"),
  "weight": "4.5",
  "food": "Royal Canin",
  "comment": "После диеты"
}
```

**Поля**:
- `_id` — уникальный идентификатор (ObjectId)
- `user_id` — идентификатор пользователя (integer)
- `date_time` — дата и время взвешивания (datetime)
- `weight` — вес в килограммах (string)
- `food` — текущий корм (string)
- `comment` — комментарий (string, optional)

### Collection: whitelist_users

```json
{
  "_id": ObjectId("..."),
  "telegram_id": 123456789
}
```

**Поля**:
- `_id` — уникальный идентификатор (ObjectId)
- `telegram_id` — Telegram ID пользователя (integer, unique)

### Collection: user_context

```json
{
  "_id": ObjectId("..."),
  "user_id": 123456789,
  "event_datetime": ISODate("..."),
  "duration": "Короткий",
  "reason": "Пил",
  ...
}
```

**Назначение**: временное хранение данных во время диалога с ботом.

## ⚙️ Конфигурация

### Переменные окружения (.env)

```bash
# MongoDB Configuration
MONGO_USER=admin                 # Имя пользователя MongoDB
MONGO_PASS=password             # Пароль MongoDB
MONGO_HOST=db                   # Хост MongoDB (имя сервиса в Docker)
MONGO_PORT=27017                # Порт MongoDB
MONGO_DB=cat_health            # Имя базы данных

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_token   # Токен Telegram Bot от @BotFather

# Flask Web App
FLASK_SECRET_KEY=secret-key     # Секретный ключ для сессий Flask
DEFAULT_PASSWORD=admin123       # Пароль для веб-интерфейса
```

### Файл конфигурации (bot/config.py)

```python
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")
MONGO_DB = os.getenv("MONGO_DB", "cat_health")
```

### Whitelist (bot/whitelist.txt)

```
123456789
987654321
```

**Формат**: один telegram_id на строку.

**Применение**: при запуске бота (`init_db()`) все ID из файла загружаются в коллекцию `whitelist_users`.

## 🐳 Docker-конфигурация

### Dockerfile

```dockerfile
FROM python:3.11-alpine

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода
COPY . .

# Команда запуска определяется в docker-compose.yml
```

### docker-compose.yml

```yaml
services:
  db:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodata:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASS}
      MONGO_INITDB_DATABASE: ${MONGO_DB}
    healthcheck:
      test: ["CMD", "bash", "-c", "echo > /dev/tcp/localhost/27017"]
      interval: 10s
      timeout: 5s
      retries: 5

  bot:
    build: .
    env_file:
      - .env
    command: "python -m bot.main"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  web:
    build: .
    env_file:
      - .env
    command: "python -m web.main"
    ports:
      - "5001:5000"
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

volumes:
  mongodata:
```

**Особенности**:
- Healthcheck для MongoDB обеспечивает корректный порядок запуска
- Том `mongodata` для персистентного хранения данных
- `restart: unless-stopped` для автоматического восстановления при сбоях
- Порт 5001 на хосте → 5000 в контейнере (Flask)

## 🚀 Развёртывание

### Локальное развёртывание

#### Требования
- Docker 20.10+
- Docker Compose 2.0+
- Токен Telegram-бота от [@BotFather](https://t.me/BotFather)

#### Шаги установки

1. **Клонирование репозитория**:
```bash
git clone <repository-url>
cd cat-health-control-bot
```

2. **Создание файла .env**:
```bash
cp .env.example .env
nano .env
```

Заполните переменные:
```env
MONGO_USER=admin
MONGO_PASS=StrongPassword123
MONGO_HOST=db
MONGO_PORT=27017
MONGO_DB=cat_health
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
FLASK_SECRET_KEY=your-random-secret-key-here
DEFAULT_PASSWORD=admin123
```

3. **Создание whitelist.txt**:
```bash
echo "YOUR_TELEGRAM_ID" > bot/whitelist.txt
```

Получить свой Telegram ID можно через [@userinfobot](https://t.me/userinfobot).

4. **Запуск приложения**:
```bash
docker-compose up -d --build
```

5. **Проверка статуса**:
```bash
docker-compose ps
```

Все три сервиса должны быть в состоянии "Up":
```
NAME                COMMAND                  STATUS
cat-health-db       "docker-entrypoint.s…"   Up (healthy)
cat-health-bot      "python -m bot.main"     Up
cat-health-web      "python -m web.main"     Up
```

6. **Просмотр логов**:
```bash
# Все сервисы
docker-compose logs -f

# Только бот
docker-compose logs -f bot

# Только веб
docker-compose logs -f web
```

7. **Доступ к приложению**:
- Веб-интерфейс: `http://localhost:5001`
- Telegram-бот: найдите своего бота в Telegram и отправьте `/start`

### Production-развёртывание

#### Рекомендации для продакшена

1. **Использование Gunicorn**:

Измените команду для web в `docker-compose.yml`:
```yaml
command: "gunicorn -w 4 -b 0.0.0.0:5000 web.app:app"
```

Добавьте в `requirements.txt`:
```
gunicorn==21.2.0
```

2. **Использование Nginx как reverse proxy**:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **HTTPS с Let's Encrypt**:
```bash
sudo certbot --nginx -d your-domain.com
```

4. **Безопасность**:
- Генерируйте сильный `FLASK_SECRET_KEY`:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- Используйте сложные пароли для MongoDB
- Ограничьте доступ к портам через firewall
- Регулярно обновляйте Docker-образы

5. **Мониторинг**:
- Используйте `docker-compose logs` для отслеживания ошибок
- Настройте автоматический перезапуск контейнеров
- Мониторьте использование ресурсов:
  ```bash
  docker stats
  ```

6. **Резервное копирование**:

Backup MongoDB:
```bash
docker exec cat-health-db mongodump --username admin --password password --authenticationDatabase admin --out /backup
docker cp cat-health-db:/backup ./mongodb-backup-$(date +%Y%m%d)
```

Restore:
```bash
docker exec -i cat-health-db mongorestore --username admin --password password --authenticationDatabase admin /backup
```

### Обновление приложения

```bash
# Остановка сервисов
docker-compose down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose up -d --build

# Проверка
docker-compose ps
docker-compose logs -f
```

## 🛠️ Разработка

### Локальная разработка без Docker

#### Требования
- Python 3.9+
- MongoDB 5.0+
- pip

#### Установка зависимостей

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Установка пакетов
pip install -r requirements.txt
```

#### Запуск MongoDB локально

```bash
# Linux/Mac (Homebrew)
brew services start mongodb-community

# Linux (systemd)
sudo systemctl start mongod

# Docker (альтернатива)
docker run -d -p 27017:27017 --name mongo \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  mongo:latest
```

#### Настройка .env для локальной разработки

```env
MONGO_USER=admin
MONGO_PASS=password
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=cat_health
TELEGRAM_BOT_TOKEN=your_token
FLASK_SECRET_KEY=dev-secret-key
DEFAULT_PASSWORD=admin123
```

#### Запуск компонентов

**Telegram Bot**:
```bash
python -m bot.main
```

**Web Application**:
```bash
python -m web.main
```

Приложение будет доступно на `http://localhost:5000`.

### Структура проекта

```
cat-health-control-bot/
│
├── bot/                          # Telegram Bot
│   ├── __init__.py
│   ├── main.py                   # Точка входа
│   ├── handlers.py               # Обработчики команд
│   ├── db.py                     # Работа с БД
│   ├── config.py                 # Конфигурация
│   └── whitelist.txt             # Список разрешённых пользователей
│
├── web/                          # Web Application
│   ├── __init__.py
│   ├── main.py                   # Точка входа
│   ├── app.py                    # Flask приложение
│   ├── templates/                # HTML шаблоны
│   │   ├── base.html             # Базовый шаблон
│   │   ├── login.html            # Страница входа
│   │   └── dashboard.html        # Главная панель
│   └── static/                   # Статические файлы
│       └── css/
│           └── style.css         # Стили
│
├── docs/                         # Документация
│   ├── PRODUCT.md                # Продуктовая документация
│   └── TECHNICAL.md              # Техническая документация
│
├── .env                          # Переменные окружения (не в Git)
├── .env.example                  # Пример конфигурации
├── .gitignore                    # Игнорируемые файлы
├── Dockerfile                    # Docker-образ
├── docker-compose.yml            # Оркестрация контейнеров
├── requirements.txt              # Python-зависимости
├── pyproject.toml                # Метаданные проекта
└── README.md                     # Основная документация
```

### Добавление новых функций

#### Пример: добавление нового типа события

1. **Обновление схемы БД** (bot/db.py):
```python
new_events = db["new_events"]

def save_new_event(user_id: int, data: Dict[str, Any]) -> None:
    event_time = data.get("date_time", datetime.now())
    new_events.insert_one({"user_id": user_id, **data, "date_time": event_time})
```

2. **Добавление обработчиков в бот** (bot/handlers.py):
```python
async def handle_new_event(update: Update, context: CallbackContext) -> int:
    # Логика обработки
    pass
```

3. **Добавление состояний** (bot/main.py):
```python
ASK_NEW_EVENT = 30
```

4. **Добавление API endpoints** (web/app.py):
```python
@app.route("/api/new_event", methods=["POST"])
@login_required
def add_new_event():
    # Логика создания
    pass

@app.route("/api/new_event", methods=["GET"])
@login_required
def get_new_events():
    # Логика получения
    pass
```

5. **Обновление UI** (web/templates/dashboard.html):
```html
<div class="card action-card" onclick="showScreen('new-event-form')">
    <h3>Новое событие</h3>
    <p>Описание</p>
</div>
```

## 🔒 Безопасность

### Уязвимости и защита

| Угроза | Защита |
|--------|--------|
| SQL Injection | MongoDB использует BSON, не SQL |
| XSS | HTML-escape в Jinja2 шаблонах |
| CSRF | Flask session cookies (HTTPOnly) |
| Brute Force | Rate limiting (рекомендуется добавить) |
| Unauthorized Access | Whitelist для бота, аутентификация для веб |
| Session Hijacking | Secure cookies, HTTPS в продакшене |

### Рекомендации

1. **Не храните секреты в коде**:
   - Используйте `.env` для всех чувствительных данных
   - Добавьте `.env` в `.gitignore`

2. **Используйте HTTPS**:
   - Обязательно для продакшена
   - Let's Encrypt для бесплатных сертификатов

3. **Ограничьте доступ к MongoDB**:
   - Не открывайте порт 27017 наружу
   - Используйте сильные пароли
   - Включите MongoDB authentication

4. **Регулярно обновляйте зависимости**:
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

5. **Мониторинг логов**:
   - Отслеживайте неудачные попытки входа
   - Проверяйте необычную активность в БД

## 🧪 Тестирование

### Структура тестов (рекомендуется)

```
tests/
├── test_bot_handlers.py      # Тесты Telegram-бота
├── test_web_api.py            # Тесты API endpoints
├── test_db.py                 # Тесты работы с БД
└── conftest.py                # Фикстуры pytest
```

### Пример теста для API

```python
import pytest
from web.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login(client):
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    assert response.status_code == 302  # Redirect

def test_api_asthma_unauthorized(client):
    response = client.get('/api/asthma')
    assert response.status_code == 401
```

### Запуск тестов

```bash
# Установка pytest
pip install pytest pytest-cov

# Запуск всех тестов
pytest

# С покрытием кода
pytest --cov=bot --cov=web

# Конкретный файл
pytest tests/test_web_api.py
```

## 📊 Мониторинг и логирование

### Логи Docker

```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Последние 100 строк
docker-compose logs --tail=100

# Только ошибки
docker-compose logs | grep ERROR
```

### Python logging (рекомендуется добавить)

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Bot started")
logger.error("Failed to connect to database")
```

## 🔧 Устранение неполадок

### Проблема: Бот не отвечает

**Диагностика**:
```bash
docker-compose logs bot
```

**Возможные причины**:
1. Неверный TELEGRAM_BOT_TOKEN
2. Пользователь не в whitelist
3. MongoDB недоступна

**Решение**:
- Проверьте токен в .env
- Добавьте telegram_id в whitelist.txt
- Проверьте healthcheck: `docker-compose ps`

### Проблема: Веб-интерфейс недоступен

**Диагностика**:
```bash
docker-compose logs web
curl http://localhost:5001
```

**Возможные причины**:
1. Порт 5001 занят
2. Контейнер не запустился
3. MongoDB недоступна

**Решение**:
- Измените порт в docker-compose.yml
- Проверьте статус: `docker-compose ps`
- Перезапустите: `docker-compose restart web`

### Проблема: Данные не сохраняются

**Диагностика**:
```bash
docker exec -it cat-health-db mongosh -u admin -p password --authenticationDatabase admin
> use cat_health
> db.asthma_attacks.find().limit(5)
```

**Возможные причины**:
1. Неверные credentials MongoDB
2. База данных не создана
3. Проблемы с правами доступа

**Решение**:
- Проверьте MONGO_USER, MONGO_PASS в .env
- Создайте БД вручную через mongosh
- Проверьте логи MongoDB: `docker-compose logs db`

### Проблема: "Unauthorized" при запросах к API

**Причина**: Отсутствие или истекшая сессия

**Решение**:
1. Перелогиньтесь в веб-интерфейс
2. Проверьте настройку cookies в браузере
3. Убедитесь, что FLASK_SECRET_KEY не изменился

## 📈 Производительность

### Оптимизация MongoDB

**Индексы**:
```javascript
// Подключение к MongoDB
mongosh -u admin -p password --authenticationDatabase admin

use cat_health

// Создание индексов
db.asthma_attacks.createIndex({ user_id: 1, date_time: -1 })
db.defecations.createIndex({ user_id: 1, date_time: -1 })
db.weights.createIndex({ user_id: 1, date_time: -1 })
db.whitelist_users.createIndex({ telegram_id: 1 }, { unique: true })
```

**Ограничение результатов**:
- В коде уже установлен `limit(100)` для запросов
- Для больших датасетов рекомендуется пагинация

### Оптимизация Flask

**Production-сервер**:
```bash
# Gunicorn с 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app

# С настройкой таймаутов
gunicorn -w 4 --timeout 120 -b 0.0.0.0:5000 web.app:app
```

**Кеширование**:
- Рассмотрите использование Redis для кеширования сессий
- Flask-Caching для кеширования API-ответов

## 📚 Зависимости

### requirements.txt

```txt
python-telegram-bot==20.7
pymongo==4.6.1
flask==3.0.0
werkzeug==3.0.1
gunicorn==21.2.0  # Для продакшена
```

### Обновление зависимостей

```bash
# Проверка устаревших пакетов
pip list --outdated

# Обновление конкретного пакета
pip install --upgrade python-telegram-bot

# Обновление requirements.txt
pip freeze > requirements.txt
```

## 🌐 API Reference

### Authentication

Все API endpoints требуют аутентификации через Flask session.

**Login**: POST `/login`
**Logout**: GET `/logout`

### Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/asthma | Создать запись о приступе |
| GET | /api/asthma | Получить список приступов |
| PUT | /api/asthma/<id> | Обновить запись |
| DELETE | /api/asthma/<id> | Удалить запись |
| POST | /api/defecation | Создать запись о дефекации |
| GET | /api/defecation | Получить список дефекаций |
| PUT | /api/defecation/<id> | Обновить запись |
| DELETE | /api/defecation/<id> | Удалить запись |
| POST | /api/weight | Создать запись о весе |
| GET | /api/weight | Получить список измерений |
| PUT | /api/weight/<id> | Обновить запись |
| DELETE | /api/weight/<id> | Удалить запись |
| GET | /api/export/<type>/<format> | Экспортировать данные |

## 🤝 Вклад в проект

### Процесс разработки

1. **Fork** репозитория
2. Создайте **feature branch**: `git checkout -b feature/new-feature`
3. **Commit** изменений: `git commit -m 'Add new feature'`
4. **Push** в branch: `git push origin feature/new-feature`
5. Откройте **Pull Request**

### Code Style

- Следуйте PEP 8 для Python-кода
- Используйте black для форматирования: `black .`
- Проверяйте с помощью flake8: `flake8 .`
- Типизируйте функции (type hints)

### Документация

- Обновляйте документацию при добавлении функций
- Документируйте API endpoints в формате OpenAPI
- Добавляйте docstrings к функциям

## 📞 Поддержка

### Контакты

- **GitHub Issues**: для багов и feature requests
- **Discussions**: для вопросов и обсуждений
- **Email**: см. контакты в профиле автора

### Полезные ресурсы

- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Docker Documentation](https://docs.docker.com/)

---

**Версия документации**: 1.0  
**Дата обновления**: 2024  
**Авторы**: Команда разработки Cat Health Control Bot  
**Лицензия**: MIT
