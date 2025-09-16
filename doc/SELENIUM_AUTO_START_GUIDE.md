# 🚀 Автоматичний запуск Selenium Twitter моніторингу

## 📋 Огляд

Selenium Twitter моніторинг тепер автоматично запускається разом з ботом! Не потрібно запускати його вручну через команди.

## 🔄 Як це працює

### 🚀 Автозапуск при старті бота

При запуску бота (`python bot.py`) автоматично:

1. **Ініціалізується** Selenium Twitter монітор
2. **Завантажуються** збережені акаунти з бази даних
3. **Запускається** моніторинг в окремому потоці
4. **Логується** статус запуску

### 📊 Логи автозапуску

```
2025-09-13 17:09:18,296 - __main__ - INFO - Бот запускається...
2025-09-13 17:09:18,297 - __main__ - INFO - Discord моніторинг запущено
2025-09-13 17:09:18,298 - __main__ - INFO - Twitter моніторинг запущено
2025-09-13 17:09:18,299 - __main__ - INFO - Завантажено 1 збережених Selenium акаунтів: ['pilk_xz']
2025-09-13 17:09:18,300 - __main__ - INFO - ✅ Selenium Twitter моніторинг готовий з 1 акаунтами
2025-09-13 17:09:18,301 - __main__ - INFO - 🚀 Selenium Twitter моніторинг автоматично запущено
```

## 🎯 Переваги автозапуску

### ✅ Зручність
- **Без ручного запуску** - моніторинг стартує автоматично
- **Без команд** - не потрібно викликати `/selenium_start`
- **Без налаштувань** - все працює "з коробки"

### ✅ Надійність
- **Автоматичне відновлення** - моніторинг перезапускається з ботом
- **Збереження стану** - акаунти зберігаються між перезапусками
- **Обробка помилок** - автоматичне відновлення при збоях

### ✅ Ефективність
- **Один процес** - все в одному додатку
- **Синхронізація** - моніторинг працює разом з іншими сервісами
- **Ресурсосбереження** - оптимізоване використання пам'яті

## 🔧 Технічні деталі

### 📁 Структура автозапуску

```python
def main() -> None:
    # ... ініціалізація бота ...
    
    # Автоматично запускаємо Selenium Twitter моніторинг
    global selenium_twitter_monitor
    selenium_twitter_monitor = SeleniumTwitterMonitor()
    
    # Завантажуємо збережені акаунти
    saved_accounts = project_manager.get_selenium_accounts()
    if saved_accounts:
        logger.info(f"Завантажено {len(saved_accounts)} збережених Selenium акаунтів: {saved_accounts}")
        for username in saved_accounts:
            selenium_twitter_monitor.add_account(username)
        logger.info(f"✅ Selenium Twitter моніторинг готовий з {len(saved_accounts)} акаунтами")
    else:
        logger.info("ℹ️ Збережених Selenium акаунтів не знайдено - моніторинг буде запущено без акаунтів")
    
    # Запускаємо Selenium моніторинг в окремому потоці
    selenium_thread = threading.Thread(target=lambda: asyncio.run(start_selenium_twitter_monitoring()))
    selenium_thread.daemon = True
    selenium_thread.start()
    logger.info("🚀 Selenium Twitter моніторинг автоматично запущено")
```

### 🔄 Цикл моніторингу

```python
async def start_selenium_twitter_monitoring():
    """Запустити Selenium Twitter моніторинг"""
    global selenium_twitter_monitor
    
    # Перевірка ініціалізації
    if not selenium_twitter_monitor:
        logger.warning("Selenium Twitter монітор не ініціалізовано")
        return
    
    # Перевірка драйвера
    if not selenium_twitter_monitor.driver:
        logger.warning("Selenium драйвер не ініціалізовано, спробуємо ініціалізувати...")
        if not selenium_twitter_monitor._setup_driver(headless=True):
            logger.error("Не вдалося ініціалізувати Selenium драйвер, пропускаємо моніторинг")
            return
    
    try:
        selenium_twitter_monitor.monitoring_active = True
        
        if selenium_twitter_monitor.monitoring_accounts:
            logger.info(f"🚀 Запуск Selenium моніторингу Twitter акаунтів: {list(selenium_twitter_monitor.monitoring_accounts)}")
        else:
            logger.info("🚀 Selenium Twitter моніторинг запущено (очікує додавання акаунтів)")
        
        # Основний цикл моніторингу
        while selenium_twitter_monitor.monitoring_active:
            try:
                # Отримуємо нові твіти через Selenium
                new_tweets = await selenium_twitter_monitor.check_new_tweets()
                
                if new_tweets:
                    # Обробляємо нові твіти
                    handle_twitter_notifications_sync(formatted_tweets)
                    logger.info(f"Selenium: оброблено {len(formatted_tweets)} нових твітів")
                
                # Чекаємо перед наступною перевіркою
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Помилка в циклі Selenium моніторингу Twitter: {e}")
                # Спробуємо переініціалізувати драйвер
                try:
                    selenium_twitter_monitor.close_driver()
                    await asyncio.sleep(5)
                    if selenium_twitter_monitor._setup_driver(headless=True):
                        logger.info("Selenium драйвер переініціалізовано")
                    else:
                        logger.error("Не вдалося переініціалізувати Selenium драйвер")
                except Exception as e2:
                    logger.error(f"Помилка переініціалізації драйвера: {e2}")
                
                await asyncio.sleep(30)  # Коротша затримка при помилці
            
    except Exception as e:
        logger.error(f"Помилка Selenium моніторингу Twitter: {e}")
        # Закриваємо драйвер при критичній помилці
        try:
            selenium_twitter_monitor.close_driver()
        except:
            pass
```

## 📱 Інтерфейс користувача

### 🏠 Головне меню

При використанні команди `/start` тепер показується:

```
👋 Привіт, username!

Ви вже авторизовані в системі.

🚀 Selenium Twitter моніторинг: 🚀 Активний
📊 Акаунтів для моніторингу: 1

Використовуйте меню нижче для навігації.
```

### 🐦 Selenium Twitter меню

При натисканні "🐦 Selenium Twitter" показується:

```
🐦 Selenium Twitter Моніторинг

📊 Статус: 🚀 Активний
👥 Акаунтів: 1
🔄 Автозапуск: ✅ Увімкнено

🔧 Доступні команди:
• /selenium_auth - Авторизація в Twitter
• /selenium_add username - Додати акаунт
• /selenium_test username - Тестувати моніторинг
• /selenium_start - Запустити моніторинг
• /selenium_stop - Зупинити моніторинг

📝 Приклад використання:
1. /selenium_auth - увійдіть в Twitter
2. /selenium_add pilk_xz - додайте акаунт
3. /selenium_test pilk_xz - протестуйте
4. Моніторинг запуститься автоматично!

💡 Переваги Selenium:
• Реальний браузер
• Авторизований доступ
• Надійний парсинг
• Обхід обмежень API
• Автоматичний запуск з ботом
```

## 🎯 Сценарії використання

### ✅ Сценарій 1: Перший запуск
1. Запускаємо бота: `python bot.py`
2. Selenium моніторинг автоматично запускається
3. Додаємо акаунт через меню або команду
4. Моніторинг починає працювати з новим акаунтом

### ✅ Сценарій 2: Перезапуск з акаунтами
1. Перезапускаємо бота: `python bot.py`
2. Selenium моніторинг автоматично запускається
3. Збережені акаунти автоматично завантажуються
4. Моніторинг продовжує працювати з усіма акаунтами

### ✅ Сценарій 3: Додавання нового акаунта
1. Бот вже працює з автозапуском
2. Додаємо новий акаунт через меню
3. Акаунт автоматично додається до активного моніторингу
4. Моніторинг починає перевіряти новий акаунт

## 🔧 Налаштування

### ⚙️ Конфігурація

Автозапуск налаштовується в функції `main()`:

```python
# Автоматично запускаємо Selenium Twitter моніторинг
global selenium_twitter_monitor
selenium_twitter_monitor = SeleniumTwitterMonitor()

# Завантажуємо збережені акаунти
saved_accounts = project_manager.get_selenium_accounts()
if saved_accounts:
    for username in saved_accounts:
        selenium_twitter_monitor.add_account(username)

# Запускаємо в окремому потоці
selenium_thread = threading.Thread(target=lambda: asyncio.run(start_selenium_twitter_monitoring()))
selenium_thread.daemon = True
selenium_thread.start()
```

### 🎛️ Управління

Хоча моніторинг запускається автоматично, користувач все ще може:

- **Додавати акаунти** через меню або команди
- **Видаляти акаунти** через меню
- **Тестувати моніторинг** командою `/selenium_test`
- **Зупиняти моніторинг** командою `/selenium_stop`
- **Перезапускати моніторинг** командою `/selenium_start`

## 🎉 Результат

Тепер Selenium Twitter моніторинг:

- **🚀 Запускається автоматично** з ботом
- **💾 Зберігає акаунти** між перезапусками  
- **🔄 Працює стабільно** в фоновому режимі
- **📱 Показує статус** в інтерфейсі користувача
- **⚡ Не потребує ручного запуску**

Користувачі можуть просто запустити бота і одразу почати додавати акаунти для моніторингу! 🎯