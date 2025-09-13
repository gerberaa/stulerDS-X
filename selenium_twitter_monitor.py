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
        
        # Автоматично ініціалізуємо драйвер
        self._setup_driver(headless=True)
        
    def _check_chrome_installation(self) -> bool:
        """Перевірити чи встановлений Chrome"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                # Для Windows перевіряємо через reg
                try:
                    result = subprocess.run(['reg', 'query', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe'], 
                                         capture_output=True, text=True, timeout=5)
                    return result.returncode == 0
                except:
                    # Альтернативний спосіб для Windows
                    chrome_paths = [
                        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
                    ]
                    return any(os.path.exists(path) for path in chrome_paths)
            else:
                # Для Linux/Mac
                try:
                    result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True, timeout=5)
                    return result.returncode == 0
                except:
                    try:
                        result = subprocess.run(['chrome', '--version'], capture_output=True, text=True, timeout=5)
                        return result.returncode == 0
                    except:
                        return False
        except:
            return False
    
    def _setup_driver(self, headless: bool = False) -> bool:
        """Налаштувати Chrome драйвер з профілем"""
        try:
            # Перевіряємо чи встановлений Chrome
            if not self._check_chrome_installation():
                logger.warning("Chrome браузер не знайдено в системі, але спробуємо продовжити...")
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
            
            # Налаштування для підтримки зображень
            prefs = {
                "profile.managed_default_content_settings.images": 1,  # Дозволити зображення
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.media_stream": 1
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Режим без головки
            if headless:
                chrome_options.add_argument('--headless')
            
            # Спробуємо використати автоматичний ChromeDriver
            try:
                self.driver = webdriver.Chrome(options=chrome_options)
                logger.info("Chrome драйвер успішно ініціалізовано (автоматичний)")
            except Exception as e:
                logger.warning(f"Не вдалося використати автоматичний ChromeDriver: {e}")
                # Спробуємо знайти ChromeDriver в поточній папці
                if os.path.exists("chromedriver.exe"):
                    try:
                        service = Service("chromedriver.exe")
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        logger.info("Chrome драйвер успішно ініціалізовано (локальний)")
                    except Exception as e2:
                        logger.error(f"Не вдалося використати локальний ChromeDriver: {e2}")
                        raise Exception(f"ChromeDriver не працює: {e2}")
                else:
                    logger.error("ChromeDriver не знайдено в поточній папці")
                    raise Exception("ChromeDriver не знайдено")
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome драйвер успішно ініціалізовано")
            return True
            
        except Exception as e:
            logger.error(f"Помилка ініціалізації Chrome драйвера: {e}")
            self.driver = None
            return False
    
    def close_driver(self):
        """Закрити драйвер"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium драйвер закрито")
            except Exception as e:
                logger.error(f"Помилка закриття драйвера: {e}")
            finally:
                self.driver = None
    
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
            
            # Для кожного твіта з зображеннями відкриваємо його окремо для кращого витягування фото
            enhanced_tweets = []
            for tweet in tweets[:limit]:
                if tweet.get('images'):
                    # Вже є зображення, додаємо як є
                    enhanced_tweets.append(tweet)
                else:
                    # Спробуємо відкрити твіт окремо для витягування фото
                    enhanced_tweet = await self._enhance_tweet_with_images(tweet)
                    enhanced_tweets.append(enhanced_tweet)
            
            return enhanced_tweets
            
        except Exception as e:
            logger.error(f"Помилка отримання твітів для {username}: {e}")
            return []
    
    async def _enhance_tweet_with_images(self, tweet: Dict) -> Dict:
        """Відкрити твіт окремо для кращого витягування зображень"""
        try:
            tweet_url = tweet.get('url')
            if not tweet_url:
                return tweet
            
            logger.debug(f"Відкриваємо твіт для витягування фото: {tweet_url}")
            
            # Відкриваємо твіт в новій вкладці
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Переходимо на сторінку твіта
            self.driver.get(tweet_url)
            await asyncio.sleep(3)  # Чекаємо завантаження
            
            # Шукаємо зображення в відкритому твіті
            images = self._extract_images_from_opened_tweet()
            
            # Закриваємо вкладку та повертаємося до основної
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            # Додаємо зображення до твіта
            if images:
                tweet['images'] = images
                logger.info(f"Знайдено {len(images)} зображень в відкритому твіті")
            
            return tweet
            
        except Exception as e:
            logger.debug(f"Помилка відкриття твіта для витягування фото: {e}")
            # Повертаємося до основної вкладки якщо щось пішло не так
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            return tweet
    
    def _extract_images_from_opened_tweet(self) -> List[str]:
        """Витягти зображення з відкритого твіта"""
        images = []
        try:
            # Селектори для зображень в відкритому твіті
            selectors = [
                '[data-testid="tweetPhoto"] img',
                'div[data-testid="tweetPhoto"] img',
                '[data-testid="tweetPhoto"] div[style*="background-image"]',
                'div[data-testid="tweetPhoto"] div[style*="background-image"]',
                'article img[src*="media"]',
                'article img[src*="pbs.twimg.com/media"]'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Для img тегів
                        if element.tag_name == 'img':
                            src = element.get_attribute('src')
                            if src and self._is_tweet_image(src):
                                clean_url = self._clean_image_url(src)
                                if clean_url and clean_url not in images:
                                    images.append(clean_url)
                                    logger.debug(f"Знайдено зображення в відкритому твіті: {clean_url}")
                        
                        # Для div з background-image
                        else:
                            style = element.get_attribute('style')
                            if style and 'background-image' in style:
                                bg_url = self._extract_background_image_url(style)
                                if bg_url and self._is_tweet_image(bg_url):
                                    clean_url = self._clean_image_url(bg_url)
                                    if clean_url and clean_url not in images:
                                        images.append(clean_url)
                                        logger.debug(f"Знайдено background зображення: {clean_url}")
                
                except Exception as e:
                    continue
            
        except Exception as e:
            logger.debug(f"Помилка витягування зображень з відкритого твіта: {e}")
        
        return images
            
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
            
            # Витягуємо фото з твіта
            images = self._extract_tweet_images(element)
            
            # Фільтруємо короткі або порожні тексти (але дозволяємо твіти тільки з фото)
            if len(text) < 5 and not images:
                return None
            
            return {
                'id': tweet_id,
                'text': text,
                'url': tweet_url,
                'images': images,
                'created_at': datetime.now().isoformat(),
                'user': {
                    'screen_name': username,
                    'name': username
                }
            }
            
        except Exception as e:
            logger.debug(f"Помилка витягування даних твіта: {e}")
            return None
    
    def _extract_tweet_images(self, element) -> List[str]:
        """Витягти URL фото з твіта (тільки з поста, не аватарки)"""
        images = []
        try:
            # Селектори для зображень саме в твіті (не аватарки)
            tweet_image_selectors = [
                '[data-testid="tweetPhoto"] img',
                'div[data-testid="tweetPhoto"] img',
                '[data-testid="tweetPhoto"] div[style*="background-image"]',
                'div[data-testid="tweetPhoto"] div[style*="background-image"]',
                '[role="img"][data-testid="tweetPhoto"]',
                'div[data-testid="tweetPhoto"]',
                '[data-testid="tweetPhoto"]'
            ]
            
            # Спочатку шукаємо контейнери з зображеннями твіта
            tweet_photo_containers = []
            for selector in tweet_image_selectors:
                try:
                    containers = element.find_elements(By.CSS_SELECTOR, selector)
                    tweet_photo_containers.extend(containers)
                except Exception:
                    continue
            
            # Витягуємо зображення з контейнерів твіта
            for container in tweet_photo_containers:
                try:
                    # Шукаємо img теги в контейнері
                    img_elements = container.find_elements(By.TAG_NAME, 'img')
                    for img in img_elements:
                        src = img.get_attribute('src')
                        if src and self._is_tweet_image(src):
                            clean_url = self._clean_image_url(src)
                            if clean_url and clean_url not in images:
                                images.append(clean_url)
                                logger.debug(f"Знайдено зображення твіта: {clean_url}")
                    
                    # Шукаємо background-image в стилях
                    style = container.get_attribute('style')
                    if style and 'background-image' in style:
                        bg_url = self._extract_background_image_url(style)
                        if bg_url and self._is_tweet_image(bg_url):
                            clean_url = self._clean_image_url(bg_url)
                            if clean_url and clean_url not in images:
                                images.append(clean_url)
                                logger.debug(f"Знайдено зображення з background: {clean_url}")
                
                except Exception as e:
                    continue
            
            # Якщо знайшли зображення, логуємо
            if images:
                logger.info(f"Знайдено {len(images)} зображень в твіті")
                
        except Exception as e:
            logger.debug(f"Помилка витягування зображень: {e}")
            
        return images
    
    def _is_tweet_image(self, url: str) -> bool:
        """Перевірити чи це зображення з твіта (не аватарка)"""
        if not url:
            return False
        
        # Виключаємо аватарки та інші нерелевантні зображення
        exclude_patterns = [
            'profile_images',
            'avatar',
            'profile_pic',
            'default_profile',
            'default_profile_images',
            'normal.jpg',
            'bigger.jpg',
            'mini.jpg',
            '400x400',
            '200x200',
            '48x48'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url.lower():
                return False
        
        # Включаємо тільки медіа зображення
        include_patterns = [
            'media',
            'pbs.twimg.com/media',
            'ton.twimg.com/media'
        ]
        
        for pattern in include_patterns:
            if pattern in url.lower():
                return True
        
        return False
    
    def _clean_image_url(self, url: str) -> str:
        """Очистити URL зображення та додати параметри для кращого відображення"""
        if not url:
            return ""
        
        # Видаляємо параметри після ?
        clean_url = url.split('?')[0]
        
        # Видаляємо фрагменти після #
        clean_url = clean_url.split('#')[0]
        
        # Додаємо параметри для кращого відображення в браузері та Telegram
        if 'pbs.twimg.com/media/' in clean_url:
            clean_url += '?format=jpg&name=medium'
        
        return clean_url
    
    def _extract_background_image_url(self, style: str) -> str:
        """Витягти URL з background-image CSS стилю"""
        try:
            import re
            # Шукаємо url(...) в стилі
            match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
            if match:
                return match.group(1)
        except Exception:
            pass
        return ""
    
    async def check_new_tweets(self) -> List[Dict]:
        """Перевірити нові твіти для всіх акаунтів"""
        if not self.driver:
            logger.warning("Selenium драйвер не ініціалізовано, спробуємо ініціалізувати...")
            if not self._setup_driver(headless=True):
                logger.error("Не вдалося ініціалізувати Selenium драйвер")
                return []
            
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
            images = tweet.get('images', [])
            
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
            
            # Додаємо інформацію про зображення якщо є
            if images:
                notification += f"\n📷 Зображень: {len(images)}"
            
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