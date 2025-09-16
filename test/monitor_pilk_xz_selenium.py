#!/usr/bin/env python3
"""
Монітор профілю @pilk_xz з використанням Selenium та реального браузера
"""

import asyncio
import logging
import time
import json
from datetime import datetime
from typing import Set, List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SeleniumPilkXzMonitor:
    """Монітор для профілю @pilk_xz з Selenium"""
    
    def __init__(self):
        self.username = "pilk_xz"
        self.url = f"https://x.com/{self.username}"
        self.seen_tweets = set()  # Для відстеження вже побачених твітів
        self.monitoring_active = False
        self.driver = None
        
    def _setup_driver(self):
        """Налаштувати Chrome драйвер"""
        chrome_options = Options()
        
        # Базові налаштування
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User Agent
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Відключити зображення для швидкості
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Запустити в фоновому режимі (закоментовано для діагностики)
        # chrome_options.add_argument('--headless')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome драйвер успішно ініціалізовано")
            return True
        except Exception as e:
            logger.error(f"Помилка ініціалізації Chrome драйвера: {e}")
            return False
    
    async def start_monitoring(self):
        """Запустити моніторинг профілю"""
        print("🚀 Запуск Selenium моніторингу профілю @pilk_xz")
        print("=" * 60)
        
        if not self._setup_driver():
            print("❌ Не вдалося ініціалізувати браузер")
            return
        
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
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Браузер закрито")
            
    async def _get_tweets_from_profile(self) -> List[Dict]:
        """Отримати твіти з профілю через Selenium"""
        try:
            print(f"🌐 Відкриваємо профіль: {self.url}")
            self.driver.get(self.url)
            
            # Чекаємо завантаження сторінки
            await asyncio.sleep(5)
            
            # Чекаємо появи твітів
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
                )
                print("✅ Твіти завантажені")
            except TimeoutException:
                print("⚠️ Твіти не знайдені за 10 секунд, спробуємо інший селектор")
            
            # Отримуємо твіти
            tweets = self._extract_tweets_from_page()
            return tweets
            
        except Exception as e:
            logger.error(f"Помилка отримання твітів: {e}")
            return []
            
    def _extract_tweets_from_page(self) -> List[Dict]:
        """Витягти твіти з поточної сторінки"""
        tweets = []
        
        try:
            # Різні селектори для пошуку твітів
            selectors = [
                '[data-testid="tweet"]',
                'article[role="article"]',
                '[data-testid="tweetText"]',
                '.tweet'
            ]
            
            tweet_elements = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        tweet_elements = elements
                        print(f"✅ Знайдено {len(elements)} елементів з селектором: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not tweet_elements:
                print("❌ Твіти не знайдені")
                return []
            
            # Витягуємо дані з кожного твіта
            for i, element in enumerate(tweet_elements[:10]):  # Максимум 10 твітів
                try:
                    tweet_data = self._extract_tweet_data(element, i)
                    if tweet_data:
                        tweets.append(tweet_data)
                except Exception as e:
                    logger.debug(f"Помилка витягування даних твіта {i}: {e}")
                    continue
            
            print(f"📝 Витягнуто {len(tweets)} твітів")
            return tweets
            
        except Exception as e:
            logger.error(f"Помилка витягування твітів: {e}")
            return []
            
    def _extract_tweet_data(self, element, index: int) -> Dict:
        """Витягти дані з одного твіта"""
        try:
            # Спробуємо знайти текст твіта
            text_selectors = [
                '[data-testid="tweetText"]',
                '[dir="auto"]',
                '.tweet-text',
                'div[role="button"]'
            ]
            
            text = ""
            for selector in text_selectors:
                try:
                    text_element = element.find_element(By.CSS_SELECTOR, selector)
                    text = text_element.text.strip()
                    if text:
                        break
                except NoSuchElementException:
                    continue
            
            # Якщо не знайшли текст, спробуємо з усього елемента
            if not text:
                text = element.text.strip()
            
            # Спробуємо знайти ID твіта
            tweet_id = f"selenium_{index}_{int(time.time())}"
            
            # Спробуємо знайти посилання на твіт
            tweet_url = f"https://x.com/{self.username}"
            try:
                link_element = element.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
                href = link_element.get_attribute('href')
                if href:
                    tweet_url = href
                    # Витягуємо ID з URL
                    if '/status/' in href:
                        tweet_id = href.split('/status/')[-1].split('?')[0]
            except NoSuchElementException:
                pass
            
            # Фільтруємо короткі або порожні тексти
            if len(text) < 5:
                return None
            
            return {
                'id': tweet_id,
                'text': text,
                'url': tweet_url,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.debug(f"Помилка витягування даних твіта: {e}")
            return None
            
    async def _check_for_new_posts(self):
        """Перевірити нові пости"""
        try:
            # Оновлюємо сторінку
            print("🔄 Оновлюємо сторінку...")
            self.driver.refresh()
            await asyncio.sleep(3)
            
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
    monitor = SeleniumPilkXzMonitor()
    
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
    print("🐦 Selenium монітор профілю @pilk_xz")
    print("=" * 45)
    print("⚠️ Переконайтеся, що у вас встановлений Chrome та ChromeDriver")
    print("📦 Встановіть залежності: pip install selenium")
    print("=" * 45)
    asyncio.run(main())