#!/usr/bin/env python3
"""
Тест інтеграції Selenium Twitter Monitor
"""

import asyncio
import logging
from selenium_twitter_monitor import SeleniumTwitterMonitor

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_selenium_monitor():
    """Тестування Selenium монітора"""
    print("🧪 Тестування Selenium Twitter Monitor")
    print("=" * 50)
    
    async with SeleniumTwitterMonitor() as monitor:
        print("✅ Selenium монітор ініціалізовано")
        
        # Додаємо тестовий акаунт
        if monitor.add_account("pilk_xz"):
            print("✅ Додано тестовий акаунт: pilk_xz")
        else:
            print("❌ Помилка додавання акаунта")
            return
        
        # Тестуємо отримання твітів
        print("\n🔍 Тестування отримання твітів...")
        tweets = await monitor.get_user_tweets("pilk_xz", limit=3)
        
        if tweets:
            print(f"✅ Знайдено {len(tweets)} твітів:")
            for i, tweet in enumerate(tweets, 1):
                text_preview = tweet['text'][:80] + "..." if len(tweet['text']) > 80 else tweet['text']
                print(f"   {i}. {text_preview}")
                print(f"      🔗 {tweet['url']}")
        else:
            print("❌ Твіти не знайдено")
        
        # Тестуємо перевірку нових твітів
        print("\n🔄 Тестування перевірки нових твітів...")
        new_tweets = await monitor.check_new_tweets()
        print(f"📊 Знайдено {len(new_tweets)} нових твітів")
        
        # Тестуємо форматування сповіщення
        if tweets:
            print("\n📝 Тестування форматування сповіщення...")
            notification = monitor.format_tweet_notification(tweets[0])
            print("✅ Форматоване сповіщення:")
            print("-" * 40)
            print(notification)
            print("-" * 40)
        
        print("\n🎉 Тест завершено успішно!")

if __name__ == "__main__":
    print("🚀 Запуск тесту Selenium інтеграції")
    print("⚠️ Переконайтеся, що у вас встановлений Chrome та ChromeDriver")
    print("=" * 60)
    
    try:
        asyncio.run(test_selenium_monitor())
    except KeyboardInterrupt:
        print("\n⏹️ Тест зупинено користувачем")
    except Exception as e:
        logger.error(f"Помилка тесту: {e}")
        print(f"❌ Помилка тесту: {e}")