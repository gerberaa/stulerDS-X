#!/usr/bin/env python3
"""
Тест форматування повідомлень
"""

from datetime import datetime, timezone
from selenium_twitter_monitor import SeleniumTwitterMonitor

def _get_time_ago(dt: datetime) -> str:
    """Отримати час тому"""
    try:
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} днів тому"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} годин тому"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} хвилин тому"
        else:
            return f"{diff.seconds} секунд тому"
    except:
        return ""

def test_twitter_formatting():
    """Тест форматування Twitter повідомлень"""
    print("🐦 **Приклад форматування Twitter повідомлень:**")
    print("=" * 60)
    
    # Приклад твіта
    tweet = {
        'id': '1234567890',
        'text': 'Це приклад твіта з Twitter. Тут може бути довгий текст, який буде обрізаний якщо перевищить 200 символів.',
        'url': 'https://twitter.com/pilk_xz/status/1234567890',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'user': {
            'screen_name': 'pilk_xz',
            'name': 'Pilk XZ'
        }
    }
    
    # Форматуємо як в Selenium моніторі
    username = tweet.get('user', {}).get('screen_name', 'unknown')
    name = tweet.get('user', {}).get('name', username)
    tweet_id = tweet.get('id', '')
    url = tweet.get('url', f"https://twitter.com/{username}/status/{tweet_id}")
    created_at = tweet.get('created_at', '')
    text = tweet.get('text', '')
    
    # Форматуємо дату
    try:
        if created_at:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%d %B, %H:%M UTC")
            time_ago = _get_time_ago(dt)
        else:
            formatted_date = "Не відомо"
            time_ago = ""
    except:
        formatted_date = created_at
        time_ago = ""
    
    # Обрізаємо текст якщо він занадто довгий
    if len(text) > 200:
        text = text[:200] + "..."
    
    notification = f"""🐦 **Новий твіт з Twitter**
• Профіль: @{username}
• Автор: {name}
• Дата: {formatted_date} ({time_ago})
• Текст: {text}
🔗 [Перейти до твіта]({url})"""
    
    print(notification)
    print()

def test_discord_formatting():
    """Тест форматування Discord повідомлень"""
    print("📢 **Приклад форматування Discord повідомлень:**")
    print("=" * 60)
    
    # Приклад Discord повідомлення
    message = {
        'channel_id': '1358806016648544326',
        'message_id': '1416174003034394675',
        'content': 'Це приклад повідомлення з Discord сервера. Тут також може бути довгий текст.',
        'author': 'nisstobdho',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'url': 'https://discord.com/channels/123456789/1358806016648544326/1416174003034394675'
    }
    
    # Форматуємо як в основному боті
    author = message['author']
    content = message['content']
    
    # Обрізаємо текст якщо він занадто довгий
    if len(content) > 200:
        content = content[:200] + "..."
    
    # Форматуємо дату
    timestamp = message.get('timestamp', '')
    formatted_date = "Не відомо"
    time_ago = ""
    
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_date = dt.strftime("%d %B, %H:%M UTC")
            time_ago = _get_time_ago(dt)
        except:
            formatted_date = timestamp[:19] if len(timestamp) > 19 else timestamp
    
    # Отримуємо інформацію про сервер з URL
    server_name = "Discord"
    try:
        # Спробуємо витягти guild_id з URL
        url_parts = message['url'].split('/')
        if len(url_parts) >= 5:
            guild_id = url_parts[4]
            server_name = f"Discord Server ({guild_id})"
    except:
        pass
    
    forward_text = (
        f"📢 **Нове повідомлення з Discord**\n"
        f"• Сервер: {server_name}\n"
        f"• Автор: {author}\n"
        f"• Дата: {formatted_date} ({time_ago})\n"
        f"• Текст: {content}\n"
        f"🔗 [Перейти до повідомлення]({message['url']})"
    )
    
    print(forward_text)
    print()

def main():
    """Головна функція"""
    print("🎨 **Тест нового форматування повідомлень**")
    print("=" * 70)
    print()
    
    test_twitter_formatting()
    test_discord_formatting()
    
    print("✨ **Особливості нового форматування:**")
    print("• Красиве оформлення з bullet points (•)")
    print("• Форматування дати: '12 September, 05:47 UTC'")
    print("• Час тому: '(2 хвилини тому)'")
    print("• Обрізання довгих текстів до 200 символів")
    print("• Інформація про сервер для Discord")
    print("• Інформація про профіль для Twitter")
    print("• Посилання в кінці повідомлення")

if __name__ == "__main__":
    main()