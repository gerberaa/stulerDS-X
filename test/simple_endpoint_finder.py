#!/usr/bin/env python3
"""
Simple Twitter/X Endpoint Finder
Простий скрипт для пошуку актуальних endpoints
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleEndpointFinder:
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        """Ініціалізація сесії"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'uk,en-US;q=0.9,en;q=0.8,ru;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'Content-Type': 'application/json',
            'Referer': 'https://x.com/'
        }
        
        timeout = aiohttp.ClientTimeout(total=15)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрити сесію"""
        if self.session:
            await self.session.close()
    
    async def test_endpoints(self) -> Dict[str, str]:
        """Тестувати відомі endpoints"""
        logger.info("🧪 Тестування відомих endpoints...")
        
        # Список відомих query IDs для тестування
        test_endpoints = {
            'user_tweets': [
                '9jV-614Qopr4Eg6_JNNoqQ',  # З вашого прикладу
                'VWxohB9x3MlYTQL32fD2g',   # Альтернативний
                'h8XQJ2OcU7X9YzK3mN5pQ',   # Ще один
                '7mjxD3-C6BxitZR0F6X0aQ',  # З вашого прикладу UserByScreenName
                'G3KGOASz96M-Qu0nwm4Xg',   # Альтернативний
            ],
            'user_by_screen_name': [
                '7mjxD3-C6BxitZR0F6X0aQ',  # З вашого прикладу
                'G3KGOASz96M-Qu0nwm4Xg',   # Альтернативний
                'sLVLhk0bGj3MVFE4d0l2ug',  # Ще один
            ],
            'tweet_detail': [
                'ikU9DgZwhNIWqqFheO2NWA',  # З вашого прикладу
                'VWxohB9x3MlYTQL32fD2g',   # Альтернативний
            ]
        }
        
        working_endpoints = {}
        
        for endpoint_type, query_ids in test_endpoints.items():
            logger.info(f"🔍 Тестування {endpoint_type}...")
            
            for query_id in query_ids:
                if await self._test_query_id(endpoint_type, query_id):
                    working_endpoints[endpoint_type] = f"https://x.com/i/api/graphql/{query_id}"
                    logger.info(f"✅ {endpoint_type}: {query_id}")
                    break
            else:
                logger.warning(f"❌ {endpoint_type}: не знайдено робочий endpoint")
        
        return working_endpoints
    
    async def _test_query_id(self, endpoint_type: str, query_id: str) -> bool:
        """Тестувати конкретний query ID"""
        try:
            url = f"https://x.com/i/api/graphql/{query_id}"
            
            # Формуємо параметри залежно від типу
            params = self._get_params_for_type(endpoint_type, query_id)
            
            async with self.session.get(url, params=params) as response:
                logger.debug(f"Тест {query_id}: статус {response.status}")
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        return self._is_valid_response(data, endpoint_type)
                    except:
                        return False
                elif response.status == 400:
                    # 400 може означати неправильні параметри, але endpoint існує
                    return True
                elif response.status == 403:
                    # 403 означає що endpoint існує, але немає доступу
                    return True
                    
        except Exception as e:
            logger.debug(f"Помилка тестування {query_id}: {e}")
            
        return False
    
    def _get_params_for_type(self, endpoint_type: str, query_id: str) -> Dict:
        """Отримати параметри для тестування"""
        base_params = {
            'features': json.dumps({
                'rweb_video_screen_enabled': False,
                'payments_enabled': False,
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
        
        return base_params
    
    def _is_valid_response(self, data: Dict, endpoint_type: str) -> bool:
        """Перевірити чи відповідь валідна"""
        try:
            if 'data' in data:
                if endpoint_type == 'user_tweets':
                    return 'user' in data['data']
                elif endpoint_type == 'user_by_screen_name':
                    return 'user' in data['data']
                elif endpoint_type == 'tweet_detail':
                    return 'threaded_conversation_with_injections_v2' in data['data']
            return False
        except:
            return False
    
    def save_results(self, endpoints: Dict[str, str]):
        """Зберегти результати"""
        # Зберігаємо у JSON файл
        with open('found_endpoints.json', 'w', encoding='utf-8') as f:
            json.dump(endpoints, f, indent=2, ensure_ascii=False)
        
        # Генеруємо Python код
        python_code = f"""
# Знайдені Twitter/X endpoints
TWITTER_ENDPOINTS = {{
"""
        
        for endpoint_type, url in endpoints.items():
            python_code += f'    "{endpoint_type}": "{url}",\n'
        
        python_code += "}\n\n"
        python_code += """
# Приклад використання в twitter_monitor.py:
# 
# async def get_user_tweets(self, username: str, limit: int = 5) -> List[Dict]:
#     user_id = await self._get_user_id_by_username(username)
#     if user_id:
#         url = TWITTER_ENDPOINTS['user_tweets']
#         # ... решта коду
"""
        
        with open('twitter_endpoints.py', 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        logger.info("💾 Результати збережено у файли:")
        logger.info("   - found_endpoints.json")
        logger.info("   - twitter_endpoints.py")

async def main():
    """Головна функція"""
    print("🔍 Simple Twitter/X Endpoint Finder")
    print("=" * 50)
    
    async with SimpleEndpointFinder() as finder:
        # Тестуємо endpoints
        endpoints = await finder.test_endpoints()
        
        # Виводимо результати
        print("\n📊 Результати:")
        print("-" * 30)
        
        if endpoints:
            for endpoint_type, url in endpoints.items():
                print(f"✅ {endpoint_type}")
                print(f"   URL: {url}")
                print()
        else:
            print("❌ Робочі endpoints не знайдено")
            print("💡 Можливі причини:")
            print("   - Неправильні токени авторизації")
            print("   - Twitter/X змінив API")
            print("   - Проблеми з мережею")
        
        # Зберігаємо результати
        if endpoints:
            finder.save_results(endpoints)
        
        print(f"🎯 Знайдено {len(endpoints)} робочих endpoints")
        print("✨ Тестування завершено!")

if __name__ == "__main__":
    asyncio.run(main())