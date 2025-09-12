#!/usr/bin/env python3
"""
Швидкий тест Twitter моніторингу
Простий скрипт для швидкої перевірки основної функціональності
"""

import asyncio
import logging
from twitter_monitor import TwitterMonitor
from config import TWITTER_AUTH_TOKEN, TWITTER_CSRF_TOKEN

# Мінімальне логування
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

async def quick_test():
    """Швидкий тест основної функціональності"""
    print("🚀 Швидкий тест Twitter моніторингу")
    print("-" * 40)
    
    if not TWITTER_AUTH_TOKEN:
        print("❌ TWITTER_AUTH_TOKEN не встановлено!")
        return False
        
    try:
        # Створюємо монітор
        monitor = TwitterMonitor(TWITTER_AUTH_TOKEN, TWITTER_CSRF_TOKEN)
        
        # Тест 1: Підключення
        print("🔗 Тест підключення...")
        async with monitor:
            print("✅ Підключення OK")
            
            # Тест 2: Додавання акаунта
            print("📝 Тест додавання акаунта...")
            monitor.add_account('twitter')
            print("✅ Додавання акаунта OK")
            
            # Тест 3: Отримання твітів
            print("🐦 Тест отримання твітів...")
            tweets = await monitor.get_user_tweets('twitter', limit=2)
            
            if tweets:
                print(f"✅ Отримано {len(tweets)} твітів")
                print(f"   Приклад: {tweets[0].get('text', '')[:50]}...")
            else:
                print("⚠️ Твіти не отримано")
                
            # Тест 4: Перевірка нових твітів
            print("🔍 Тест перевірки нових твітів...")
            new_tweets = await monitor.check_new_tweets()
            print(f"✅ Перевірка завершена, знайдено {len(new_tweets)} нових твітів")
            
        print("\n🎉 Швидкий тест завершено успішно!")
        return True
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(quick_test())
    
    if success:
        print("\n💡 Рекомендації:")
        print("- Запустіть 'python test_twitter.py' для повного тесту")
        print("- Запустіть 'python interactive_twitter_test.py' для інтерактивного тесту")
        print("- Запустіть 'python bot.py' для роботи з ботом")
    else:
        print("\n⚠️ Перевірте налаштування:")
        print("- TWITTER_AUTH_TOKEN в .env файлі")
        print("- TWITTER_CSRF_TOKEN в .env файлі")
        print("- Інтернет-з'єднання")
        print("- Доступ до Twitter")