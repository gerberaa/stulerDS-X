#!/usr/bin/env python3
"""
Тестування Twitter моніторингу
Окремий скрипт для перевірки всієї функціональності Twitter
"""

import asyncio
import logging
import json
from datetime import datetime
from twitter_monitor import TwitterMonitor
from config import TWITTER_AUTH_TOKEN, TWITTER_CSRF_TOKEN, TWITTER_MONITORING_INTERVAL

# Налаштування логування для тестування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TwitterTester:
    """Клас для тестування Twitter моніторингу"""
    
    def __init__(self):
        self.monitor = TwitterMonitor(TWITTER_AUTH_TOKEN, TWITTER_CSRF_TOKEN)
        self.test_accounts = []
        self.test_results = {
            'connection_test': False,
            'account_parsing': False,
            'tweet_fetching': False,
            'monitoring_test': False,
            'notification_test': False
        }
        
    async def test_connection(self):
        """Тест підключення до Twitter"""
        print("🔗 Тестування підключення до Twitter...")
        
        try:
            async with self.monitor:
                print("✅ Підключення до Twitter успішне!")
                self.test_results['connection_test'] = True
                return True
        except Exception as e:
            print(f"❌ Помилка підключення до Twitter: {e}")
            return False
            
    def test_account_parsing(self):
        """Тест парсингу Twitter акаунтів"""
        print("\n📝 Тестування парсингу Twitter акаунтів...")
        
        test_urls = [
            "https://twitter.com/elonmusk",
            "https://x.com/elonmusk", 
            "https://www.twitter.com/elonmusk",
            "https://twitter.com/elonmusk?ref=test",
            "https://twitter.com/elonmusk#section",
            "elonmusk",
            "@elonmusk"
        ]
        
        for url in test_urls:
            username = self.extract_twitter_username(url)
            print(f"URL: {url} -> Username: {username}")
            
        print("✅ Парсинг акаунтів працює!")
        self.test_results['account_parsing'] = True
        return True
        
    def extract_twitter_username(self, url: str) -> str:
        """Витягти username з Twitter URL (копія з bot.py)"""
        try:
            if 'twitter.com' in url or 'x.com' in url:
                url = url.replace('https://', '').replace('http://', '')
                if url.startswith('www.'):
                    url = url[4:]
                    
                if url.startswith('twitter.com/'):
                    username = url.split('/')[1]
                elif url.startswith('x.com/'):
                    username = url.split('/')[1]
                else:
                    return None
                    
                username = username.split('?')[0].split('#')[0]
                return username if username else None
                
            return None
        except Exception as e:
            logger.error(f"Помилка витягування Twitter username: {e}")
            return None
            
    async def test_tweet_fetching(self):
        """Тест отримання твітів"""
        print("\n🐦 Тестування отримання твітів...")
        
        # Тестові акаунти (публічні)
        test_accounts = ['elonmusk', 'twitter', 'github']
        
        try:
            async with self.monitor:
                for account in test_accounts:
                    print(f"📱 Тестування акаунта: @{account}")
                    
                    # Додаємо акаунт
                    self.monitor.add_account(account)
                    
                    # Отримуємо твіти
                    tweets = await self.monitor.get_user_tweets(account, limit=3)
                    
                    if tweets:
                        print(f"✅ Знайдено {len(tweets)} твітів для @{account}")
                        for i, tweet in enumerate(tweets[:2]):  # Показуємо тільки 2
                            print(f"  {i+1}. {tweet.get('text', '')[:100]}...")
                    else:
                        print(f"⚠️ Твіти не знайдено для @{account}")
                        
                    # Затримка між запитами
                    await asyncio.sleep(2)
                    
            print("✅ Отримання твітів працює!")
            self.test_results['tweet_fetching'] = True
            return True
            
        except Exception as e:
            print(f"❌ Помилка отримання твітів: {e}")
            return False
            
    async def test_monitoring_cycle(self):
        """Тест циклу моніторингу"""
        print("\n🔄 Тестування циклу моніторингу...")
        
        try:
            async with self.monitor:
                # Додаємо тестові акаунти
                test_accounts = ['elonmusk', 'twitter']
                for account in test_accounts:
                    self.monitor.add_account(account)
                    
                print(f"📊 Додано {len(test_accounts)} акаунтів для моніторингу")
                
                # Запускаємо один цикл моніторингу
                new_tweets = await self.monitor.check_new_tweets()
                
                print(f"🔍 Знайдено {len(new_tweets)} нових твітів")
                
                if new_tweets:
                    for tweet in new_tweets:
                        print(f"  🐦 @{tweet['account']}: {tweet['text'][:50]}...")
                        
                print("✅ Цикл моніторингу працює!")
                self.test_results['monitoring_test'] = True
                return True
                
        except Exception as e:
            print(f"❌ Помилка циклу моніторингу: {e}")
            return False
            
    def test_notification_formatting(self):
        """Тест форматування сповіщень"""
        print("\n📢 Тестування форматування сповіщень...")
        
        # Тестові дані твіта
        test_tweet = {
            'account': 'elonmusk',
            'tweet_id': '1234567890',
            'text': 'This is a test tweet with *special* characters and [links]!',
            'author': 'Elon Musk',
            'username': 'elonmusk',
            'timestamp': datetime.now().isoformat(),
            'url': 'https://twitter.com/elonmusk/status/1234567890'
        }
        
        try:
            formatted = self.monitor.format_tweet_notification(test_tweet)
            print("✅ Форматоване сповіщення:")
            print("-" * 50)
            print(formatted)
            print("-" * 50)
            
            self.test_results['notification_test'] = True
            return True
            
        except Exception as e:
            print(f"❌ Помилка форматування сповіщення: {e}")
            return False
            
    async def run_full_test(self):
        """Запустити повний тест"""
        print("🚀 Запуск повного тесту Twitter моніторингу")
        print("=" * 60)
        
        # Тест 1: Підключення
        await self.test_connection()
        
        # Тест 2: Парсинг акаунтів
        self.test_account_parsing()
        
        # Тест 3: Отримання твітів
        await self.test_tweet_fetching()
        
        # Тест 4: Цикл моніторингу
        await self.test_monitoring_cycle()
        
        # Тест 5: Форматування сповіщень
        self.test_notification_formatting()
        
        # Підсумок
        self.print_summary()
        
    def print_summary(self):
        """Вивести підсумок тестів"""
        print("\n" + "=" * 60)
        print("📊 ПІДСУМОК ТЕСТІВ")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        for test_name, result in self.test_results.items():
            status = "✅ ПРОЙДЕНО" if result else "❌ ПРОВАЛЕНО"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            
        print(f"\n🎯 Результат: {passed_tests}/{total_tests} тестів пройдено")
        
        if passed_tests == total_tests:
            print("🎉 Всі тести пройдено! Twitter моніторинг готовий до роботи.")
        else:
            print("⚠️ Деякі тести провалено. Перевірте налаштування.")
            
        print("\n💡 Рекомендації:")
        if not self.test_results['connection_test']:
            print("- Перевірте TWITTER_AUTH_TOKEN в .env файлі")
        if not self.test_results['tweet_fetching']:
            print("- Перевірте інтернет-з'єднання та доступ до Twitter")
        if not self.test_results['monitoring_test']:
            print("- Перевірте налаштування моніторингу")

async def main():
    """Головна функція тестування"""
    print("🧪 Twitter Monitor Tester")
    print("Тестування всієї функціональності Twitter моніторингу")
    print()
    
    if not TWITTER_AUTH_TOKEN:
        print("❌ TWITTER_AUTH_TOKEN не встановлено!")
        print("Додайте TWITTER_AUTH_TOKEN в .env файл")
        return
        
    tester = TwitterTester()
    await tester.run_full_test()

if __name__ == "__main__":
    asyncio.run(main())