#!/usr/bin/env python3
"""
Тест покращеного HTML парсингу для Twitter
"""

import asyncio
import logging
from twitter_monitor import TwitterMonitor

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_html_parsing():
    """Тест покращеного HTML парсингу"""
    print("🚀 Тест покращеного HTML парсингу Twitter")
    print("=" * 50)
    
    auth_token = "262d2ffed60222b5c42f4150300cb144ac012871"
    csrf_token = "ddf294f36c4c0fd61ca8fae2dea1b30f24b82d01ddc860b9c0bf8009876a744b031f8d07b1e4774dea6771b26adcdc217b44726d034345a324b1e0999b31cf9513eeafc0954310dd3478db570e59d170"
    
    async with TwitterMonitor(auth_token, csrf_token) as monitor:
        # Додаємо акаунт для тестування
        monitor.add_account("twitter")
        
        print("🔍 Тестування HTML парсингу...")
        
        # Отримуємо твіти через HTML парсинг
        tweets = await monitor.get_user_tweets("twitter", limit=5)
        
        print(f"📊 Результат: знайдено {len(tweets)} твітів")
        
        if tweets:
            print("\n📝 Знайдені твіти:")
            for i, tweet in enumerate(tweets, 1):
                print(f"{i}. ID: {tweet['id']}")
                print(f"   Текст: {tweet['text'][:100]}...")
                print(f"   URL: {tweet['url']}")
                print()
        else:
            print("❌ Твіти не знайдено")
        
        # Перевіряємо нові твіти
        print("🔍 Перевірка нових твітів...")
        new_tweets = await monitor.check_new_tweets()
        print(f"📊 Знайдено {len(new_tweets)} нових твітів")
        
        if new_tweets:
            print("\n🆕 Нові твіти:")
            for i, tweet in enumerate(new_tweets, 1):
                print(f"{i}. {tweet['text'][:100]}...")
                print(f"   URL: {tweet['url']}")
                print()

if __name__ == "__main__":
    asyncio.run(test_html_parsing())