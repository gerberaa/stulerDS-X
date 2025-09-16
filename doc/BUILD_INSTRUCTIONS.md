# 🚀 Інструкція з компіляції Telegram Monitor Bot

## Опис
Цей проект містить скрипти для компіляції Telegram Monitor Bot в один виконуваний файл, який можна запускати на Windows та Linux без встановлення Python та залежностей.

## 📋 Передумови

### Windows
- Python 3.8+ (завантажити з [python.org](https://python.org))
- pip (зазвичай встановлюється разом з Python)

### Linux
- Python 3.8+
- pip3
- Для Ubuntu/Debian: `sudo apt install python3 python3-pip`
- Для CentOS/RHEL: `sudo yum install python3 python3-pip`

## 🔨 Компіляція

### Windows
1. Відкрийте командний рядок в папці проекту
2. Запустіть: `build.bat`
3. Дочекайтеся завершення компіляції

### Linux
1. Відкрийте термінал в папці проекту
2. Запустіть: `./build.sh`
3. Дочекайтеся завершення компіляції

## 📁 Результат компіляції

Після успішної компіляції створиться папка `dist_package/` з наступною структурою:

```
dist_package/
├── telegram_monitor_bot.exe (Windows) або telegram_monitor_bot (Linux)
├── data.json
├── projects.json
├── browser_profile/
├── .env.example
├── run.bat (Windows) або run.sh (Linux)
├── README.md
└── *.md (документація)
```

## 🚀 Запуск готового проекту

### Windows
1. Перейдіть в папку `dist_package/`
2. Скопіюйте `.env.example` в `.env`
3. Налаштуйте параметри в `.env` файлі
4. Запустіть `run.bat`

### Linux
1. Перейдіть в папку `dist_package/`
2. Скопіюйте `.env.example` в `.env`
3. Налаштуйте параметри в `.env` файлі
4. Запустіть `./run.sh`

## ⚙️ Налаштування .env файлу

### Обов'язкові параметри:
```env
BOT_TOKEN=your_bot_token_here
ADMIN_PASSWORD=401483
```

### Опціональні параметри:
```env
# Discord моніторинг
AUTHORIZATION=your_discord_authorization_token

# Twitter/X моніторинг
TWITTER_AUTH_TOKEN=your_twitter_auth_token
TWITTER_CSRF_TOKEN=your_twitter_csrf_token
```

## 📦 Що включає компіляція

### Файли проекту:
- ✅ `bot.py` - основний файл бота
- ✅ `config.py` - конфігурація
- ✅ `security_manager.py` - менеджер безпеки
- ✅ `project_manager.py` - менеджер проектів
- ✅ `discord_monitor.py` - моніторинг Discord
- ✅ `twitter_monitor.py` - моніторинг Twitter
- ✅ `selenium_twitter_monitor.py` - Selenium моніторинг Twitter
- ✅ `data.json` - база даних
- ✅ `projects.json` - конфігурація проектів
- ✅ `browser_profile/` - профіль браузера

### Залежності:
- ✅ `python-telegram-bot` - Telegram API
- ✅ `aiohttp` - HTTP клієнт
- ✅ `requests` - HTTP запити
- ✅ `selenium` - автоматизація браузера
- ✅ `python-dotenv` - робота з .env файлами

## 🏗️ Архітектура проекту

Проект зберігає всю архітектуру:

### База даних:
- `data.json` - зберігає користувачів, проекти, налаштування пересилання
- `projects.json` - конфігурація проектів моніторингу

### Профіль браузера:
- `browser_profile/` - повний профіль Chrome для Selenium
- Зберігає cookies, сесії, налаштування браузера

### Документація:
- `README.md` - основна документація
- `ACCOUNT_MANAGER_GUIDE.md` - керівництво по менеджеру акаунтів
- `SELENIUM_TWITTER_GUIDE.md` - керівництво по Selenium Twitter
- `TWITTER_IMPROVEMENTS_SUMMARY.md` - покращення Twitter

## 🔧 Технічні деталі

### PyInstaller конфігурація:
- Використовується `.spec` файл для точного контролю
- Всі залежності включаються автоматично
- Створюється один виконуваний файл
- Підтримується UPX стиснення

### Підтримувані платформи:
- ✅ Windows 10/11 (x64)
- ✅ Linux (x64) - Ubuntu, CentOS, RHEL, Debian
- ✅ macOS (теоретично, але не тестувалося)

## 🐛 Вирішення проблем

### Помилка "Python не знайдено":
- Windows: Встановіть Python з [python.org](https://python.org)
- Linux: `sudo apt install python3 python3-pip`

### Помилка "PyInstaller не встановлений":
- Скрипт автоматично встановить PyInstaller
- Якщо не вдається: `pip install pyinstaller`

### Помилка компіляції:
- Перевірте чи всі файли проекту на місці
- Переконайтеся що немає синтаксичних помилок в Python коді
- Спробуйте запустити `python bot.py` для перевірки

### Помилка запуску:
- Перевірте налаштування в `.env` файлі
- Переконайтеся що `BOT_TOKEN` правильний
- Перевірте права доступу до файлів

## 📞 Підтримка

При виникненні проблем:
1. Перевірте налаштування в `.env` файлі
2. Переконайтеся що всі файли проекту на місці
3. Перевірте права доступу до файлів
4. Переконайтеся що є інтернет-з'єднання

## 📝 Версія
- Версія проекту: 1.0
- Дата створення інструкції: 2025
- Підтримувані ОС: Windows 10/11, Linux x64