#!/usr/bin/env python3
"""
Twitter/X Endpoint Finder
Автоматично знаходить актуальні endpoints для Twitter/X API
"""

import asyncio
import aiohttp
import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import time

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TwitterEndpointFinder:
    def __init__(self):
        self.session = None
        self.found_endpoints = {
            'user_tweets': None,
            'user_by_screen_name': None,
            'tweet_detail': None,
            'home_timeline': None
        }
        
    async def __aenter__(self):
        """Ініціалізація сесії"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'uk,en-US;q=0.9,en;q=0.8,ru;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'Content-Type': 'application/json',
            'Referer': 'https://x.com/',
            'X-Twitter-Active-User': 'yes',
            'X-Twitter-Auth-Type': 'OAuth2Session'
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрити сесію"""
        if self.session:
            await self.session.close()
    
    async def find_endpoints_by_analysis(self) -> Dict[str, str]:
        """Знайти endpoints через аналіз відомих паттернів"""
        logger.info("🔍 Пошук endpoints через аналіз паттернів...")
        
        endpoints = {}
        
        # Відомі query IDs для різних операцій
        known_queries = {
            'user_tweets': [
                '9jV-614Qopr4Eg6_JNNoqQ',  # UserTweets
                'VWxohB9x3MlYTQL32fD2g',  # UserTweets (альтернативний)
                'h8XQJ2OcU7X9YzK3mN5pQ',  # UserTweets (ще один)
            ],
            'user_by_screen_name': [
                '7mjxD3-C6BxitZR0F6X0aQ',  # UserByScreenName
                'G3KGOASz96M-Qu0nwm4Xg',   # UserByScreenName (альтернативний)
                'sLVLhk0bGj3MVFE4d0l2ug',  # UserByScreenName (ще один)
            ],
            'tweet_detail': [
                'ikU9DgZwhNIWqqFheO2NWA',  # TweetDetail
                'VWxohB9x3MlYTQL32fD2g',   # TweetDetail (альтернативний)
            ],
            'home_timeline': [
                'VWxohB9x3MlYTQL32fD2g',   # HomeTimeline
                '9jV-614Qopr4Eg6_JNNoqQ',  # HomeTimeline (альтернативний)
            ]
        }
        
        # Тестуємо кожен query ID
        for endpoint_type, query_ids in known_queries.items():
            for query_id in query_ids:
                if await self._test_endpoint(endpoint_type, query_id):
                    endpoints[endpoint_type] = f"https://x.com/i/api/graphql/{query_id}"
                    logger.info(f"✅ Знайдено {endpoint_type}: {query_id}")
                    break
        
        return endpoints
    
    async def _test_endpoint(self, endpoint_type: str, query_id: str) -> bool:
        """Тестувати конкретний endpoint"""
        try:
            url = f"https://x.com/i/api/graphql/{query_id}"
            
            # Формуємо параметри залежно від типу endpoint
            params = self._get_test_params(endpoint_type, query_id)
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Перевіряємо чи відповідь містить очікувані дані
                    if self._validate_response(data, endpoint_type):
                        return True
                elif response.status == 400:
                    # 400 може означати неправильні параметри, але endpoint існує
                    return True
                    
        except Exception as e:
            logger.debug(f"Помилка тестування {query_id}: {e}")
            
        return False
    
    def _get_test_params(self, endpoint_type: str, query_id: str) -> Dict:
        """Отримати тестові параметри для endpoint"""
        base_params = {
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
            })
        }
        
        if endpoint_type == 'user_tweets':
            base_params['variables'] = json.dumps({
                'userId': '1923350225114001408',  # Тестовий user ID
                'count': 20,
                'includePromotedContent': True,
                'withQuickPromoteEligibilityTweetFields': True,
                'withVoice': True
            })
        elif endpoint_type == 'user_by_screen_name':
            base_params['variables'] = json.dumps({
                'screen_name': 'twitter',
                'withSafetyModeUserFields': True
            })
        elif endpoint_type == 'tweet_detail':
            base_params['variables'] = json.dumps({
                'focalTweetId': '1966241718786981898',  # Тестовий tweet ID
                'referrer': 'me',
                'controller_data': 'DAACDAABDAABCgABAAAAAAAAAAAKAAkasRzW4pZwAAAAAAA=',
                'with_rux_injections': False,
                'rankingMode': 'Relevance',
                'includePromotedContent': True,
                'withCommunity': True,
                'withQuickPromoteEligibilityTweetFields': True,
                'withBirdwatchNotes': True,
                'withVoice': True
            })
        elif endpoint_type == 'home_timeline':
            base_params['variables'] = json.dumps({
                'count': 20,
                'includePromotedContent': True,
                'withQuickPromoteEligibilityTweetFields': True,
                'withVoice': True
            })
        
        return base_params
    
    def _validate_response(self, data: Dict, endpoint_type: str) -> bool:
        """Валідувати відповідь endpoint"""
        try:
            if 'data' in data:
                if endpoint_type == 'user_tweets':
                    return 'user' in data['data'] and 'result' in data['data']['user']
                elif endpoint_type == 'user_by_screen_name':
                    return 'user' in data['data'] and 'result' in data['data']['user']
                elif endpoint_type == 'tweet_detail':
                    return 'threaded_conversation_with_injections_v2' in data['data']
                elif endpoint_type == 'home_timeline':
                    return 'home' in data['data']
            return False
        except:
            return False
    
    async def find_endpoints_by_scraping(self) -> Dict[str, str]:
        """Знайти endpoints через скрапінг сторінки Twitter"""
        logger.info("🌐 Пошук endpoints через скрапінг сторінки...")
        
        endpoints = {}
        
        try:
            # Завантажуємо головну сторінку Twitter
            async with self.session.get('https://x.com/home') as response:
                if response.status == 200:
                    html = await response.text()
                    
                    # Шукаємо GraphQL endpoints в HTML
                    graphql_pattern = r'https://x\.com/i/api/graphql/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)'
                    matches = re.findall(graphql_pattern, html)
                    
                    for query_id, operation_name in matches:
                        endpoint_type = self._map_operation_to_type(operation_name)
                        if endpoint_type:
                            endpoints[endpoint_type] = f"https://x.com/i/api/graphql/{query_id}/{operation_name}"
                            logger.info(f"✅ Знайдено {endpoint_type}: {query_id}/{operation_name}")
                    
                    # Шукаємо в JavaScript файлах
                    js_pattern = r'"([a-zA-Z0-9_-]{20,})"'
                    js_matches = re.findall(js_pattern, html)
                    
                    for match in js_matches:
                        if len(match) >= 20:  # Query IDs зазвичай довгі
                            # Тестуємо як потенційний query ID
                            if await self._test_endpoint('user_tweets', match):
                                endpoints['user_tweets'] = f"https://x.com/i/api/graphql/{match}"
                                logger.info(f"✅ Знайдено user_tweets через JS: {match}")
                                break
                                
        except Exception as e:
            logger.error(f"Помилка скрапінгу: {e}")
        
        return endpoints
    
    def _map_operation_to_type(self, operation_name: str) -> Optional[str]:
        """Мапити назву операції до типу endpoint"""
        mapping = {
            'UserTweets': 'user_tweets',
            'UserByScreenName': 'user_by_screen_name',
            'TweetDetail': 'tweet_detail',
            'HomeTimeline': 'home_timeline',
            'TweetResultByRestId': 'tweet_detail',
            'UserResultByScreenName': 'user_by_screen_name'
        }
        return mapping.get(operation_name)
    
    async def find_endpoints_by_network_analysis(self) -> Dict[str, str]:
        """Знайти endpoints через аналіз мережевих запитів"""
        logger.info("📡 Пошук endpoints через аналіз мережевих запитів...")
        
        endpoints = {}
        
        # Список популярних акаунтів для тестування
        test_accounts = ['twitter', 'elonmusk', 'github', 'microsoft', 'google']
        
        for account in test_accounts:
            try:
                # Спробуємо отримати сторінку профілю
                profile_url = f"https://x.com/{account}"
                async with self.session.get(profile_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Шукаємо API виклики в HTML
                        api_pattern = r'https://x\.com/i/api/graphql/([a-zA-Z0-9_-]+)'
                        matches = re.findall(api_pattern, html)
                        
                        for query_id in matches:
                            # Тестуємо різні типи операцій
                            for endpoint_type in ['user_tweets', 'user_by_screen_name']:
                                if await self._test_endpoint(endpoint_type, query_id):
                                    if endpoint_type not in endpoints:
                                        endpoints[endpoint_type] = f"https://x.com/i/api/graphql/{query_id}"
                                        logger.info(f"✅ Знайдено {endpoint_type}: {query_id}")
                                        break
                        
                        # Якщо знайшли достатньо endpoints, зупиняємося
                        if len(endpoints) >= 2:
                            break
                            
            except Exception as e:
                logger.debug(f"Помилка аналізу {account}: {e}")
                continue
        
        return endpoints
    
    async def find_all_endpoints(self) -> Dict[str, str]:
        """Знайти всі endpoints всіма методами"""
        logger.info("🚀 Початок пошуку Twitter/X endpoints...")
        
        all_endpoints = {}
        
        # Метод 1: Аналіз відомих паттернів
        endpoints1 = await self.find_endpoints_by_analysis()
        all_endpoints.update(endpoints1)
        
        # Метод 2: Скрапінг сторінки
        endpoints2 = await self.find_endpoints_by_scraping()
        all_endpoints.update(endpoints2)
        
        # Метод 3: Аналіз мережевих запитів
        endpoints3 = await self.find_endpoints_by_network_analysis()
        all_endpoints.update(endpoints3)
        
        return all_endpoints
    
    def save_endpoints(self, endpoints: Dict[str, str], filename: str = 'twitter_endpoints.json'):
        """Зберегти знайдені endpoints у файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(endpoints, f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Endpoints збережено у файл: {filename}")
        except Exception as e:
            logger.error(f"Помилка збереження: {e}")
    
    def generate_code_update(self, endpoints: Dict[str, str]) -> str:
        """Генерувати код для оновлення twitter_monitor.py"""
        code = """
# Автоматично згенеровані endpoints для Twitter/X API
TWITTER_ENDPOINTS = {
"""
        
        for endpoint_type, url in endpoints.items():
            code += f'    "{endpoint_type}": "{url}",\n'
        
        code += "}\n"
        
        return code

async def main():
    """Головна функція"""
    print("🔍 Twitter/X Endpoint Finder")
    print("=" * 50)
    
    async with TwitterEndpointFinder() as finder:
        # Знаходимо всі endpoints
        endpoints = await finder.find_all_endpoints()
        
        # Виводимо результати
        print("\n📊 Результати пошуку:")
        print("-" * 30)
        
        if endpoints:
            for endpoint_type, url in endpoints.items():
                print(f"✅ {endpoint_type}: {url}")
        else:
            print("❌ Endpoints не знайдено")
        
        # Зберігаємо результати
        if endpoints:
            finder.save_endpoints(endpoints)
            
            # Генеруємо код для оновлення
            code = finder.generate_code_update(endpoints)
            print(f"\n💻 Код для оновлення twitter_monitor.py:")
            print("-" * 40)
            print(code)
            
            # Зберігаємо код у файл
            with open('twitter_endpoints_update.py', 'w', encoding='utf-8') as f:
                f.write(code)
            print("💾 Код збережено у файл: twitter_endpoints_update.py")
        
        print(f"\n🎯 Знайдено {len(endpoints)} endpoints")
        print("✨ Пошук завершено!")

if __name__ == "__main__":
    asyncio.run(main())