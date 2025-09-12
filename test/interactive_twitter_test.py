#!/usr/bin/env python3
"""
Інтерактивний тест Twitter моніторингу
Дозволяє користувачу тестувати різні функції в реальному часі
"""

import asyncio
import logging
import json
from datetime import datetime
from twitter_monitor import TwitterMonitor
from config import TWITTER_AUTH_TOKEN, TWITTER_CSRF_TOKEN, TWITTER_MONITORING_INTERVAL

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InteractiveTwitterTester:
    """Інтерактивний тестер Twitter моніторингу"""
    
    def __init__(self):
        self.monitor = TwitterMonitor(TWITTER_AUTH_TOKEN, TWITTER_CSRF_TOKEN)
        self.monitoring_accounts = []
        
    def print_menu(self):
        """Вивести меню опцій"""
        print("\n" + "=" * 50)
        print("🐦 ІНТЕРАКТИВНИЙ ТЕСТ TWITTER МОНІТОРИНГУ")
        print("=" * 50)
        print("1. 🔗 Тест підключення")
        print("2. 📝 Тест парсингу URL")
        print("3. 🐦 Отримати твіти акаунта")
        print("4. 📊 Додати акаунт до моніторингу")
        print("5. 🔍 Перевірити нові твіти")
        print("6. ⏱️ Запустити моніторинг (30 сек)")
        print("7. 📋 Показати список акаунтів")
        print("8. 🗑️ Очистити список акаунтів")
        print("9. 📢 Тест форматування сповіщень")
        print("0. 🚪 Вихід")
        print("=" * 50)
        
    def extract_twitter_username(self, url: str) -> str:
        """Витягти username з Twitter URL"""
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
            
    async def test_connection(self):
        """Тест підключення"""
        print("\n🔗 Тестування підключення до Twitter...")
        
        try:
            async with self.monitor:
                print("✅ Підключення успішне!")
                return True
        except Exception as e:
            print(f"❌ Помилка підключення: {e}")
            return False
            
    def test_url_parsing(self):
        """Тест парсингу URL"""
        print("\n📝 Тестування парсингу URL...")
        
        while True:
            url = input("Введіть Twitter URL (або 'back' для повернення): ").strip()
            
            if url.lower() == 'back':
                break
                
            if not url:
                print("❌ Введіть URL!")
                continue
                
            username = self.extract_twitter_username(url)
            print(f"URL: {url}")
            print(f"Username: {username if username else 'Не знайдено'}")
            
    async def get_account_tweets(self):
        """Отримати твіти акаунта"""
        print("\n🐦 Отримання твітів акаунта...")
        
        username = input("Введіть username (без @): ").strip().replace('@', '')
        
        if not username:
            print("❌ Введіть username!")
            return
            
        try:
            async with self.monitor:
                print(f"📱 Отримання твітів для @{username}...")
                
                tweets = await self.monitor.get_user_tweets(username, limit=5)
                
                if tweets:
                    print(f"✅ Знайдено {len(tweets)} твітів:")
                    print("-" * 50)
                    
                    for i, tweet in enumerate(tweets, 1):
                        text = tweet.get('text', '')[:100]
                        timestamp = tweet.get('created_at', 'Невідомо')
                        print(f"{i}. {text}...")
                        print(f"   Час: {timestamp}")
                        print()
                else:
                    print("⚠️ Твіти не знайдено")
                    
        except Exception as e:
            print(f"❌ Помилка: {e}")
            
    def add_account_to_monitoring(self):
        """Додати акаунт до моніторингу"""
        print("\n📊 Додавання акаунта до моніторингу...")
        
        username = input("Введіть username (без @): ").strip().replace('@', '')
        
        if not username:
            print("❌ Введіть username!")
            return
            
        if username in self.monitoring_accounts:
            print(f"⚠️ @{username} вже в списку моніторингу")
            return
            
        self.monitoring_accounts.append(username)
        print(f"✅ @{username} додано до моніторингу")
        
    async def check_new_tweets(self):
        """Перевірити нові твіти"""
        print("\n🔍 Перевірка нових твітів...")
        
        if not self.monitoring_accounts:
            print("❌ Немає акаунтів для моніторингу!")
            return
            
        try:
            async with self.monitor:
                # Додаємо акаунти до монітора
                for account in self.monitoring_accounts:
                    self.monitor.add_account(account)
                    
                print(f"📊 Перевірка {len(self.monitoring_accounts)} акаунтів...")
                
                new_tweets = await self.monitor.check_new_tweets()
                
                if new_tweets:
                    print(f"✅ Знайдено {len(new_tweets)} нових твітів:")
                    print("-" * 50)
                    
                    for tweet in new_tweets:
                        print(f"🐦 @{tweet['account']}")
                        print(f"📝 {tweet['text'][:100]}...")
                        print(f"⏰ {tweet['timestamp']}")
                        print()
                else:
                    print("ℹ️ Нові твіти не знайдені")
                    
        except Exception as e:
            print(f"❌ Помилка: {e}")
            
    async def run_monitoring(self):
        """Запустити моніторинг на 30 секунд"""
        print("\n⏱️ Запуск моніторингу на 30 секунд...")
        
        if not self.monitoring_accounts:
            print("❌ Немає акаунтів для моніторингу!")
            return
            
        try:
            async with self.monitor:
                # Додаємо акаунти
                for account in self.monitoring_accounts:
                    self.monitor.add_account(account)
                    
                print(f"📊 Моніторинг {len(self.monitoring_accounts)} акаунтів...")
                print("⏰ Чекаємо 30 секунд...")
                
                # Запускаємо один цикл моніторингу
                new_tweets = await self.monitor.check_new_tweets()
                
                if new_tweets:
                    print(f"✅ Знайдено {len(new_tweets)} нових твітів!")
                    for tweet in new_tweets:
                        print(f"🐦 @{tweet['account']}: {tweet['text'][:50]}...")
                else:
                    print("ℹ️ Нові твіти не знайдені")
                    
        except Exception as e:
            print(f"❌ Помилка моніторингу: {e}")
            
    def show_accounts(self):
        """Показати список акаунтів"""
        print("\n📋 Список акаунтів для моніторингу:")
        
        if not self.monitoring_accounts:
            print("❌ Список порожній")
            return
            
        for i, account in enumerate(self.monitoring_accounts, 1):
            print(f"{i}. @{account}")
            
    def clear_accounts(self):
        """Очистити список акаунтів"""
        print("\n🗑️ Очищення списку акаунтів...")
        
        if not self.monitoring_accounts:
            print("ℹ️ Список вже порожній")
            return
            
        confirm = input(f"Видалити {len(self.monitoring_accounts)} акаунтів? (y/n): ").lower()
        
        if confirm == 'y':
            self.monitoring_accounts.clear()
            print("✅ Список очищено")
        else:
            print("❌ Скасовано")
            
    def test_notification_formatting(self):
        """Тест форматування сповіщень"""
        print("\n📢 Тестування форматування сповіщень...")
        
        # Тестові дані
        test_tweets = [
            {
                'account': 'elonmusk',
                'tweet_id': '1234567890',
                'text': 'This is a normal tweet without special characters.',
                'author': 'Elon Musk',
                'username': 'elonmusk',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://twitter.com/elonmusk/status/1234567890'
            },
            {
                'account': 'twitter',
                'tweet_id': '0987654321',
                'text': 'This tweet has *asterisks*, _underscores_, [brackets], and (parentheses)!',
                'author': 'Twitter',
                'username': 'twitter',
                'timestamp': datetime.now().isoformat(),
                'url': 'https://twitter.com/twitter/status/0987654321'
            }
        ]
        
        for i, tweet in enumerate(test_tweets, 1):
            print(f"\n--- Тест {i} ---")
            formatted = self.monitor.format_tweet_notification(tweet)
            print(formatted)
            
    async def run(self):
        """Запустити інтерактивний тест"""
        print("🧪 Інтерактивний тест Twitter моніторингу")
        print("Тестуйте різні функції в реальному часі")
        
        if not TWITTER_AUTH_TOKEN:
            print("❌ TWITTER_AUTH_TOKEN не встановлено!")
            print("Додайте TWITTER_AUTH_TOKEN в .env файл")
            return
            
        while True:
            self.print_menu()
            
            try:
                choice = input("Оберіть опцію (0-9): ").strip()
                
                if choice == '0':
                    print("👋 До побачення!")
                    break
                elif choice == '1':
                    await self.test_connection()
                elif choice == '2':
                    self.test_url_parsing()
                elif choice == '3':
                    await self.get_account_tweets()
                elif choice == '4':
                    self.add_account_to_monitoring()
                elif choice == '5':
                    await self.check_new_tweets()
                elif choice == '6':
                    await self.run_monitoring()
                elif choice == '7':
                    self.show_accounts()
                elif choice == '8':
                    self.clear_accounts()
                elif choice == '9':
                    self.test_notification_formatting()
                else:
                    print("❌ Невірний вибір!")
                    
            except KeyboardInterrupt:
                print("\n👋 До побачення!")
                break
            except Exception as e:
                print(f"❌ Помилка: {e}")

async def main():
    """Головна функція"""
    tester = InteractiveTwitterTester()
    await tester.run()

if __name__ == "__main__":
    asyncio.run(main())