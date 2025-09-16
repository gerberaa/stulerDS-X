#!/usr/bin/env python3
"""
Скрипт для моніторингу профілю @pilk_xz на Twitter/X
"""

import asyncio
import logging
import time
from datetime import datetime
from twitter_monitor import TwitterMonitor

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PilkXzMonitor:
    """Монітор для профілю @pilk_xz"""
    
    def __init__(self):
        self.auth_token = "262d2ffed60222b5c42f4150300cb144ac012871"
        self.csrf_token = "ddf294f36c4c0fd61ca8fae2dea1b30f24b82d01ddc860b9c0bf8009876a744b031f8d07b1e4774dea6771b26adcdc217b44726d034345a324b1e0999b31cf9513eeafc0954310dd3478db570e59d170"
        self.username = "pilk_xz"
        self.twitter_monitor = None
        self.last_tweet_ids = set()  # Для відстеження вже побачених твітів
        self.monitoring_active = False
        
    async def start_monitoring(self):
        """Запустити моніторинг профілю"""
        print("🚀 Запуск моніторингу профілю @pilk_xz")
        print("=" * 50)
        
        try:
            async with TwitterMonitor(self.auth_token, self.csrf_token) as monitor:
                self.twitter_monitor = monitor
                
                # Додаємо акаунт для моніторингу
                monitor.add_account(self.username)
                print(f"✅ Додано акаунт @{self.username} для моніторингу")
                
                # Отримуємо початкові твіти для бази
                print("🔍 Отримання початкових твітів...")
                initial_tweets = await monitor.get_user_tweets(self.username, limit=10)
                
                if initial_tweets:
                    real_tweets = []
                    for tweet in initial_tweets:
                        if self._is_real_tweet(tweet):
                            real_tweets.append(tweet)
                            self.last_tweet_ids.add(tweet['id'])
                    
                    print(f"📊 Знайдено {len(real_tweets)} справжніх твітів (відфільтровано {len(initial_tweets) - len(real_tweets)} системних)")
                    
                    if real_tweets:
                        print("📝 Початкові твіти:")
                        for tweet in real_tweets[:3]:  # Показуємо тільки перші 3
                            text_preview = tweet['text'][:60] + "..." if len(tweet['text']) > 60 else tweet['text']
                            print(f"   📝 {text_preview}")
                    else:
                        print("⚠️ Справжніх твітів не знайдено")
                else:
                    print("⚠️ Початкові твіти не знайдено")
                
                print("\n🔄 Початок моніторингу нових постів...")
                print("💡 Натисніть Ctrl+C для зупинки")
                print("-" * 50)
                
                self.monitoring_active = True
                
                # Основний цикл моніторингу
                while self.monitoring_active:
                    try:
                        await self._check_for_new_posts()
                        await asyncio.sleep(30)  # Перевірка кожні 30 секунд
                        
                    except KeyboardInterrupt:
                        print("\n⏹️ Зупинка моніторингу...")
                        self.monitoring_active = False
                        break
                    except Exception as e:
                        logger.error(f"Помилка в циклі моніторингу: {e}")
                        await asyncio.sleep(10)  # Коротша затримка при помилці
                        
        except Exception as e:
            logger.error(f"Критична помилка моніторингу: {e}")
            
    async def _check_for_new_posts(self):
        """Перевірити нові пости"""
        try:
            tweets = await self.twitter_monitor.get_user_tweets(self.username, limit=10)
            
            if tweets:
                new_tweets = []
                current_tweet_ids = set()
                
                # Спочатку збираємо всі поточні ID
                for tweet in tweets:
                    tweet_id = tweet['id']
                    current_tweet_ids.add(tweet_id)
                    
                    # Перевіряємо чи це новий твіт
                    if tweet_id not in self.last_tweet_ids:
                        # Додаткова перевірка - чи це справжній твіт, а не системні дані
                        if self._is_real_tweet(tweet):
                            new_tweets.append(tweet)
                            print(f"🆕 Знайдено новий твіт: {tweet_id}")
                
                # Оновлюємо список відстежуваних твітів
                self.last_tweet_ids = current_tweet_ids
                
                # Додаткове логування для діагностики
                if len(tweets) > 0:
                    print(f"🔍 Діагностика: отримано {len(tweets)} твітів, знайдено {len(new_tweets)} нових")
                    for tweet in tweets[:2]:  # Показуємо перші 2 твіти для діагностики
                        print(f"   📋 Твіт ID: {tweet['id']}, Текст: '{tweet.get('text', '')[:30]}...', Реальний: {self._is_real_tweet(tweet)}")
                
                if new_tweets:
                    self._notify_new_posts(new_tweets)
                else:
                    # Тихе логування - нових постів немає
                    current_time = datetime.now().strftime("%H:%M:%S")
                    print(f"[{current_time}] 🔍 Перевірка завершена - нових постів немає (відстежується {len(self.last_tweet_ids)} твітів)")
            else:
                print("⚠️ Не вдалося отримати твіти")
                
        except Exception as e:
            logger.error(f"Помилка перевірки нових постів: {e}")
            
    def _is_real_tweet(self, tweet):
        """Перевірити чи це справжній твіт, а не системні дані"""
        tweet_id = tweet['id']
        text = tweet.get('text', '')
        
        # Фільтруємо системні дані
        system_keywords = ['entities', 'errors', 'fetchStatus', 'timeline', 'user', 'data']
        
        # Якщо ID містить системні ключові слова
        if any(keyword in tweet_id.lower() for keyword in system_keywords):
            return False
            
        # Якщо текст порожній або містить тільки крапки
        if not text or text.strip() in ['.', '...', '']:
            return False
            
        # Якщо текст занадто короткий (менше 5 символів)
        if len(text.strip()) < 5:
            return False
            
        # Якщо це виглядає як справжній твіт
        return True
            
    def _notify_new_posts(self, new_tweets):
        """Повідомити про нові пости"""
        print("\n" + "🎉" * 20)
        print("🆕 НОВІ ПОСТИ ЗНАЙДЕНО!")
        print("🎉" * 20)
        
        for i, tweet in enumerate(new_tweets, 1):
            print(f"\n📝 Пост #{i}:")
            print(f"🆔 ID: {tweet['id']}")
            print(f"👤 Автор: @{tweet['user']['screen_name']}")
            print(f"📅 Час: {tweet['created_at']}")
            print(f"🔗 URL: {tweet['url']}")
            print(f"📄 Текст:")
            print("-" * 40)
            
            # Форматуємо текст для кращого відображення
            text = tweet['text']
            if len(text) > 200:
                print(text[:200] + "...")
                print(f"[Повний текст: {len(text)} символів]")
            else:
                print(text)
                
            print("-" * 40)
            
        print(f"\n✅ Всього нових постів: {len(new_tweets)}")
        print("🎉" * 20 + "\n")
        
    def print_status(self):
        """Вивести статус моніторингу"""
        print(f"\n📊 Статус моніторингу:")
        print(f"👤 Профіль: @{self.username}")
        print(f"🔄 Активний: {'✅ Так' if self.monitoring_active else '❌ Ні'}")
        print(f"📝 Відстежується твітів: {len(self.last_tweet_ids)}")
        print(f"🔗 Профіль: https://x.com/{self.username}")

async def main():
    """Головна функція"""
    monitor = PilkXzMonitor()
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n👋 Моніторинг зупинено користувачем")
    except Exception as e:
        logger.error(f"Помилка запуску: {e}")
    finally:
        monitor.print_status()
        print("🏁 Скрипт завершено")

if __name__ == "__main__":
    print("🐦 Монітор профілю @pilk_xz")
    print("=" * 30)
    asyncio.run(main())