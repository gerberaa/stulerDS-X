# 🤖 Telegram Bot для Моніторингу Discord Каналів

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Version](https://img.shields.io/badge/Version-v2.1.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot%20API-0088cc?logo=telegram)
![Discord](https://img.shields.io/badge/Discord-API-5865f2?logo=discord)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Security](https://img.shields.io/badge/Security-Password%20Protected-red?logo=security)
![Maintained](https://img.shields.io/badge/Maintained-Yes-green)

---

## 📋 Зміст

- [Огляд проекту](#-огляд-проекту)
- [Ключові особливості](#-ключові-особливості)
- [Архітектура системи](#-архітектура-системи)
- [Швидкий старт](#-швидкий-старт)
- [Детальна установка](#-детальна-установка)
- [Конфігурація](#-конфігурація)
- [Використання](#-використання)
- [API документація](#-api-документація)
- [Структура проекту](#-структура-проекту)
- [Безпека](#-безпека)
- [Моніторинг та діагностика](#-моніторинг-та-діагностика)
- [Розгортання](#-розгортання)
- [Тестування](#-тестування)
- [Усунення несправностей](#-усунення-несправностей)
- [Внесок в розробку](#-внесок-в-розробку)
- [Ліцензія](#-ліцензія)
- [Подяки](#-подяки)

---

## 🎯 Огляд проекту

**Telegram Bot для Моніторингу Discord** — це потужне рішення для автоматичного відстеження активності в Discord каналах з миттєвими сповіщеннями через Telegram. Бот забезпечує безперебійний моніторинг, безпечну авторизацію та детальну діагностику системи.

### Чому обрати цей бот?

- ⚡ **Миттєві сповіщення**: Отримуйте повідомлення з Discord каналів в реальному часі
- 🔒 **Безпека**: Багаторівнева система захисту з паролями та сесіями
- 📊 **Діагностика**: Комплексна система моніторингу стану бота
- 🛠️ **Легка настройка**: Інтуїтивний інтерфейс з кнопками
- 🔄 **Автоматизація**: Повністю автономна робота без втручання користувача

---

## ✨ Ключові особливості

### 🔐 Система безпеки
- **Авторизація по паролю** з автоматичним закінченням сесії
- **Тайм-аути сесій** (5 хвилин неактивності)
- **Захищені токени** з шифруванням в змінних середовища
- **Аудит дій** користувачів

### 📱 Інтерфейс користувача
- **Інтуїтивне меню** з кнопками для всіх дій
- **Покрокові майстри** для додавання проектів
- **Контекстна допомога** та підказки
- **Багатомовна підтримка** (українська/англійська)

### 📢 Моніторинг Discord
- **Реальний час**: Відстеження нових повідомлень кожні 15 секунд
- **Rate Limiting**: Дотримання лімітів Discord API
- **Розумні запити**: Випадкові затримки для природної поведінки
- **Фільтрація**: Відстеження тільки людських повідомлень

### 🔧 Діагностика та моніторинг
- **Комплексна діагностика** стану всіх компонентів
- **API тестування**: Перевірка підключення до Discord
- **Статистика роботи**: Кількість повідомлень, помилок, час роботи
- **Логування подій**: Детальні логи для налагодження

### ⚡ Оптимізація продуктивності
- **Кешування даних**: Зберігання кожні 30 секунд
- **Оптимізовані запити**: Мінімальне навантаження на API
- **Автоочищення**: Видалення старих даних
- **Асинхронна обробка**: Не блокуючі операції

---

## 🏗️ Архітектура системи

### Огляд компонентів

Система складається з модульних компонентів, кожен з яких відповідає за конкретну функціональність:

| Компонент | Відповідальність | Технології |
|-----------|------------------|-------------|
| **Bot Core** | Основна логіка, обробка команд | Python, aiogram |
| **Security Manager** | Авторизація, сесії | Bcrypt, JWT |
| **Project Manager** | CRUD проектів, збереження | JSON, File I/O |
| **Discord Monitor** | Моніторинг каналів | Discord API, aiohttp |
| **Telegram Forwarder** | Пересилання повідомлень | Telegram Bot API |

### Потік даних

```
Користувач → Telegram Bot API → Security Check → Project Manager → Discord Monitor → Telegram Channel
                                      ↓
                                Data Storage (JSON)
```

---

## 🚀 Швидкий старт

### Передумови

Перед початком роботи переконайтесь, що у вас встановлено:

- **Python 3.8+** ([завантажити](https://python.org))
- **Git** ([завантажити](https://git-scm.com))
- **Telegram акаунт** для створення бота
- **Discord акаунт** для отримання токенів

### Експрес-установка

```bash
# 1. Клонування репозиторію
git clone https://github.com/username/telegram-discord-monitor.git
cd telegram-discord-monitor

# 2. Встановлення залежностей
pip install -r requirements.txt

# 3. Конфігурація (скопіюйте .env.example в .env)
cp .env.example .env

# 4. Запуск
python bot.py
```

**Важливо**: Не забудьте налаштувати змінні в `.env` файлі!

---

## 📦 Детальна установка

### 1. Клонування та налаштування середовища

```bash
# Клонування репозиторію
git clone https://github.com/gerberaa/stulerDS-X/
cd stulerDS-X

# Створення віртуального середовища (рекомендовано)
python -m venv stulerDS-X

# Активація віртуального середовища
# Windows:
telegram-bot-env\Scripts\activate
# Linux/Mac:
source stulerDS-X-env/bin/activate

# Оновлення pip
python -m pip install --upgrade pip
```

### 2. Встановлення залежностей

```bash
# Основні залежності
pip install -r requirements.txt

# Або окремо:
pip install aiogram aiohttp asyncio python-dotenv bcrypt
```

### 3. Налаштування Telegram бота

1. Відкрийте [@BotFather](https://t.me/botfather) в Telegram
2. Надішліть `/newbot`
3. Введіть ім'я бота (наприклад, "Discord Monitor Bot")
4. Введіть username (наприклад, "discord_monitor_bot")
5. Збережіть отриманий токен

### 4. Отримання Discord токену

#### Метод 1: Через Developer Tools
1. Відкрийте Discord в браузері
2. Натисніть `F12` (Developer Tools)
3. Перейдіть на вкладку `Network`
4. Відправте повідомлення в Discord
5. Знайдіть запит до `messages`
6. Скопіюйте значення `Authorization` з заголовків

#### Метод 2: Через додаток
1. Відкрийте Discord додаток
2. Натисніть `Ctrl+Shift+I` (Developer Tools)
3. В консолі виконайте:
   ```javascript
   (webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
   ```

---

## ⚙️ Конфігурація

### Змінні середовища (.env)

Створіть файл `.env` в кореневій папці:

```env
# Telegram Bot Configuration
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789
ADMIN_PASSWORD=ваш_безпечний_пароль

# Discord Configuration  
AUTHORIZATION=ваш_discord_токен_авторизації

# Optional: Advanced Settings
SESSION_TIMEOUT=300          # Час сесії в секундах (за замовчанням: 300)
MONITOR_INTERVAL=15          # Інтервал моніторингу в секундах
MAX_RETRIES=3               # Максимум повторних спроб
LOG_LEVEL=INFO              # Рівень логування: DEBUG, INFO, WARNING, ERROR
CACHE_INTERVAL=30           # Інтервал збереження кешу в секундах

# Database Configuration
DATA_FILE=data.json         # Шлях до файлу бази даних
BACKUP_INTERVAL=3600        # Інтервал резервного копіювання в секундах
```

### Налаштування логування

Створіть файл `logging.conf`:

```ini
[loggers]
keys=root,bot,security,discord

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_bot]
level=INFO
handlers=consoleHandler,fileHandler
qualname=bot
propagate=0

[logger_security]
level=WARNING
handlers=fileHandler
qualname=security
propagate=0

[logger_discord]
level=INFO
handlers=fileHandler
qualname=discord
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=detailedFormatter
args=('bot.log', 'a')

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s
```

---

## 🎮 Використання

### Перший запуск

1. **Запустіть бота**:
   ```bash
   python bot.py
   ```

2. **Знайдіть бота в Telegram** за username та надішліть `/start`

3. **Авторизуйтесь** паролем, який ви встановили в `.env`

### Основні команди

| Команда | Опис | Приклад |
|---------|------|---------|
| `/start` | Запуск бота та відображення меню | `/start` |
| `/help` | Довідка по командам | `/help` |
| `/status` | Статус бота та системи | `/status` |
| `/logout` | Вихід з поточної сесії | `/logout` |
| `/version` | Версія бота | `/version` |

### Інтерфейс з кнопками

#### Головне меню
- **➕ Додати проект** - Додавання Discord каналу для моніторингу
- **📜 Історія Discord** - Перегляд останніх повідомлень
- **📢 Налаштування пересилання** - Налаштування каналу для сповіщень
- **🔧 Діагностика** - Перевірка системи
- **📊 Статистика** - Показники роботи бота

#### Додавання Discord проекту

1. Натисніть **"➕ Додати проект"**
2. Оберіть **"Discord"**
3. Введіть назву проекту
4. Вставте посилання на канал:
   ```
   https://discord.com/channels/SERVER_ID/CHANNEL_ID
   ```

#### Налаштування пересилання

1. Натисніть **"📢 Налаштування пересилання"**
2. Введіть ID каналу або username:
   - `@channel_username`
   - `-1001234567890`
   - `channel_username`

### Автоматичні функції

- **Моніторинг**: Автоматична перевірка нових повідомлень кожні 15 секунд
- **Пересилання**: Миттєве відправлення нових повідомлень в налаштований канал
- **Збереження**: Автоматичне збереження даних кожні 30 секунд
- **Очищення**: Видалення старих даних для оптимізації

---

## 📚 API документація

### Внутрішній API

#### SecurityManager

```python
class SecurityManager:
    def authenticate(user_id: int, password: str) -> bool:
        """Авторизація користувача"""
        
    def is_authorized(user_id: int) -> bool:
        """Перевірка авторизації"""
        
    def create_session(user_id: int) -> str:
        """Створення нової сесії"""
        
    def invalidate_session(user_id: int) -> None:
        """Закінчення сесії"""
```

#### ProjectManager

```python
class ProjectManager:
    def add_discord_project(name: str, channel_url: str) -> dict:
        """Додавання Discord проекту"""
        
    def get_projects() -> list:
        """Отримання списку проектів"""
        
    def remove_project(project_id: str) -> bool:
        """Видалення проекту"""
        
    def update_project(project_id: str, data: dict) -> bool:
        """Оновлення проекту"""
```

#### DiscordMonitor

```python
class DiscordMonitor:
    async def fetch_messages(channel_id: str, last_message_id: str) -> list:
        """Отримання нових повідомлень"""
        
    async def start_monitoring() -> None:
        """Запуск моніторингу"""
        
    async def stop_monitoring() -> None:
        """Зупинка моніторингу"""
```

### REST API Endpoints

Бот також надає REST API для інтеграції з зовнішніми системами:

```
GET /api/v1/status - Статус системи
POST /api/v1/projects - Додавання проекту
GET /api/v1/projects - Список проектів
DELETE /api/v1/projects/{id} - Видалення проекту
GET /api/v1/stats - Статистика
```

---

## 📁 Структура проекту

```
telegram-discord-monitor/
├── 📄 bot.py                     # Основний файл бота
├── 📄 config.py                  # Конфігурація та константи
├── 📄 security_manager.py        # Менеджер безпеки
├── 📄 project_manager.py         # Менеджер проектів
├── 📄 discord_monitor.py         # Моніторинг Discord
├── 📄 requirements.txt           # Python залежності
├── 📄 .env                       # Змінні середовища
├── 📄 .gitignore                 # Git ignore правила
├── 📄 README.md                  # Документація проекту
├── 📄 LICENSE                    # Ліцензія
├── 📁 docs/                      # Додаткова документація
│   ├── 📄 api.md                 # API документація
│   ├── 📄 deployment.md          # Розгортання
│   └── 📄 troubleshooting.md     # Усунення несправностей
├── 📁 tests/                     # Тести
│   ├── 📄 test_bot.py
│   ├── 📄 test_security.py
│   └── 📄 test_discord.py
├── 📁 scripts/                   # Допоміжні скрипти
│   ├── 📄 setup.sh               # Автоматичне налаштування
│   ├── 📄 deploy.sh              # Скрипт розгортання
│   └── 📄 backup.sh              # Резервне копіювання
├── 📁 assets/                    # Статичні ресурси
│   ├── 📁 screenshots/           # Скріншоти
│   ├── 📁 diagrams/              # Діаграми
│   └── 📁 icons/                 # Іконки
└── 📄 data.json                  # База даних (автоматично)
```

---

## 🔒 Безпека

### Рівні захисту

1. **Авторизація по паролю**
   - Хешування паролів з bcrypt
   - Захист від брутфорс атак
   - Обмеження спроб входу

2. **Управління сесіями**
   - JWT токени для сесій
   - Автоматичне закінчення сесій
   - Відстеження активності користувачів

3. **Захист API**
   - Rate limiting для запитів
   - Валідація вхідних даних
   - Санітизація повідомлень

4. **Безпека даних**
   - Шифрування чутливих даних
   - Безпечне зберігання токенів
   - Регулярне резервне копіювання

### Рекомендації з безпеки

- ✅ Використовуйте складні паролі (мінімум 12 символів)
- ✅ Регулярно змінюйте Discord токени
- ✅ Не публікуйте .env файл в репозиторії
- ✅ Використовуйте HTTPS для всіх зовнішніх запитів
- ✅ Регулярно оновлюйте залежності
- ❌ Не діліться токенами та паролями
- ❌ Не запускайте бота з правами адміністратора

---

## 📈 Моніторинг та діагностика

### Діагностичні інструменти

#### 1. Статус системи
```
🤖 Bot Status: ✅ Online
🔐 Security: ✅ Active  
📊 Projects: 3 active
💾 Database: ✅ Connected
🌐 API Status: ✅ All services operational
```

#### 2. Тестування каналів
```
Discord Channel Test Results:
📺 #general: ✅ Accessible (125 messages)
📺 #announcements: ✅ Accessible (15 messages)  
📺 #development: ❌ Access denied
```

#### 3. API тестування
```
API Connectivity Test:
Discord API: ✅ 200ms response time
Telegram API: ✅ 150ms response time
Rate Limits: ✅ Within normal range (45% used)
```

#### 4. Статистика роботи
```
📊 Performance Statistics:
Messages processed: 1,247
Successful forwards: 1,241 (99.5%)
Failed forwards: 6 (0.5%)
Uptime: 15d 7h 23m
Average response time: 180ms
```

### Логування

#### Рівні логів
- **DEBUG**: Детальна інформація для налагодження
- **INFO**: Загальна інформація про роботу
- **WARNING**: Попередження про потенційні проблеми  
- **ERROR**: Критичні помилки
- **CRITICAL**: Критичні помилки що зупиняють роботу

#### Структура логів
```
2024-09-12 15:30:45 - bot - INFO - Bot started successfully
2024-09-12 15:30:46 - security - INFO - User 123456789 authenticated
2024-09-12 15:30:50 - discord - INFO - Monitoring started for 3 channels
2024-09-12 15:31:05 - discord - INFO - New message forwarded to -1003096179237
```

---

## 🚀 Розгортання

### Локальне розгортання

```bash
# 1. Активація середовища
source telegram-bot-env/bin/activate

# 2. Встановлення в режимі розробки
pip install -e .

# 3. Запуск з логуванням
python bot.py --log-level DEBUG
```

### Docker розгортання

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копіювання та встановлення Python залежностей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіювання коду програми
COPY . .

# Створення папки для даних
RUN mkdir -p /app/data

# Встановлення змінних середовища
ENV PYTHONPATH=/app
ENV DATA_FILE=/app/data/data.json

EXPOSE 8080

# Запуск бота
CMD ["python", "bot.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    container_name: discord-monitor-bot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_PASSWORD=${ADMIN_PASSWORD}
      - AUTHORIZATION=${AUTHORIZATION}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    ports:
      - "8080:8080"
    networks:
      - bot-network

  # Опціонально: Redis для кешування
  redis:
    image: redis:7-alpine
    container_name: discord-monitor-redis
    restart: unless-stopped
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
```

### Команди Docker

```bash
# Збірка та запуск
docker-compose up -d --build

# Перегляд логів
docker-compose logs -f telegram-bot

# Зупинка
docker-compose down

# Повне перезавантаження
docker-compose down && docker-compose up -d --build
```

### Хмарне розгортання

#### Heroku
```bash
# 1. Створення додатку
heroku create discord-monitor-bot

# 2. Налаштування змінних
heroku config:set BOT_TOKEN=your_token
heroku config:set ADMIN_PASSWORD=your_password
heroku config:set AUTHORIZATION=your_discord_token

# 3. Розгортання
git push heroku main
```

#### DigitalOcean/AWS/Azure
1. Створіть віртуальну машину
2. Встановіть Docker та docker-compose
3. Клонуйте репозиторій
4. Налаштуйте змінні середовища
5. Запустіть через docker-compose

---

## 🧪 Тестування

### Структура тестів

```
tests/
├── unit/                 # Модульні тести
│   ├── test_security.py
│   ├── test_project_manager.py
│   └── test_discord_monitor.py
├── integration/          # Інтеграційні тести
│   ├── test_bot_flows.py
│   └── test_api_integration.py
└── e2e/                 # End-to-end тести
    ├── test_full_workflow.py
    └── test_monitoring_cycle.py
```

### Запуск тестів

```bash
# Усі тести
pytest

# Конкретна категорія
pytest tests/unit/

# З покриттям коду
pytest --cov=. --cov-report=html

# Конкретний тест
pytest tests/unit/test_security.py::TestSecurityManager::test_authentication
```

### Приклад тесту

```python
import pytest
from security_manager import SecurityManager

class TestSecurityManager:
    def setup_method(self):
        self.security = SecurityManager()
    
    def test_authentication_success(self):
        # Тест успішної авторизації
        user_id = 123456789
        password = "test_password"
        
        # Реєстрація користувача
        self.security.register_user(user_id, password)
        
        # Перевірка авторизації
        assert self.security.authenticate(user_id, password) == True
    
    def test_session_expiration(self):
        # Тест закінчення сесії
        user_id = 123456789
        session = self.security.create_session(user_id)
        
        # Симуляція часу
        import time
        time.sleep(301)  # 5+ хвилин
        
        assert self.security.is_session_valid(session) == False
```

### Тестові дані

Створіть файл `tests/fixtures/test_data.json`:

```json
{
  "users": [
    {
      "id": 123456789,
      "password_hash": "$2b$12$example_hash",
      "permissions": ["admin"]
    }
  ],
  "projects": [
    {
      "id": "test_project_1",
      "name": "Test Discord Channel",
      "type": "discord",
      "channel_id": "1234567890123456789",
      "last_message_id": "1234567890123456790"
    }
  ]
}
```

---

## 🛠️ Усунення несправностей

### Поширені проблеми та рішення

#### 1. Бот не запускається

**Симптоми**: 
- Помилка при запуску
- Бот не відповідає на команди

**Рішення**:
```bash
# Перевірка залежностей
pip install --upgrade -r requirements.txt

# Перевірка змінних середовища
python -c "import os; print('BOT_TOKEN:', bool(os.getenv('BOT_TOKEN')))"

# Перевірка токену
curl -X GET "https://api.telegram.org/bot${BOT_TOKEN}/getMe"
```

#### 2. Discord токен не працює

**Симптоми**:
- 401 Unauthorized помилки
- Не можливо отримати повідомлення з каналів

**Рішення**:
1. Отримайте новий токен через Developer Tools
2. Перевірте правильність токену:
```bash
curl -H "Authorization: YOUR_TOKEN" "https://discord.com/api/v9/users/@me"
```
3. Переконайтеся що маєте доступ до каналу

#### 3. Повідомлення не пересилаються

**Симптоми**:
- Бот отримує повідомлення але не пересилає
- Помилки при відправці в Telegram

**Рішення**:
1. Перевірте права бота в Telegram каналі
2. Перевірте ID каналу:
```bash
# Отримання оновлень бота
curl -X GET "https://api.telegram.org/bot${BOT_TOKEN}/getUpdates"
```
3. Перевірте налаштування пересилання в боті

#### 4. Висока навантаженість CPU/RAM

**Симптоми**:
- Повільна робота бота
- Високе використання ресурсів

**Рішення**:
```bash
# Зменшення інтервалу моніторингу
export MONITOR_INTERVAL=30

# Обмеження кількості проектів
# Видаліть неактивні проекти через бота

# Очищення логів
truncate -s 0 bot.log
```

### Діагностичні команди

```bash
# Перевірка статусу процесу
ps aux | grep python

# Перевірка використання портів
netstat -tlnp | grep python

# Перевірка логів
tail -f bot.log

# Перевірка дискового простору
df -h

# Перевірка пам'яті
free -h
```

### Відновлення після збоїв

#### Автоматичне відновлення
```bash
#!/bin/bash
# restart_bot.sh

while true; do
    python bot.py
    echo "Bot crashed with exit code $?. Respawning.." >&2
    sleep 5
done
```

#### Systemd сервіс
```ini
[Unit]
Description=Telegram Discord Monitor Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/telegram-discord-monitor
ExecStart=/home/botuser/telegram-bot-env/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## 🤝 Внесок в розробку

Ми вітаємо внески в розвиток проекту! Ось як ви можете долучитися:

### Процес внеску

1. **Fork** репозиторію
2. Створіть **feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit** зміни: `git commit -m 'Add amazing feature'`
4. **Push** в branch: `git push origin feature/amazing-feature`
5. Відкрийте **Pull Request**

### Стандарти коду

#### Python стиль
- Використовуйте **PEP 8** стандарт
- Максимальна довжина рядка: **88 символів**
- Використовуйте **type hints**
- Документуйте функції з **docstrings**

#### Приклад коду
```python
async def process_discord_message(
    channel_id: str, 
    message_data: dict
) -> Optional[str]:
    """
    Обробляє повідомлення з Discord каналу.
    
    Args:
        channel_id: ID Discord каналу
        message_data: Дані повідомлення з Discord API
    
    Returns:
        ID обробленого повідомлення або None при помилці
        
    Raises:
        DiscordAPIError: При помилках Discord API
    """
    try:
        # Валідація даних
        if not message_data.get('content'):
            return None
            
        # Обробка повідомлення
        formatted_message = format_discord_message(message_data)
        await send_to_telegram(formatted_message)
        
        return message_data['id']
        
    except Exception as e:
        logger.error(f"Помилка обробки повідомлення: {e}")
        return None
```

### Тестування змін

```bash
# Перед commit завжди запускайте:
pytest                    # Всі тести
black .                   # Форматування коду  
flake8 .                  # Лінтинг
mypy .                    # Перевірка типів
```

### Документація

- Оновлюйте README при додаванні функцій
- Додавайте docstrings до нових функцій
- Створюйте приклади використання
- Оновлюйте API документацію

### Повідомлення про помилки

При повідомленні про помилку включіть:

1. **Опис проблеми**: Що сталося?
2. **Кроки відтворення**: Як відтворити помилку?
3. **Очікуваний результат**: Що повинно було статися?
4. **Фактичний результат**: Що сталося насправді?
5. **Середовище**: ОС, Python версія, залежності
6. **Логи**: Релевантні логи та трейси

### Пропозиції функцій

Перед реалізацією нової функції:

1. Створіть **Issue** з описом функції
2. Обговоріть технічні деталі
3. Отримайте схвалення від maintainer'ів
4. Реалізуйте функцію в окремому branch

---

## 📄 Ліцензія

Цей проект ліцензується під **MIT License** - дивіться файл [LICENSE](LICENSE) для деталей.

```
MIT License

Copyright (c) 2024 Discord Monitor Bot Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Подяки

### Основні розробники
- **@username** - Ідея та архітектура проекту
- **@contributor1** - Система безпеки та авторизації
- **@contributor2** - Discord API інтеграція
- **@contributor3** - Telegram Bot UI/UX

### Бібліотеки та інструменти

Величезна подяка авторам цих проектів:

- **[aiogram](https://github.com/aiogram/aiogram)** - Telegram Bot фреймворк
- **[aiohttp](https://github.com/aio-libs/aiohttp)** - HTTP клієнт/сервер
- **[python-dotenv](https://github.com/theskumar/python-dotenv)** - Завантаження змінних середовища
- **[bcrypt](https://github.com/pyca/bcrypt/)** - Хешування паролів

### Спільнота

Подяка всім користувачам, які:
- 🐛 Повідомили про помилки
- 💡 Запропонували покращення
- 📖 Покращили документацію
- ⭐ Поставили зірочку проекту

---

## 📞 Підтримка та контакти

### Отримання допомоги

- 📚 **Документація**: Перевірте цей README та файли в папці `docs/`
- 🐛 **Баг репорти**: Створіть [Issue](https://github.com/username/repo/issues)
- 💬 **Питання**: Використайте [Discussions](https://github.com/username/repo/discussions)
- 📧 **Email**: support@example.com (тільки для критичних проблем)

### Соціальні мережі

- 🐦 **Twitter**: [@discordmonitorbot](https://twitter.com/discordmonitorbot)
- 💬 **Telegram**: [@discord_monitor_chat](https://t.me/discord_monitor_chat)
- 💻 **GitHub**: [Репозиторій проекту](https://github.com/username/telegram-discord-monitor)

### Статистика проекту

![GitHub stars](https://img.shields.io/github/stars/username/telegram-discord-monitor?style=social)
![GitHub forks](https://img.shields.io/github/forks/username/telegram-discord-monitor?style=social)
![GitHub issues](https://img.shields.io/github/issues/username/telegram-discord-monitor)
![GitHub pull requests](https://img.shields.io/github/issues-pr/username/telegram-discord-monitor)
![GitHub contributors](https://img.shields.io/github/contributors/username/telegram-discord-monitor)

---

<div align="center">
  
**Зроблено з ❤️ українською спільнотою розробників**

*Якщо цей проект допоміг вам, поставте ⭐ зірочку!*

[⬆️ Повернутися до змісту](#-зміст)

</div>
