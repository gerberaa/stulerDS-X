# 📷 Підтримка зображень в Telegram Monitor Bot

## 🆕 Нова функціональність

Бот тепер підтримує автоматичне витягування та відправку зображень з:
- **Twitter/X твітів** - всі фото з твітів
- **Discord повідомлень** - вкладення та embed зображення

## 🔧 Як це працює

### Twitter/X Моніторинг

#### Selenium Twitter Monitor
- Автоматично виявляє зображення в твітах
- Підтримує множинні зображення (до 5 на твіт)
- Витягує оригінальні URL зображень
- Відправляє кожне зображення окремо з підписом

#### Звичайний Twitter Monitor
- Підтримує зображення через HTML парсинг
- Витягує зображення з JSON даних Twitter

### Discord Моніторинг

#### Підтримувані типи зображень:
- **Attachments** - файли, завантажені користувачами
- **Embeds** - зображення в embed повідомленнях
- **Thumbnails** - мініатюри в embed

## 📋 Технічні деталі

### Витягування зображень

#### Twitter
```python
def _extract_tweet_images(self, element) -> List[str]:
    """Витягти URL фото з твіта"""
    images = []
    
    # Селектори для пошуку зображень
    image_selectors = [
        'img[src*="media"]',
        'img[src*="pbs.twimg.com"]',
        'img[alt*="Image"]',
        '[data-testid="tweetPhoto"] img',
        'div[data-testid="tweetPhoto"] img'
    ]
    
    # Витягуємо та очищаємо URL
    for selector in image_selectors:
        img_elements = element.find_elements(By.CSS_SELECTOR, selector)
        for img in img_elements:
            src = img.get_attribute('src')
            if src and ('media' in src or 'pbs.twimg.com' in src):
                clean_url = src.split('?')[0]  # Видаляємо параметри
                images.append(clean_url)
    
    return images
```

#### Discord
```python
def _extract_message_images(self, message: Dict) -> List[str]:
    """Витягти URL фото з Discord повідомлення"""
    images = []
    
    # Перевіряємо attachments
    attachments = message.get('attachments', [])
    for attachment in attachments:
        if attachment.get('content_type', '').startswith('image/'):
            url = attachment.get('url')
            if url:
                images.append(url)
    
    # Перевіряємо embeds
    embeds = message.get('embeds', [])
    for embed in embeds:
        if 'image' in embed:
            image_url = embed['image'].get('url')
            if image_url:
                images.append(image_url)
        
        if 'thumbnail' in embed:
            thumb_url = embed['thumbnail'].get('url')
            if thumb_url:
                images.append(thumb_url)
    
    return images
```

### Завантаження та відправка

```python
def download_and_send_image(image_url: str, chat_id: str, caption: str = "") -> bool:
    """Завантажити та відправити зображення в Telegram"""
    try:
        # Завантажуємо зображення
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(image_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Перевіряємо розмір (максимум 20MB для Telegram)
        if len(response.content) > 20 * 1024 * 1024:
            return False
        
        # Створюємо тимчасовий файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        try:
            # Відправляємо через Telegram API
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            
            with open(temp_file_path, 'rb') as photo_file:
                files = {'photo': photo_file}
                data = {
                    'chat_id': chat_id,
                    'caption': caption[:1024],  # Обмеження Telegram
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, files=files, data=data, timeout=30)
                return response.status_code == 200
                
        finally:
            # Видаляємо тимчасовий файл
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Помилка завантаження/відправки зображення: {e}")
        return False
```

## 🎯 Формат сповіщень

### Twitter з зображеннями
```
🐦 **Новий твіт з Twitter**
• Профіль: @username
• Автор: Display Name
• Дата: 13 September, 16:30 UTC (2 години тому)
• Текст: Твіт з фото...
📷 Зображень: 2
🔗 [Перейти до твіта](https://x.com/username/status/123)

[Потім відправляються зображення окремо]
📷 Twitter зображення 1/2
📷 Twitter зображення 2/2
```

### Discord з зображеннями
```
📢 **Нове повідомлення з Discord**
• Сервер: Discord Server (123456789)
• Автор: Username
• Дата: 13 September, 16:30 UTC (2 години тому)
• Текст: Повідомлення з фото...
📷 Зображень: 1
🔗 [Перейти до повідомлення](https://discord.com/channels/...)

[Потім відправляється зображення]
📷 Discord зображення
```

## ⚙️ Налаштування

### Chrome/Selenium налаштування
```python
# Дозволяємо зображення в Chrome
prefs = {
    "profile.managed_default_content_settings.images": 1,  # Дозволити зображення
    "profile.default_content_setting_values.notifications": 2,
    "profile.managed_default_content_settings.media_stream": 1
}
chrome_options.add_experimental_option("prefs", prefs)
```

### Обмеження
- **Максимум зображень**: 5 на повідомлення/твіт
- **Розмір файлу**: до 20MB (обмеження Telegram)
- **Затримка між зображеннями**: 1 секунда
- **Timeout завантаження**: 10 секунд
- **Caption обмеження**: 1024 символи

## 🧪 Тестування

Запустіть тест функціональності:
```bash
python test_image_functionality.py
```

Тест перевіряє:
- ✅ Витягування зображень з Twitter
- ✅ Витягування зображень з Discord
- ✅ Завантаження зображень
- ✅ Форматування сповіщень

## 🐛 Вирішення проблем

### Зображення не відправляються
1. Перевірте інтернет-з'єднання
2. Переконайтеся що URL зображень доступні
3. Перевірте розмір файлів (максимум 20MB)
4. Перевірте логи на помилки

### Selenium не бачить зображення
1. Переконайтеся що Chrome дозволяє зображення
2. Перевірте що профіль браузера правильно налаштований
3. Спробуйте запустити без headless режиму

### Discord зображення не витягуються
1. Перевірте Discord authorization токен
2. Переконайтеся що бот має доступ до каналу
3. Перевірте формат повідомлень (attachments/embeds)

## 📈 Покращення продуктивності

### Оптимізації
- Тимчасові файли автоматично видаляються
- Затримки між зображеннями для уникнення rate limit
- Обмеження кількості зображень
- Перевірка розміру файлів перед завантаженням

### Логування
- Детальне логування процесу витягування зображень
- Помилки завантаження/відправки логуються
- Статистика кількості знайдених зображень

## 🔄 Оновлення з попередньої версії

Якщо у вас вже є робоча версія бота:

1. **Оновіть файли**:
   - `selenium_twitter_monitor.py` - додано витягування зображень
   - `discord_monitor.py` - додано витягування зображень
   - `bot.py` - додано функцію завантаження та відправки

2. **Перезапустіть бота** - нові функції активуються автоматично

3. **Протестуйте** - запустіть `test_image_functionality.py`

## 🎉 Готово!

Тепер ваш бот автоматично:
- 🔍 Знаходить зображення в Twitter твітах
- 🔍 Знаходить зображення в Discord повідомленнях
- 📥 Завантажує зображення
- 📤 Відправляє їх в Telegram канал
- 📝 Додає інформацію про кількість зображень в сповіщення

Всі зображення відправляються з підписами та зберігають оригінальну якість!