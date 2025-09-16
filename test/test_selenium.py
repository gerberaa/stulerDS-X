#!/usr/bin/env python3
"""
Тест Selenium Twitter Monitor
"""

import asyncio
import logging
from selenium_twitter_monitor import SeleniumTwitterMonitor

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_selenium():
    """Тест Selenium функціональності"""
    print("🧪 Тестування Selenium Twitter Monitor")
    print("=" * 50)
    
    try:
        # Створюємо монітор
        monitor = SeleniumTwitterMonitor()
        
        # Перевіряємо чи драйвер ініціалізовано
        if monitor.driver:
            print("✅ Selenium драйвер успішно ініціалізовано")
        else:
            print("❌ Selenium драйвер не ініціалізовано")
            return
        
        # Додаємо тестовий акаунт
        test_username = "pilk_xz"
        monitor.add_account(test_username)
        print(f"✅ Додано тестовий акаунт: {test_username}")
        
        # Перевіряємо чи є акаунти
        if monitor.monitoring_accounts:
            print(f"✅ Акаунти для моніторингу: {list(monitor.monitoring_accounts)}")
        else:
            print("❌ Немає акаунтів для моніторингу")
            return
        
        # Тестуємо отримання твітів
        print(f"\n🔍 Тестування отримання твітів для {test_username}...")
        tweets = await monitor.get_user_tweets(test_username, limit=3)
        
        if tweets:
            print(f"✅ Отримано {len(tweets)} твітів")
            for i, tweet in enumerate(tweets, 1):
                print(f"  📝 Твіт {i}: {tweet.get('text', '')[:50]}...")
                if tweet.get('images'):
                    print(f"    📷 Зображень: {len(tweet['images'])}")
        else:
            print("❌ Твіти не отримано")
        
        # Тестуємо перевірку нових твітів
        print(f"\n🔄 Тестування перевірки нових твітів...")
        new_tweets = await monitor.check_new_tweets()
        
        if new_tweets:
            print(f"✅ Знайдено {len(new_tweets)} нових твітів")
        else:
            print("ℹ️  Нових твітів не знайдено (це нормально для першого запуску)")
        
        # Закриваємо драйвер
        monitor.close_driver()
        print("✅ Selenium драйвер закрито")
        
        print("\n" + "=" * 50)
        print("🎉 Тест завершено успішно!")
        
    except Exception as e:
        logger.error(f"Помилка тестування: {e}")
        print(f"\n❌ Помилка тестування: {e}")
        print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_selenium())