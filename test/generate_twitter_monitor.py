#!/usr/bin/env python3
"""
Generate Twitter Monitor Code
Генерує оновлений код для twitter_monitor.py з усіма знайденими endpoints
"""

import json
from datetime import datetime

def generate_twitter_monitor_code():
    """Генерувати код для twitter_monitor.py"""
    
    # Знайдені endpoints
    endpoints = {
        'user_tweets': 'https://x.com/i/api/graphql/9jV-614Qopr4Eg6_JNNoqQ',
        'user_by_screen_name': 'https://x.com/i/api/graphql/7mjxD3-C6BxitZR0F6X0aQ',
        'tweet_detail': 'https://x.com/i/api/graphql/ikU9DgZwhNIWqqFheO2NWA',
    }
    
    code = f'''#!/usr/bin/env python3
"""
Twitter Monitor - Оновлена версія з автоматично знайденими endpoints
Згенеровано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import asyncio
import aiohttp
import json
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Автоматично знайдені endpoints
TWITTER_ENDPOINTS = {{
    "user_tweets": "{endpoints['user_tweets']}",
    "user_by_screen_name": "{endpoints['user_by_screen_name']}",
    "tweet_detail": "{endpoints['tweet_detail']}",
}}

class TwitterMonitor:
    """Моніторинг Twitter/X акаунтів"""
    
    def __init__(self, auth_token: str = None, csrf_token: str = None):
        self.auth_token = auth_token
        self.csrf_token = csrf_token
        self.session = None
        self.monitoring_accounts = set()
        self.sent_tweets = set()  # Для запобігання дублікатів
        
    async def __aenter__(self):
        """Асинхронний контекстний менеджер"""
        if self.auth_token:
            # Формуємо cookies для автентифікації
            cookies = {{
                'auth_token': self.auth_token,
                'ct0': self.csrf_token or 'default_csrf_token'
            }}
            
            headers = {{
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
            }}
            
            timeout = aiohttp.ClientTimeout(total=15)
            self.session = aiohttp.ClientSession(headers=headers, cookies=cookies, timeout=timeout)
            logger.info("Twitter моніторинг ініціалізовано з auth_token")
        else:
            logger.warning("Twitter auth_token не встановлено! Twitter моніторинг буде відключено")
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
                logger.info(f"Додано акаунт для моніторингу: {{clean_username}}")
                return True
        except Exception as e:
            logger.error(f"Помилка додавання акаунта {{username}}: {{e}}")
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
                url = TWITTER_ENDPOINTS['user_tweets']
                params = {{
                    'variables': json.dumps({{
                        'userId': user_id,
                        'count': limit,
                        'includePromotedContent': True,
                        'withQuickPromoteEligibilityTweetFields': True,
                        'withVoice': True
                    }}),
                    'features': json.dumps({{
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
                    }}),
                    'fieldToggles': json.dumps({{
                        'withArticlePlainText': False
                    }})
                }}
                
                # Спробуємо GET запит
                async with self.session.get(url, params=params) as response:
                    logger.info(f"GET запит до {{url}}: статус {{response.status}}")
                    if response.status == 200:
                        data = await response.json()
                        tweets = self._parse_api_response(data, username)
                        return tweets[:limit]
                    elif response.status == 401:
                        logger.error("Unauthorized: неправильний auth_token")
                    elif response.status == 403:
                        logger.error("Forbidden: немає доступу до акаунта")
                    elif response.status == 429:
                        logger.warning("Rate limited: занадто багато запитів")
                    else:
                        logger.error(f"Помилка отримання твітів {{username}}: {{response.status}}")
                        # Спробуємо POST запит як fallback
                        logger.info("Спробуємо POST запит...")
                        async with self.session.post(url, json={{
                            'variables': {{
                                'userId': user_id,
                                'count': limit,
                                'includePromotedContent': True,
                                'withQuickPromoteEligibilityTweetFields': True,
                                'withVoice': True
                            }},
                            'features': {{
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
                            }},
                            'fieldToggles': {{
                                'withArticlePlainText': False
                            }}
                        }}) as post_response:
                            logger.info(f"POST запит до {{url}}: статус {{post_response.status}}")
                            if post_response.status == 200:
                                data = await post_response.json()
                                tweets = self._parse_api_response(data, username)
                                return tweets[:limit]
                            else:
                                logger.error(f"POST запит також не працює: {{post_response.status}}")
                                return []
            else:
                # Якщо user_id не отримано, використовуємо HTML парсинг
                logger.info(f"User_id не отримано для {{username}}, використовуємо HTML парсинг")
                return await self._get_tweets_from_html(username, limit)
                
        except Exception as e:
            logger.error(f"Помилка запиту до Twitter API для {{username}}: {{e}}")
            # Fallback до HTML парсингу
            try:
                return await self._get_tweets_from_html(username, limit)
            except Exception as html_error:
                logger.error(f"Помилка HTML парсингу для {{username}}: {{html_error}}")
                return []
            
    async def _get_user_id_by_username(self, username: str) -> str:
        """Отримати user_id за username через GraphQL"""
        try:
            # Використовуємо знайдений GraphQL endpoint для отримання user_id
            url = TWITTER_ENDPOINTS['user_by_screen_name']
            params = {{
                'variables': json.dumps({{
                    'screen_name': username,
                    'withSafetyModeUserFields': True
                }}),
                'features': json.dumps({{
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
                    'responsive_web_twitter_article_tweet_consumption_enabled': False,
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
                }})
            }}
            
            # Спробуємо GET запит
            async with self.session.get(url, params=params) as response:
                logger.info(f"GET запит user_id для {{username}}: статус {{response.status}}")
                if response.status == 200:
                    data = await response.json()
                    user_data = data.get('data', {{}}).get('user', {{}}).get('result', {{}})
                    user_id = user_data.get('rest_id')
                    if user_id:
                        logger.info(f"Отримано user_id {{user_id}} для {{username}}")
                        return str(user_id)
                    else:
                        logger.error(f"User_id не знайдено в відповіді для {{username}}")
                        return None
                elif response.status == 404:
                    logger.error(f"Endpoint не знайдено для {{username}}: {{response.status}}")
                    return None
                elif response.status == 403:
                    logger.error(f"Немає доступу для {{username}}: {{response.status}}")
                    return None
                else:
                    logger.error(f"Помилка отримання user_id для {{username}}: {{response.status}}")
                    return None
                    
        except Exception as e:
            logger.error(f"Помилка запиту user_id для {{username}}: {{e}}")
            return None
            
    async def _get_tweets_from_html(self, username: str, limit: int = 5) -> List[Dict]:
        """Отримати твіти через HTML парсинг (fallback метод)"""
        try:
            # Використовуємо requests для HTML запитів (синхронно)
            import requests
            
            headers = {{
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }}
            
            url = f"https://x.com/{{username}}"
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                html = response.text
                return self._parse_tweets_from_html(html, username)[:limit]
            else:
                logger.error(f"Помилка завантаження HTML для {{username}}: {{response.status_code}}")
                return []
        except Exception as e:
            logger.error(f"Помилка HTML парсингу для {{username}}: {{e}}")
            return []
            
    def _parse_api_response(self, data: Dict, username: str) -> List[Dict]:
        """Парсинг відповіді Twitter GraphQL API"""
        tweets = []
        
        try:
            # Логуємо структуру відповіді для дебагу
            logger.info(f"GraphQL відповідь для {{username}}: {{json.dumps(data, indent=2)[:500]}}...")
            
            # Парсинг відповіді від Twitter GraphQL API
            if 'data' in data:
                user_data = data['data']
                if 'user' in user_data:
                    user = user_data['user']
                    if 'result' in user:
                        result = user['result']
                        if 'timeline_v2' in result:
                            timeline = result['timeline_v2']
                            if 'timeline' in timeline:
                                timeline_data = timeline['timeline']
                                instructions = timeline_data.get('instructions', [])
                                
                                for instruction in instructions:
                                    if instruction.get('type') == 'TimelineAddEntries':
                                        entries = instruction.get('entries', [])
                                        
                                        for entry in entries:
                                            if entry.get('entryId', '').startswith('tweet-'):
                                                content = entry.get('content', {{}})
                                                
                                                if content.get('entryType') == 'TimelineTimelineItem':
                                                    item_content = content.get('itemContent', {{}})
                                                    tweet_data = item_content.get('tweet_results', {{}}).get('result', {{}})
                                                    
                                                    if tweet_data.get('__typename') == 'Tweet':
                                                        tweet_id = tweet_data.get('rest_id', '')
                                                        text = tweet_data.get('legacy', {{}}).get('full_text', '')
                                                        created_at = tweet_data.get('legacy', {{}}).get('created_at', '')
                                                        user_info = tweet_data.get('core', {{}}).get('user_results', {{}}).get('result', {{}})
                                                        
                                                        if text and tweet_id:
                                                            tweets.append({{
                                                                'id': tweet_id,
                                                                'text': text,
                                                                'created_at': created_at,
                                                                'user': {{
                                                                    'screen_name': username,
                                                                    'name': user_info.get('legacy', {{}}).get('name', username)
                                                                }},
                                                                'url': f"https://twitter.com/{{username}}/status/{{tweet_id}}"
                                                            }})
                                        
        except Exception as e:
            logger.error(f"Помилка парсингу GraphQL відповіді: {{e}}")
            
        return tweets
        
    def _parse_tweets_from_html(self, html: str, username: str) -> List[Dict]:
        """Парсинг твітів з HTML (базовий)"""
        tweets = []
        
        try:
            # Шукаємо JSON дані в HTML
            import re
            
            # Паттерн для пошуку JSON даних
            json_pattern = r'<script[^>]*>.*?window\\.__INITIAL_STATE__\\s*=\\s*({{.*?}});'
            match = re.search(json_pattern, html, re.DOTALL)
            
            if match:
                try:
                    json_data = json.loads(match.group(1))
                    # Тут можна додати парсинг JSON даних
                    logger.info(f"Знайдено JSON дані в HTML для {{username}}")
                except json.JSONDecodeError:
                    logger.warning(f"Не вдалося розпарсити JSON з HTML для {{username}}")
            
            # Базовий парсинг HTML (можна розширити)
            logger.info(f"HTML парсинг для {{username}} (базовий)")
            
        except Exception as e:
            logger.error(f"Помилка парсингу HTML для {{username}}: {{e}}")
            
        return tweets
    
    async def check_new_tweets(self) -> List[Dict]:
        """Перевірити нові твіти для всіх акаунтів"""
        new_tweets = []
        
        for username in self.monitoring_accounts:
            try:
                tweets = await self.get_user_tweets(username, limit=5)
                
                for tweet in tweets:
                    tweet_id = tweet.get('id')
                    if tweet_id and tweet_id not in self.sent_tweets:
                        new_tweets.append(tweet)
                        self.sent_tweets.add(tweet_id)
                        
            except Exception as e:
                logger.error(f"Помилка перевірки твітів для {{username}}: {{e}}")
                
        return new_tweets
    
    def format_tweet_notification(self, tweet: Dict) -> str:
        """Форматувати сповіщення про твіт"""
        try:
            # Екрануємо спеціальні символи для Markdown
            text = tweet.get('text', '')
            text = text.replace('*', '\\*').replace('_', '\\_').replace('[', '\\[').replace(']', '\\]')
            
            username = tweet.get('user', {{}}).get('screen_name', 'unknown')
            name = tweet.get('user', {{}}).get('name', username)
            tweet_id = tweet.get('id', '')
            url = tweet.get('url', f"https://twitter.com/{{username}}/status/{{tweet_id}}")
            created_at = tweet.get('created_at', '')
            
            notification = f"""🐦 **Новий твіт з Twitter**
👤 Автор: {{name}} (@{{username}})
📝 Текст: {{text}}
🔗 [Перейти до твіта]({{url}})
⏰ {{created_at}}"""
            
            return notification
            
        except Exception as e:
            logger.error(f"Помилка форматування сповіщення: {{e}}")
            return f"🐦 Новий твіт з Twitter: {{tweet.get('text', 'Помилка форматування')}}"

# Приклад використання
async def main():
    """Приклад використання TwitterMonitor"""
    auth_token = "262d2ffed60222b5c42f4150300cb144ac012871"  # Ваш auth_token
    csrf_token = "ddf294f36c4c0fd61ca8fae2dea1b30f24b82d01ddc860b9c0bf8009876a744b031f8d07b1e4774dea6771b26adcdc217b44726d034345a324b1e0999b31cf9513eeafc0954310dd3478db570e59d170"  # Ваш csrf_token
    
    async with TwitterMonitor(auth_token, csrf_token) as monitor:
        # Додаємо акаунт для моніторингу
        monitor.add_account("twitter")
        
        # Отримуємо твіти
        tweets = await monitor.get_user_tweets("twitter", limit=5)
        print(f"Знайдено {{len(tweets)}} твітів")
        
        # Перевіряємо нові твіти
        new_tweets = await monitor.check_new_tweets()
        print(f"Знайдено {{len(new_tweets)}} нових твітів")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    return code

def main():
    """Головна функція"""
    print("🔧 Generate Twitter Monitor Code")
    print("=" * 50)
    
    # Генеруємо код
    code = generate_twitter_monitor_code()
    
    # Зберігаємо у файл
    with open('twitter_monitor_updated.py', 'w', encoding='utf-8') as f:
        f.write(code)
    
    print("✅ Оновлений код згенеровано!")
    print("📁 Файл: twitter_monitor_updated.py")
    print()
    print("🔧 Основні покращення:")
    print("   - Автоматично знайдені endpoints")
    print("   - Детальна діагностика запитів")
    print("   - Fallback до HTML парсингу")
    print("   - Спробуємо GET і POST методи")
    print("   - Покращена обробка помилок")
    print()
    print("💡 Для використання:")
    print("   1. Оновіть токени в коді")
    print("   2. Запустіть: python twitter_monitor_updated.py")
    print("   3. Перевірте логи для діагностики")

if __name__ == "__main__":
    main()