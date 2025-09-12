#!/usr/bin/env python3
"""
Selenium Twitter Monitor для інтеграції з ботом
"""

import asyncio
import logging
import time
import json
import os
from datetime import datetime
from typing import Set, List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SeleniumTwitterMonitor:
    """Selenium монітор для Twitter/X з підтримкою авторизації"""
    
    def __init__(self, profile_path: str = None):
        self.profile_path = profile_path or "./browser_profile"
        self.driver = None
        self.monitoring_accounts = set()
        self.seen_tweets = {}  # account -> set of tweet_ids
        self.monitoring_active = False
        
        # Створюємо папку профілю якщо не існує
        if not os.path.exists(self.profile_path):
            os.makedirs(self.profile_path)
            logger.info(f"Створено папку профілю: {self.profile_path}")
        
    def _setup_driver(self, headless: bool = False) -> bool:
        """Налаштувати Chrome драйвер з профілем"""
        try:
            chrome_options = Options()
            
            # Профіль браузера
            chrome_options.add_argument(f'--user-data-dir={os.path.abspath(self.profile_path)}')
            chrome_options.add_argument('--profile-directory=Default')
            
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
            
            # Режим без головки
            if headless:
                chrome_options.add_argument('--headless')
            
            # Спробуємо використати автоматичний ChromeDriver
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                logger.warning(f"Не вдалося використати автоматичний ChromeDriver: {e}")
                # Спробуємо знайти ChromeDriver в поточній папці
                if os.path.exists("chromedriver.exe"):
                    service = Service("chromedriver.exe")
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    raise Exception("ChromeDriver не знайдено")
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome драйвер успішно ініціалізовано")
            return True
            
        except Exception as e:
            logger.error(f"Помилка ініціалізації Chrome драйвера: {e}")
            return False
    
    async def __aenter__(self):
        """Асинхронний контекстний менеджер"""
        if self._setup_driver():
            logger.info("Selenium Twitter моніторинг ініціалізовано")
        else:
            logger.warning("Selenium Twitter моніторинг не вдалося ініціалізувати")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрити сесію"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium драйвер закрито")
            
    def add_account(self, username: str) -> bool:
        """Додати акаунт для моніторингу"""
        try:
            clean_username = username.replace('@', '').strip()
            if clean_username:
                self.monitoring_accounts.add(clean_username)
                if clean_username not in self.seen_tweets:
                    self.seen_tweets[clean_username] = set()
                logger.info(f"Додано акаунт для моніторингу: {clean_username}")
                return True
        except Exception as e:
            logger.error(f"Помилка додавання акаунта {username}: {e}")
        return False
        
    def get_monitoring_accounts(self) -> List[str]:
        """Отримати список акаунтів для моніторингу"""
        return list(self.monitoring_accounts)
        
    async def get_user_tweets(self, username: str, limit: int = 5) -> List[Dict]:
        """Отримати твіти користувача через Selenium"""
        if not self.driver:
            logger.error("Selenium драйвер не ініціалізовано")
            return []
            
        try:
            clean_username = username.replace('@', '').strip()
            url = f"https://x.com/{clean_username}"
            
            logger.info(f"Відкриваємо профіль: {url}")
            self.driver.get(url)
            
            # Чекаємо завантаження сторінки
            await asyncio.sleep(5)
            
            # Отримуємо твіти
            tweets = self._extract_tweets_from_page(clean_username)
            logger.info(f"Знайдено {len(tweets)} твітів для {clean_username}")
            
            return tweets[:limit]
            
        except Exception as e:
            logger.error(f"Помилка отримання твітів для {username}: {e}")
            return []
            
    def _extract_tweets_from_page(self, username: str) -> List[Dict]:
        """Витягти твіти з поточної сторінки"""
        tweets = []
        
        try:
            # Різні селектори для пошуку твітів
            selectors = [
                '[data-testid="tweet"]',
                'article[role="article"]',
                '[data-testid="tweetText"]',
                'div[data-testid="tweetText"]'
            ]
            
            tweet_elements = []
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        tweet_elements = elements
                        logger.info(f"Знайдено {len(elements)} елементів з селектором: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not tweet_elements:
                logger.warning("Твіти не знайдені")
                return []
            
            # Витягуємо дані з кожного твіта
            for i, element in enumerate(tweet_elements[:10]):  # Максимум 10 твітів
                try:
                    tweet_data = self._extract_tweet_data(element, username, i)
                    if tweet_data:
                        tweets.append(tweet_data)
                except Exception as e:
                    logger.debug(f"Помилка витягування даних твіта {i}: {e}")
                    continue
            
            return tweets
            
        except Exception as e:
            logger.error(f"Помилка витягування твітів: {e}")
            return []
            
    def _extract_tweet_data(self, element, username: str, index: int) -> Optional[Dict]:
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
            tweet_id = f"selenium_{username}_{index}_{int(time.time())}"
            
            # Спробуємо знайти посилання на твіт
            tweet_url = f"https://x.com/{username}"
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
                'created_at': datetime.now().isoformat(),
                'user': {
                    'screen_name': username,
                    'name': username
                }
            }
            
        except Exception as e:
            logger.debug(f"Помилка витягування даних твіта: {e}")
            return None
    
    async def check_new_tweets(self) -> List[Dict]:
        """Перевірити нові твіти для всіх акаунтів"""
        new_tweets = []
        
        for username in self.monitoring_accounts:
            try:
                tweets = await self.get_user_tweets(username, limit=5)
                
                for tweet in tweets:
                    tweet_id = tweet.get('id')
                    if tweet_id and tweet_id not in self.seen_tweets[username]:
                        new_tweets.append(tweet)
                        self.seen_tweets[username].add(tweet_id)
                        
            except Exception as e:
                logger.error(f"Помилка перевірки твітів для {username}: {e}")
                
        return new_tweets
    
    def format_tweet_notification(self, tweet: Dict) -> str:
        """Форматувати сповіщення про твіт"""
        try:
            username = tweet.get('user', {}).get('screen_name', 'unknown')
            name = tweet.get('user', {}).get('name', username)
            tweet_id = tweet.get('id', '')
            url = tweet.get('url', f"https://twitter.com/{username}/status/{tweet_id}")
            created_at = tweet.get('created_at', '')
            text = tweet.get('text', '')
            
            # Форматуємо дату
            try:
                from datetime import datetime
                if created_at:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%d %B, %H:%M UTC")
                    time_ago = self._get_time_ago(dt)
                else:
                    formatted_date = "Не відомо"
                    time_ago = ""
            except:
                formatted_date = created_at
                time_ago = ""
            
            # Обрізаємо текст якщо він занадто довгий
            if len(text) > 200:
                text = text[:200] + "..."
            
            notification = f"""🐦 **Новий твіт з Twitter**
• Профіль: @{username}
• Автор: {name}
• Дата: {formatted_date} ({time_ago})
• Текст: {text}
🔗 [Перейти до твіта]({url})"""
            
            return notification
            
        except Exception as e:
            logger.error(f"Помилка форматування сповіщення: {e}")
            return f"🐦 Новий твіт з Twitter: {tweet.get('text', 'Помилка форматування')}"
    
    def _get_time_ago(self, dt: datetime) -> str:
        """Отримати час тому"""
        try:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            
            # Переконуємося що dt має timezone
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            diff = now - dt
            
            total_seconds = int(diff.total_seconds())
            
            if total_seconds < 0:
                return "щойно"
            elif total_seconds < 60:
                return f"{total_seconds} секунд тому"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                return f"{minutes} хвилин тому"
            elif total_seconds < 86400:
                hours = total_seconds // 3600
                return f"{hours} годин тому"
            else:
                days = total_seconds // 86400
                return f"{days} днів тому"
        except Exception as e:
            logger.error(f"Помилка обчислення часу: {e}")
            return ""
    
    def open_manual_auth(self):
        """Відкрити браузер для ручної авторизації"""
        if not self.driver:
            if not self._setup_driver(headless=False):
                return False
        
        try:
            self.driver.get("https://x.com/login")
            logger.info("Відкрито сторінку авторизації Twitter")
            print("🔐 Відкрито браузер для авторизації")
            print("📝 Будь ласка, увійдіть в свій Twitter акаунт")
            print("⏳ Після авторизації натисніть Enter в консолі...")
            input("Натисніть Enter після завершення авторизації...")
            return True
        except Exception as e:
            logger.error(f"Помилка відкриття авторизації: {e}")
            return False
    
    def save_profile(self):
        """Зберегти профіль браузера"""
        try:
            # Профіль автоматично зберігається в папці profile_path
            logger.info(f"Профіль браузера збережено в: {self.profile_path}")
            return True
        except Exception as e:
            logger.error(f"Помилка збереження профілю: {e}")
            return False

# Приклад використання
async def main():
    """Приклад використання SeleniumTwitterMonitor"""
    async with SeleniumTwitterMonitor() as monitor:
        # Додаємо акаунт для моніторингу
        monitor.add_account("pilk_xz")
        
        # Отримуємо твіти
        tweets = await monitor.get_user_tweets("pilk_xz", limit=5)
        print(f"Знайдено {len(tweets)} твітів")
        
        # Перевіряємо нові твіти
        new_tweets = await monitor.check_new_tweets()
        print(f"Знайдено {len(new_tweets)} нових твітів")

if __name__ == "__main__":
    asyncio.run(main())