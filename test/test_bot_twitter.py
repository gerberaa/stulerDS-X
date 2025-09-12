#!/usr/bin/env python3
"""
Тест покращеного Twitter моніторингу в боті
"""

import asyncio
import logging
from twitter_monitor import TwitterMonitor

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_bot_twitter_integration():
    """Тест інтеграції Twitter моніторингу з ботом"""
    print("🚀 Тест інтеграції Twitter моніторингу з ботом")
    print("=" * 60)
    
    auth_token = "262d2ffed60222b5c42f4150300cb144ac012871"
    csrf_token = "ddf294f36c4c0fd61ca8fae2dea1b30f24b82d01ddc860b9c0bf8009876a744b031f8d07b1e4774dea6771b26adcdc217b44726d034345a324b1e0999b31cf9513eeafc0954310dd3478db570e59d170"
    
    async with TwitterMonitor(auth_token, csrf_token) as monitor:
        # Додаємо тестові акаунти
        test_accounts = ["twitter", "elonmusk"]
        
        for account in test_accounts:
            monitor.add_account(account)
            print(f"✅ Додано акаунт: @{account}")
        
        print(f"\n📊 Всього акаунтів для моніторингу: {len(monitor.monitoring_accounts)}")
        
        # Тестуємо отримання твітів
        print("\n🔍 Тестування отримання твітів...")
        
        for account in test_accounts:
            print(f"\n🐦 Тестування @{account}:")
            tweets = await monitor.get_user_tweets(account, limit=3)
            
            if tweets:
                print(f"   ✅ Знайдено {len(tweets)} твітів")
                for i, tweet in enumerate(tweets, 1):
                    text_preview = tweet['text'][:80] + "..." if len(tweet['text']) > 80 else tweet['text']
                    print(f"   {i}. {text_preview}")
                    print(f"      🔗 {tweet['url']}")
            else:
                print(f"   ❌ Твіти не знайдено")
        
        # Тестуємо перевірку нових твітів
        print("\n🔍 Тестування перевірки нових твітів...")
        new_tweets = await monitor.check_new_tweets()
        
        if new_tweets:
            print(f"✅ Знайдено {len(new_tweets)} нових твітів")
            
            # Конвертуємо формат як у боті
            formatted_tweets = []
            for tweet in new_tweets:
                formatted_tweets.append({
                    'tweet_id': tweet.get('id', ''),
                    'account': tweet.get('user', {}).get('screen_name', ''),
                    'author': tweet.get('user', {}).get('name', ''),
                    'text': tweet.get('text', ''),
                    'url': tweet.get('url', ''),
                    'timestamp': tweet.get('created_at', '')
                })
            
            print("\n📝 Форматовані твіти для бота:")
            for i, tweet in enumerate(formatted_tweets, 1):
                print(f"{i}. @{tweet['account']}: {tweet['text'][:60]}...")
                print(f"   ID: {tweet['tweet_id']}")
                print(f"   URL: {tweet['url']}")
        else:
            print("❌ Нові твіти не знайдено")
        
        print("\n🎉 Тест завершено!")
        print("💡 Twitter моніторинг готовий до інтеграції з ботом")

if __name__ == "__main__":
    asyncio.run(test_bot_twitter_integration())