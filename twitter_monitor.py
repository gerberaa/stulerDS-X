import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
import json
import re
import random
import ssl
import urllib3
from urllib.parse import urlparse, parse_qs

# Відключаємо попередження про SSL сертифікати
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TwitterMonitor:
    """Моніторинг Twitter/X акаунтів через автентифіковані API запити"""
    
    def __init__(self, auth_token: str = None, csrf_token: str = None):
        self.auth_token = auth_token
        self.csrf_token = csrf_token
        self.session = None
        self.monitoring_accounts = set()
        self.last_tweet_ids = {}  # account -> last_tweet_id
        self.sent_tweets = {}  # account -> set of sent tweet_ids
        self.seen_tweets = {}  # account -> set of seen tweet_ids
        self.logger = logging.getLogger(__name__)
        self.seen_tweets_file = "twitter_api_seen_tweets.json"
        
        # Завантажуємо збережені seen_tweets
        self.load_seen_tweets()
        
    async def __aenter__(self):
        """Асинхронний контекстний менеджер"""
        if self.auth_token:
            # Формуємо cookies для автентифікації
            cookies = {
                'auth_token': self.auth_token,
                'ct0': self.csrf_token or 'default_csrf_token'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'uk,en-US;q=0.9,en;q=0.8,ru;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
                'Content-Type': 'application/json',
                'Referer': 'https://x.com/',
                'X-Csrf-Token': self.csrf_token or 'default_csrf_token',
                'X-Twitter-Active-User': 'yes',
                'X-Twitter-Auth-Type': 'OAuth2Session'
            }
            
            timeout = aiohttp.ClientTimeout(total=15)
            
            # Налаштування SSL для обходу проблем з сертифікатами
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(
                headers=headers, 
                cookies=cookies, 
                timeout=timeout,
                connector=connector
            )
            self.logger.info("Twitter моніторинг ініціалізовано з auth_token та SSL налаштуваннями")
        else:
            self.logger.warning("Twitter auth_token не встановлено! Twitter моніторинг буде відключено")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрити сесію"""
        if self.session:
            await self.session.close()
            
    def add_account(self, username: str) -> bool:
        """Додати акаунт для моніторингу"""
        try:
            # Очищаємо username від @ та зайвих символів
            clean_username = username.replace('@', '').strip()
            if clean_username:
                self.monitoring_accounts.add(clean_username)
                # Ініціалізуємо множину відправлених твітів для нового акаунта
                if clean_username not in self.sent_tweets:
                    self.sent_tweets[clean_username] = set()
                # Ініціалізуємо множину оброблених твітів для нового акаунта
                if clean_username not in self.seen_tweets:
                    self.seen_tweets[clean_username] = set()
                self.logger.info(f"Додано акаунт для моніторингу: {clean_username}")
                return True
        except Exception as e:
            self.logger.error(f"Помилка додавання акаунта {username}: {e}")
        return False
        
    def remove_account(self, username: str) -> bool:
        """Видалити акаунт з моніторингу"""
        try:
            clean_username = username.replace('@', '').strip()
            if clean_username in self.monitoring_accounts:
                self.monitoring_accounts.remove(clean_username)
                if clean_username in self.last_tweet_ids:
                    del self.last_tweet_ids[clean_username]
                if clean_username in self.sent_tweets:
                    del self.sent_tweets[clean_username]
                if clean_username in self.seen_tweets:
                    del self.seen_tweets[clean_username]
                # Зберігаємо зміни
                self.save_seen_tweets()
                self.logger.info(f"Видалено акаунт з моніторингу: {clean_username}")
                return True
        except Exception as e:
            self.logger.error(f"Помилка видалення акаунта {username}: {e}")
        return False
        
    def get_monitoring_accounts(self) -> List[str]:
        """Отримати список акаунтів для моніторингу"""
        return list(self.monitoring_accounts)
        
    async def get_user_tweets(self, username: str, limit: int = 5) -> List[Dict]:
        """Отримати твіти користувача через Twitter API"""
        if not self.session:
            return []
            
        try:
            # Спочатку спробуємо отримати твіти через GraphQL API
            user_id = await self._get_user_id_by_username(username)
            if user_id:
                # Використовуємо знайдений GraphQL endpoint для твітів користувача
                url = "https://x.com/i/api/graphql/9jV-614Qopr4Eg6_JNNoqQ"
                params = {
                    'variables': json.dumps({
                        'userId': user_id,
                        'count': limit,
                        'includePromotedContent': True,
                        'withQuickPromoteEligibilityTweetFields': True,
                        'withVoice': True
                    }),
                    'features': json.dumps({
                        'rweb_video_screen_enabled': False,
                        'payments_enabled': False,
                        'profile_label_improvements_pcf_label_in_post_enabled': True,
                        'rweb_tipjar_consumption_enabled': True,
                        'verified_phone_label_enabled': False,
                        'creator_subscriptions_tweet_preview_api_enabled': True,
                        'responsive_web_graphql_timeline_navigation_enabled': True,
                        'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
                        'premium_content_api_read_enabled': False,
                        'communities_web_enable_tweet_community_results_fetch': True,
                        'c9s_tweet_anatomy_moderator_badge_enabled': True,
                        'responsive_web_grok_analyze_button_fetch_trends_enabled': False,
                        'responsive_web_grok_analyze_post_followups_enabled': True,
                        'responsive_web_jetfuel_frame': True,
                        'responsive_web_grok_share_attachment_enabled': True,
                        'articles_preview_enabled': True,
                        'responsive_web_edit_tweet_api_enabled': True,
                        'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
                        'view_counts_everywhere_api_enabled': True,
                        'longform_notetweets_consumption_enabled': True,
                        'responsive_web_twitter_article_tweet_consumption_enabled': True,
                        'tweet_awards_web_tipping_enabled': False,
                        'responsive_web_grok_show_grok_translated_post': False,
                        'responsive_web_grok_analysis_button_from_backend': False,
                        'creator_subscriptions_quote_tweet_preview_enabled': False,
                        'freedom_of_speech_not_reach_fetch_enabled': True,
                        'standardized_nudges_misinfo': True,
                        'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
                        'longform_notetweets_rich_text_read_enabled': True,
                        'longform_notetweets_inline_media_enabled': True,
                        'responsive_web_grok_image_annotation_enabled': True,
                        'responsive_web_grok_imagine_annotation_enabled': True,
                        'responsive_web_grok_community_note_auto_translation_is_enabled': False,
                        'responsive_web_enhance_cards_enabled': False
                    }),
                    'fieldToggles': json.dumps({
                        'withArticlePlainText': False
                    })
                }
                
                async with self.session.post(url, json=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tweets = self._parse_api_response(data, username)
                        return tweets[:limit]
                    elif response.status == 401:
                        self.logger.error("Unauthorized: неправильний auth_token")
                    elif response.status == 403:
                        self.logger.error("Forbidden: немає доступу до акаунта")
                    elif response.status == 429:
                        self.logger.warning("Rate limited: занадто багато запитів")
                    else:
                        self.logger.error(f"Помилка отримання твітів {username}: {response.status}")
                        # Fallback до HTML парсингу якщо API не працює
                        self.logger.info(f"API не працює для {username}, використовуємо HTML парсинг")
                        return await self._get_tweets_from_html(username, limit)
            else:
                # Якщо user_id не отримано, використовуємо HTML парсинг
                self.logger.info(f"User_id не отримано для {username}, використовуємо HTML парсинг")
                return await self._get_tweets_from_html(username, limit)
                
        except Exception as e:
            self.logger.error(f"Помилка запиту до Twitter API для {username}: {e}")
            # Fallback до HTML парсингу
            try:
                return await self._get_tweets_from_html(username, limit)
            except Exception as html_error:
                self.logger.error(f"Помилка HTML парсингу для {username}: {html_error}")
                return []
            
    async def _get_user_id_by_username(self, username: str) -> str:
        """Отримати user_id за username через GraphQL"""
        try:
            # Використовуємо знайдений GraphQL endpoint для отримання user_id
            url = "https://x.com/i/api/graphql/7mjxD3-C6BxitZR0F6X0aQ"
            params = {
                'variables': json.dumps({
                    'screen_name': username,
                    'withSafetyModeUserFields': True
                }),
                'features': json.dumps({
                    'hidden_profile_likes_enabled': True,
                    'hidden_profile_subscriptions_enabled': True,
                    'responsive_web_graphql_exclude_directive_enabled': True,
                    'verified_phone_label_enabled': False,
                    'subscriptions_verification_info_is_identity_verified_enabled': True,
                    'subscriptions_verification_info_verified_since_enabled': True,
                    'highlights_tweets_tab_ui_enabled': True,
                    'responsive_web_twitter_article_tweet_consumption_enabled': False,
                    'creator_subscriptions_tweet_preview_api_enabled': True,
                    'responsive_web_graphql_timeline_navigation_enabled': True,
                    'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
                    'c9s_tweet_anatomy_moderator_badge_enabled': True,
                    'tweetypie_unmention_optimization_enabled': True,
                    'responsive_web_edit_tweet_api_enabled': True,
                    'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
                    'view_counts_everywhere_api_enabled': True,
                    'longform_notetweets_consumption_enabled': True,
                    'responsive_web_twitter_article_tweet_consumption_enabled': False,
                    'tweet_awards_web_tipping_enabled': False,
                    'freedom_of_speech_not_reach_fetch_enabled': True,
                    'standardized_nudges_misinfo': True,
                    'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
                    'longform_notetweets_rich_text_read_enabled': True,
                    'longform_notetweets_inline_media_enabled': True,
                    'responsive_web_media_download_video_enabled': False,
                    'responsive_web_enhance_cards_enabled': False
                })
            }
            
            async with self.session.post(url, json=params) as response:
                if response.status == 200:
                    data = await response.json()
                    user_data = data.get('data', {}).get('user', {}).get('result', {})
                    user_id = user_data.get('rest_id')
                    if user_id:
                        self.logger.info(f"Отримано user_id {user_id} для {username}")
                        return str(user_id)
                    else:
                        self.logger.error(f"User_id не знайдено в відповіді для {username}")
                        return None
                elif response.status == 404:
                    self.logger.warning(f"Акаунт {username} не знайдено (404), використовуємо HTML парсинг")
                    return None
                elif response.status == 401:
                    self.logger.warning(f"Unauthorized для {username}, використовуємо HTML парсинг")
                    return None
                else:
                    self.logger.warning(f"Помилка отримання user_id для {username}: {response.status}, використовуємо HTML парсинг")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Помилка запиту user_id для {username}: {e}")
            return None
            
    async def _get_tweets_from_html(self, username: str, limit: int = 5) -> List[Dict]:
        """Отримати твіти через HTML парсинг (fallback метод)"""
        try:
            # Використовуємо requests для HTML запитів (синхронно)
            import requests
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            url = f"https://x.com/{username}"
            
            # Налаштування SSL для requests
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            response = requests.get(url, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                html = response.text
                return self._parse_tweets_from_html(html, username)[:limit]
            else:
                self.logger.error(f"Помилка завантаження HTML для {username}: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Помилка HTML парсингу для {username}: {e}")
            return []
            
    def _parse_api_response(self, data: Dict, username: str) -> List[Dict]:
        """Парсинг відповіді Twitter API"""
        tweets = []
        
        try:
            # Логуємо структуру відповіді для дебагу
            self.logger.info(f"API відповідь для {username}: {json.dumps(data, indent=2)[:500]}...")
            
            # Шукаємо твіти в GraphQL структурі відповіді
            if 'data' in data and 'user' in data['data']:
                user_data = data['data']['user']
                if 'result' in user_data and 'timeline_v2' in user_data['result']:
                    timeline = user_data['result']['timeline_v2']['timeline']
                    instructions = timeline.get('instructions', [])
                else:
                    instructions = []
            else:
                instructions = data.get('timeline', {}).get('instructions', [])
            
            for instruction in instructions:
                if instruction.get('type') == 'TimelineAddEntries':
                    entries = instruction.get('entries', [])
                    
                    for entry in entries:
                        if entry.get('type') == 'TimelineTimelineItem':
                            content = entry.get('content', {})
                            
                            if content.get('entryType') == 'TimelineTimelineItem':
                                item_content = content.get('itemContent', {})
                                tweet_data = item_content.get('tweet_results', {}).get('result', {})
                                
                                if tweet_data.get('__typename') == 'Tweet':
                                    tweet_id = tweet_data.get('rest_id', '')
                                    text = tweet_data.get('legacy', {}).get('full_text', '')
                                    created_at = tweet_data.get('legacy', {}).get('created_at', '')
                                    user_data = tweet_data.get('core', {}).get('user_results', {}).get('result', {})
                                    
                                    if text and tweet_id:
                                        tweets.append({
                                            'id': tweet_id,
                                            'text': text,
                                            'created_at': created_at,
                                            'user': {
                                                'screen_name': username,
                                                'name': user_data.get('legacy', {}).get('name', username)
                                            },
                                            'url': f"https://twitter.com/{username}/status/{tweet_id}"
                                        })
                                        
        except Exception as e:
            self.logger.error(f"Помилка парсингу API відповіді: {e}")
            
        return tweets
        
    def _parse_tweets_from_html(self, html: str, username: str) -> List[Dict]:
        """Покращений парсинг твітів з HTML"""
        tweets = []
        
        try:
            # Різні паттерни для пошуку JSON даних
            json_patterns = [
                r'<script[^>]*>.*?window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'<script[^>]*>.*?window\.__INITIAL_DATA__\s*=\s*({.*?});',
                r'<script[^>]*>.*?window\.__INITIAL_REDUX_STATE__\s*=\s*({.*?});',
                r'"timeline":\s*({.*?})',
                r'"tweets":\s*(\[.*?\])',
                r'"statuses":\s*(\[.*?\])',
                r'<script[^>]*>.*?window\.__INITIAL_CONTEXT__\s*=\s*({.*?});',
                r'<script[^>]*>.*?window\.__INITIAL_PROPS__\s*=\s*({.*?});'
            ]
            
            found_data = False
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    try:
                        json_data = json.loads(match)
                        parsed_tweets = self._extract_tweets_from_json(json_data, username)
                        tweets.extend(parsed_tweets)
                        found_data = True
                        self.logger.info(f"Знайдено JSON дані в HTML для {username}: {len(parsed_tweets)} твітів")
                    except json.JSONDecodeError:
                        continue
            
            # Якщо не знайшли JSON, використовуємо HTML парсинг
            if not found_data:
                tweets = self._basic_html_parsing(html, username)
                self.logger.info(f"HTML парсинг для {username}: знайдено {len(tweets)} твітів")
                
        except Exception as e:
            self.logger.error(f"Помилка парсингу HTML для {username}: {e}")
            
        return tweets
        
    def _extract_tweets_from_json(self, json_data: Dict, username: str) -> List[Dict]:
        """Покращене витягування твітів з JSON даних"""
        tweets = []
        
        try:
            # Рекурсивно шукаємо твіти в JSON структурі
            def find_tweets_recursive(obj, path=""):
                if isinstance(obj, dict):
                    # Шукаємо структури твітів
                    if 'id_str' in obj and 'text' in obj:
                        tweet = {
                            'id': obj.get('id_str', ''),
                            'text': obj.get('text', ''),
                            'created_at': obj.get('created_at', ''),
                            'user': {
                                'screen_name': obj.get('user', {}).get('screen_name', username),
                                'name': obj.get('user', {}).get('name', username)
                            },
                            'url': f"https://twitter.com/{username}/status/{obj.get('id_str', '')}"
                        }
                        tweets.append(tweet)
                    
                    # Шукаємо в підструктурах
                    for key, value in obj.items():
                        find_tweets_recursive(value, f"{path}.{key}")
                        
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        find_tweets_recursive(item, f"{path}[{i}]")
            
            find_tweets_recursive(json_data)
            
            # Якщо не знайшли через рекурсію, спробуємо відомі структури
            if not tweets:
                # Структура Twitter API v1.1
                if 'statuses' in json_data:
                    for tweet_data in json_data['statuses']:
                        tweets.append({
                            'id': tweet_data.get('id_str', ''),
                            'text': tweet_data.get('text', ''),
                            'created_at': tweet_data.get('created_at', ''),
                            'user': {
                                'screen_name': tweet_data.get('user', {}).get('screen_name', username),
                                'name': tweet_data.get('user', {}).get('name', username)
                            },
                            'url': f"https://twitter.com/{username}/status/{tweet_data.get('id_str', '')}"
                        })
                
                # Структура Twitter API v2
                elif 'data' in json_data:
                    for tweet_data in json_data['data']:
                        tweets.append({
                            'id': tweet_data.get('id', ''),
                            'text': tweet_data.get('text', ''),
                            'created_at': tweet_data.get('created_at', ''),
                            'user': {
                                'screen_name': username,
                                'name': username
                            },
                            'url': f"https://twitter.com/{username}/status/{tweet_data.get('id', '')}"
                        })
                
                # Структура з entities
                elif 'entities' in json_data:
                    entities = json_data['entities']
                    if 'tweets' in entities:
                        for tweet_id, tweet_data in entities['tweets'].items():
                            tweets.append({
                                'id': tweet_id,
                                'text': tweet_data.get('full_text', ''),
                                'created_at': tweet_data.get('created_at', ''),
                                'user': {
                                    'screen_name': username,
                                    'name': tweet_data.get('user', {}).get('name', username)
                                },
                                'url': f"https://twitter.com/{username}/status/{tweet_id}"
                            })
            
        except Exception as e:
            self.logger.error(f"Помилка витягування твітів з JSON: {e}")
            
        return tweets
        
    def _basic_html_parsing(self, html: str, username: str) -> List[Dict]:
        """Покращений парсинг HTML для твітів"""
        tweets = []
        
        try:
            # Різні паттерни для пошуку твітів
            tweet_patterns = [
                r'<article[^>]*data-testid="tweet"[^>]*>(.*?)</article>',
                r'<div[^>]*data-testid="tweet"[^>]*>(.*?)</div>',
                r'<div[^>]*class="[^"]*tweet[^"]*"[^>]*>(.*?)</div>',
                r'data-tweet-id="(\d+)"[^>]*>(.*?)</div>',
                r'tweet_id=(\d+).*?>(.*?)<'
            ]
            
            for pattern in tweet_patterns:
                tweet_matches = re.findall(pattern, html, re.DOTALL)
                
                for i, match in enumerate(tweet_matches[:10]):  # Максимум 10 твітів
                    tweet_html = match if isinstance(match, str) else match[1]
                    tweet_id = match[0] if isinstance(match, tuple) and len(match) > 1 else f"html_{username}_{i}_{int(datetime.now().timestamp())}"
                    
                    # Різні паттерни для тексту твіта
                    text_patterns = [
                        r'<div[^>]*dir="auto"[^>]*>(.*?)</div>',
                        r'<div[^>]*class="[^"]*tweet-text[^"]*"[^>]*>(.*?)</div>',
                        r'<span[^>]*class="[^"]*tweet-text[^"]*"[^>]*>(.*?)</span>',
                        r'<p[^>]*>(.*?)</p>',
                        r'data-testid="tweetText"[^>]*>(.*?)</div>'
                    ]
                    
                    text = ""
                    for text_pattern in text_patterns:
                        text_match = re.search(text_pattern, tweet_html, re.DOTALL)
                        if text_match:
                            text = re.sub(r'<[^>]+>', '', text_match.group(1))  # Видаляємо HTML теги
                            text = text.strip()
                            break
                    
                    # Якщо не знайшли текст, спробуємо витягти з усього блоку
                    if not text:
                        text = re.sub(r'<[^>]+>', '', tweet_html)
                        text = text.strip()
                    
                    # Очищаємо текст від зайвих символів
                    text = re.sub(r'\s+', ' ', text)  # Замінюємо множинні пробіли на один
                    text = text.strip()
                    
                    if text and len(text) > 10:  # Фільтруємо короткі тексти
                        # Спробуємо знайти реальний tweet_id
                        real_tweet_id = tweet_id
                        if isinstance(match, tuple) and len(match) > 1:
                            real_tweet_id = match[0]
                        
                        # Генеруємо стабільний ID на основі тексту якщо немає реального ID
                        if not real_tweet_id.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')):
                            # Створюємо стабільний хеш на основі тексту та username (без часу для стабільності)
                            import hashlib
                            content_for_hash = f"{username}_{text}".encode('utf-8')
                            text_hash = hashlib.md5(content_for_hash).hexdigest()[:16]
                            real_tweet_id = f"html_{text_hash}"
                        
                        tweets.append({
                            'id': real_tweet_id,
                            'text': text,
                            'created_at': datetime.now().isoformat(),
                            'user': {
                                'screen_name': username,
                                'name': username
                            },
                            'url': f"https://twitter.com/{username}/status/{real_tweet_id}" if real_tweet_id.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')) else f"https://twitter.com/{username}"
                        })
                
                if tweets:  # Якщо знайшли твіти з цим паттерном, зупиняємося
                    break
                        
        except Exception as e:
            self.logger.error(f"Помилка базового HTML парсингу: {e}")
            
        return tweets
        
    async def check_new_tweets(self) -> List[Dict]:
        """Перевірити нові твіти у всіх акаунтах"""
        new_tweets = []
        
        for i, username in enumerate(self.monitoring_accounts):
            try:
                # Додаємо затримку між запитами до різних акаунтів
                if i > 0:
                    await asyncio.sleep(2)  # 2 секунди між акаунтами
                    
                # Отримуємо твіти
                tweets = await self.get_user_tweets(username, limit=5)
                if not tweets:
                    continue
                
                # Ініціалізуємо множини якщо не існують
                if username not in self.sent_tweets:
                    self.sent_tweets[username] = set()
                if username not in self.seen_tweets:
                    self.seen_tweets[username] = set()
                    
                # Знаходимо нові твіти
                last_id = self.last_tweet_ids.get(username)
                
                # Якщо це перша перевірка - зберігаємо останній твіт як базовий
                if last_id is None:
                    if tweets:
                        self.last_tweet_ids[username] = tweets[0]['id']
                        # Додаємо всі поточні твіти до відправлених та оброблених (щоб не спамити при першому запуску)
                        for tweet in tweets:
                            self.sent_tweets[username].add(tweet['id'])
                            self.seen_tweets[username].add(tweet['id'])
                        # Зберігаємо зміни
                        self.save_seen_tweets()
                    continue
                    
                # Шукаємо нові твіти
                found_new = False
                for tweet in tweets:
                    tweet_id = tweet['id']
                    tweet_text = tweet.get('text', '').strip()
                    
                    # Перевіряємо чи цей твіт вже був оброблений
                    if tweet_id in self.seen_tweets[username]:
                        continue
                    
                    # Перевіряємо чи цей твіт вже був відправлений за ID
                    if tweet_id in self.sent_tweets[username]:
                        continue
                    
                    # Додаткова перевірка за контентом
                    if tweet_text:
                        import hashlib
                        content_hash = hashlib.md5(f"{username}_{tweet_text}".encode('utf-8')).hexdigest()[:12]
                        content_key = f"content_{content_hash}"
                        if content_key in self.sent_tweets[username]:
                            self.logger.info(f"Контент твіта для {username} вже був відправлений, пропускаємо")
                            continue
                    
                    # Якщо знайшли останній відомий твіт - зупиняємося
                    if tweet_id == last_id:
                        break
                        
                    # Це новий твіт
                    found_new = True
                    new_tweets.append({
                        'account': username,
                        'tweet_id': tweet_id,
                        'text': tweet.get('text', ''),
                        'author': tweet.get('user', {}).get('name', username),
                        'username': username,
                        'timestamp': tweet.get('created_at', ''),
                        'url': tweet.get('url', f"https://twitter.com/{username}")
                    })
                    
                    # Додаємо твіт до оброблених та відправлених
                    self.seen_tweets[username].add(tweet_id)
                    self.sent_tweets[username].add(tweet_id)
                    
                    # Додаємо хеш контенту до відправлених
                    if tweet_text:
                        import hashlib
                        content_hash = hashlib.md5(f"{username}_{tweet_text}".encode('utf-8')).hexdigest()[:12]
                        content_key = f"content_{content_hash}"
                        self.sent_tweets[username].add(content_key)
                    
                # Діагностичне логування
                if found_new:
                    self.logger.info(f"Акаунт {username}: знайдено нові твіти, останній відомий: {last_id}")
                    
                # Оновлюємо останній твіт на найновіший
                if tweets:
                    self.last_tweet_ids[username] = tweets[0]['id']
                    
            except Exception as e:
                self.logger.error(f"Помилка перевірки акаунта {username}: {e}")
        
        # Зберігаємо оброблені твіти після кожної перевірки
        if new_tweets:
            self.save_seen_tweets()
                
        return new_tweets
        
    async def start_monitoring(self, callback_func, interval: int = 30):
        """Запустити моніторинг з callback функцією"""
        self.logger.info(f"Запуск моніторингу Twitter акаунтів (інтервал: {interval}с)")
        
        while True:
            try:
                new_tweets = await self.check_new_tweets()
                
                if new_tweets:
                    self.logger.info(f"Знайдено {len(new_tweets)} нових твітів")
                    if asyncio.iscoroutinefunction(callback_func):
                        await callback_func(new_tweets)
                    else:
                        callback_func(new_tweets)
                        
                # Додаємо випадкову затримку для уникнення підозрілої активності
                random_delay = random.uniform(1.0, 3.0)
                await asyncio.sleep(interval + random_delay)
                
            except Exception as e:
                self.logger.error(f"Помилка в циклі моніторингу Twitter: {e}")
                # При помилці чекаємо довше
                await asyncio.sleep(interval * 2)
                
    def format_tweet_notification(self, tweet: Dict) -> str:
        """Форматувати сповіщення про новий твіт"""
        try:
            # Екрануємо спеціальні символи для Markdown
            author = self._escape_markdown(tweet.get('author', 'Unknown'))
            text = self._escape_markdown(tweet.get('text', '')[:200])  # Обмежуємо довжину
            username = tweet.get('username', '')
            
            if len(tweet.get('text', '')) > 200:
                text += '...'
                
            notification = (
                f"🐦 **Новий твіт з Twitter**\n\n"
                f"👤 Автор: {author} (@{username})\n"
                f"📝 Текст: {text}\n"
                f"🔗 [Перейти до твіта]({tweet.get('url', '')})\n\n"
                f"⏰ {tweet.get('timestamp', 'Невідомо')[:19] if tweet.get('timestamp') else 'Невідомо'}"
            )
            
            return notification
            
        except Exception as e:
            self.logger.error(f"Помилка форматування сповіщення: {e}")
            return f"🐦 Новий твіт від {tweet.get('username', 'Unknown')}"
            
    def _escape_markdown(self, text: str) -> str:
        """Екранувати спеціальні символи Markdown"""
        if not text:
            return ""
            
        # Список символів, які потрібно екранувати в Markdown
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
            
        return text
    
    def save_seen_tweets(self):
        """Зберегти список оброблених твітів"""
        try:
            import json
            # Конвертуємо set у list для JSON серіалізації
            data_to_save = {}
            for account, tweet_ids in self.seen_tweets.items():
                if isinstance(tweet_ids, set):
                    data_to_save[account] = list(tweet_ids)
                else:
                    data_to_save[account] = tweet_ids
            
            with open(self.seen_tweets_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Збережено seen_tweets для {len(data_to_save)} акаунтів")
            return True
        except Exception as e:
            self.logger.error(f"Помилка збереження seen_tweets: {e}")
            return False
    
    def load_seen_tweets(self):
        """Завантажити список оброблених твітів"""
        try:
            import json
            import os
            if os.path.exists(self.seen_tweets_file):
                with open(self.seen_tweets_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Конвертуємо list назад у set
                for account, tweet_ids in data.items():
                    if isinstance(tweet_ids, list):
                        self.seen_tweets[account] = set(tweet_ids)
                    else:
                        self.seen_tweets[account] = set()
                
                self.logger.info(f"Завантажено seen_tweets для {len(self.seen_tweets)} акаунтів")
            else:
                self.logger.info("Файл twitter_api_seen_tweets.json не знайдено, починаємо з порожнього списку")
        except Exception as e:
            self.logger.error(f"Помилка завантаження seen_tweets: {e}")
            self.seen_tweets = {}