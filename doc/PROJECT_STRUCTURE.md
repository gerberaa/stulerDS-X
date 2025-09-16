# 📁 Структура проекту

## 🎯 Основна ідея

Проект організований для максимальної зручності та чистоти:

- **🤖 Основні файли** - в корені проекту
- **📚 Документація** - в папці `doc/`
- **🧪 Тести** - в папці `test/`
- **🏗️ Збірка** - в папках `build/`, `dist/`

## 📂 Коренева папка

### 🤖 Основні файли бота
- `bot.py` - Головний файл бота
- `config.py` - Конфігурація
- `requirements.txt` - Залежності Python
- `run.bat` - Скрипт запуску (Windows)

### 🔧 Модулі моніторингу
- `twitter_monitor.py` - Twitter/X моніторинг
- `discord_monitor.py` - Discord моніторинг
- `selenium_twitter_monitor.py` - Selenium Twitter моніторинг
- `project_manager.py` - Менеджер проектів

### 🔐 Система доступу
- `access_manager.py` - Менеджер авторизації
- `access_data.json` - Дані користувачів
- `setup_admin.py` - Налаштування адміністратора
- `security_manager.py` - Менеджер безпеки

### 📊 Дані
- `data.json` - Основні дані проекту
- `browser_profile/` - Профілі браузера

### 🏗️ Компіляція
- `build.py` - Скрипт компіляції
- `build.bat` - Windows build script
- `build.sh` - Linux build script
- `quick_build.py` - Швидка компіляція
- `build_requirements.txt` - Залежності для компіляції
- `telegram_monitor_bot.spec` - PyInstaller spec

## 📚 Папка doc/

Вся документація проекту:

- `ACCESS_MANAGEMENT_GUIDE.md` - Керівництво по авторизації
- `IMAGE_SUPPORT_GUIDE.md` - Підтримка зображень
- `PROJECT_MANAGER_INTERFACE.md` - Інтерфейс менеджера проектів
- `SELENIUM_AUTO_START_GUIDE.md` - Автозапуск Selenium
- `SELENIUM_PERSISTENT_ACCOUNTS_GUIDE.md` - Збереження акаунтів
- `SELENIUM_TWITTER_GUIDE.md` - Selenium Twitter моніторинг
- `TWITTER_IMAGE_EXTRACTION_GUIDE.md` - Витягування зображень
- `TWITTER_IMAGE_PARAMETERS_GUIDE.md` - Параметри зображень
- `BUILD_INSTRUCTIONS.md` - Інструкції збірки
- `COMPILATION_README.md` - Швидкий старт компіляції
- `TWITTER_IMPROVEMENTS_SUMMARY.md` - Покращення Twitter

## 🧪 Папка test/

Всі тести та допоміжні скрипти:

### Тести
- `test_selenium.py` - Тести Selenium
- `test_image_functionality.py` - Тести зображень
- `test_message_formatting.py` - Тести форматування
- `test_selenium_integration.py` - Тести інтеграції
- `test_bot_twitter.py` - Тести бота Twitter
- `test_html_parsing.py` - Тести HTML парсингу
- `test_twitter.py` - Тести Twitter API

### Допоміжні скрипти
- `install_selenium.py` - Встановлення Selenium
- `monitor_pilk_xz*.py` - Тестові монітори
- `twitter_*.py` - Тести Twitter API
- `TWITTER_ENDPOINTS_REPORT.md` - Звіт по ендпоінтам

## 🏗️ Папки збірки

- `build/` - Проміжні файли збірки
- `dist/` - Готові виконувані файли
- `dist_package/` - Пакунок для розповсюдження

## 🎯 Переваги такої структури

### ✅ Чистота
- Коренева папка містить тільки основні файли
- Документація не засмічує основний код
- Тести відокремлені від продакшн коду

### ✅ Організованість
- Легко знайти потрібний файл
- Логічне групування по функціональності
- Зрозуміла структура для нових розробників

### ✅ Зручність
- Швидкий доступ до основних файлів
- Документація в одному місці
- Тести не заважають основній роботі

### ✅ Масштабованість
- Легко додавати нові модулі
- Просто розширювати документацію
- Зручно додавати нові тести

## 🚀 Використання

### Запуск бота
```bash
python bot.py
```

### Читання документації
```bash
# Відкрийте файли в папці doc/
cat doc/ACCESS_MANAGEMENT_GUIDE.md
cat doc/SELENIUM_AUTO_START_GUIDE.md
```

### Запуск тестів
```bash
python test/test_selenium.py
python test/test_image_functionality.py
```

### Компіляція
```bash
python quick_build.py
```

## 📝 Примітки

- **Не змінюйте** структуру основних файлів без потреби
- **Додавайте** нову документацію в `doc/`
- **Розміщуйте** нові тести в `test/`
- **Зберігайте** чистоти кореневої папки

Така структура забезпечує максимальну зручність роботи з проектом! 🎯