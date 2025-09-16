#!/usr/bin/env python3
"""
Прямий монітор профілю @pilk_xz з HTML парсингом
"""

import asyncio
import logging
import requests
import re
import time
from datetime import datetime
from typing import Set, List, Dict

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DirectPilkXzMonitor:
    """Прямий монітор для профілю @pilk_xz"""
    
    def __init__(self):
        self.username = "pilk_xz"
        self.url = f"https://x.com/{self.username}"
        self.seen_tweets = set()  # Для відстеження вже побачених твітів
        self.monitoring_active = False
        
        # Headers для запитів
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
    async def start_monitoring(self):
        """Запустити моніторинг профілю"""
        print("🚀 Запуск прямого моніторингу профілю @pilk_xz")
        print("=" * 60)
        
        try:
            # Отримуємо початкові твіти
            print("🔍 Отримання початкових твітів...")
            initial_tweets = await self._get_tweets_from_profile()
            
            if initial_tweets:
                print(f"📊 Знайдено {len(initial_tweets)} початкових твітів")
                for tweet in initial_tweets:
                    self.seen_tweets.add(tweet['id'])
                    print(f"   📝 {tweet['text'][:80]}...")
            else:
                print("⚠️ Початкові твіти не знайдено")
            
            print("\n🔄 Початок моніторингу нових постів...")
            print("💡 Натисніть Ctrl+C для зупинки")
            print("-" * 60)
            
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
            
    async def _get_tweets_from_profile(self) -> List[Dict]:
        """Отримати твіти з профілю через прямий HTML парсинг"""
        try:
            # Використовуємо requests для синхронного запиту
            response = requests.get(self.url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                html = response.text
                return self._parse_tweets_from_html(html)
            else:
                logger.error(f"Помилка завантаження сторінки: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Помилка отримання твітів: {e}")
            return []
            
    def _parse_tweets_from_html(self, html: str) -> List[Dict]:
        """Парсинг твітів з HTML"""
        tweets = []
        
        try:
            # Різні паттерни для пошуку твітів
            patterns = [
                # Паттерн для пошуку твітів з data-tweet-id
                r'data-tweet-id="(\d+)"[^>]*>.*?<div[^>]*class="[^"]*tweet-text[^"]*"[^>]*>(.*?)</div>',
                # Паттерн для пошуку твітів в article тегах
                r'<article[^>]*data-testid="tweet"[^>]*>.*?<div[^>]*dir="auto"[^>]*>(.*?)</div>',
                # Паттерн для пошуку твітів з href
                r'href="/{}/status/(\d+)"[^>]*>.*?<div[^>]*dir="auto"[^>]*>(.*?)</div>'.format(self.username),
                # Загальний паттерн для пошуку текстів твітів
                r'<div[^>]*dir="auto"[^>]*class="[^"]*"[^>]*>(.*?)</div>',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
                
                for match in matches:
                    if len(match) == 2:
                        tweet_id, text = match
                    else:
                        # Якщо тільки текст
                        text = match
                        tweet_id = f"html_{len(tweets)}_{int(time.time())}"
                    
                    # Очищаємо текст від HTML тегів
                    clean_text = re.sub(r'<[^>]+>', '', text)
                    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                    
                    # Фільтруємо короткі або порожні тексти
                    if len(clean_text) > 10 and clean_text not in ['...', '.', '']:
                        tweets.append({
                            'id': tweet_id,
                            'text': clean_text,
                            'url': f"https://twitter.com/{self.username}/status/{tweet_id}",
                            'created_at': datetime.now().isoformat()
                        })
                        
                        # Обмежуємо кількість твітів
                        if len(tweets) >= 10:
                            break
                
                if tweets:
                    break  # Якщо знайшли твіти з цим паттерном, зупиняємося
            
            # Видаляємо дублікати
            seen_texts = set()
            unique_tweets = []
            for tweet in tweets:
                if tweet['text'] not in seen_texts:
                    seen_texts.add(tweet['text'])
                    unique_tweets.append(tweet)
            
            return unique_tweets
            
        except Exception as e:
            logger.error(f"Помилка парсингу HTML: {e}")
            return []
            
    async def _check_for_new_posts(self):
        """Перевірити нові пости"""
        try:
            tweets = await self._get_tweets_from_profile()
            
            if tweets:
                new_tweets = []
                current_tweet_ids = set()
                
                for tweet in tweets:
                    tweet_id = tweet['id']
                    current_tweet_ids.add(tweet_id)
                    
                    if tweet_id not in self.seen_tweets:
                        new_tweets.append(tweet)
                        print(f"🆕 Знайдено новий твіт: {tweet_id}")
                
                # Оновлюємо список відстежуваних твітів
                self.seen_tweets = current_tweet_ids
                
                if new_tweets:
                    self._notify_new_posts(new_tweets)
                else:
                    current_time = datetime.now().strftime("%H:%M:%S")
                    print(f"[{current_time}] 🔍 Перевірка завершена - нових постів немає (відстежується {len(self.seen_tweets)} твітів)")
            else:
                print("⚠️ Не вдалося отримати твіти")
                
        except Exception as e:
            logger.error(f"Помилка перевірки нових постів: {e}")
            
    def _notify_new_posts(self, new_tweets):
        """Повідомити про нові пости"""
        print("\n" + "🎉" * 20)
        print("🆕 НОВІ ПОСТИ ЗНАЙДЕНО!")
        print("🎉" * 20)
        
        for i, tweet in enumerate(new_tweets, 1):
            print(f"\n📝 Пост #{i}:")
            print(f"🆔 ID: {tweet['id']}")
            print(f"👤 Автор: @{self.username}")
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
        print(f"📝 Відстежується твітів: {len(self.seen_tweets)}")
        print(f"🔗 Профіль: {self.url}")

async def main():
    """Головна функція"""
    monitor = DirectPilkXzMonitor()
    
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
    print("🐦 Прямий монітор профілю @pilk_xz")
    print("=" * 40)
    asyncio.run(main())