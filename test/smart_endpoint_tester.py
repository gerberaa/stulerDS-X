#!/usr/bin/env python3
"""
Smart Twitter/X Endpoint Tester
Розумний тестер який знаходить правильні параметри для endpoints
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional

# Налаштування логування
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartEndpointTester:
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
            'Referer': 'https://x.com/',
            'X-Twitter-Active-User': 'yes',
            'X-Twitter-Auth-Type': 'OAuth2Session'
        }
        
        timeout = aiohttp.ClientTimeout(total=15)
        self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрити сесію"""
        if self.session:
            await self.session.close()
    
    async def test_user_by_screen_name(self) -> Optional[Dict]:
        """Тестувати отримання user_id за username"""
        logger.info("🔍 Тестування UserByScreenName...")
        
        query_id = "7mjxD3-C6BxitZR0F6X0aQ"
        
        # Різні варіанти URL
        url_variants = [
            f"https://x.com/i/api/graphql/{query_id}/UserByScreenName",
            f"https://x.com/i/api/graphql/{query_id}",
        ]
        
        # Різні варіанти параметрів
        param_variants = [
            # Варіант 1: GET з query параметрами
            {
                'method': 'GET',
                'params': {
                    'variables': json.dumps({
                        'screen_name': 'twitter',
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
                    })
                }
            },
            # Варіант 2: POST з JSON body
            {
                'method': 'POST',
                'json': {
                    'variables': {
                        'screen_name': 'twitter',
                        'withSafetyModeUserFields': True
                    },
                    'features': {
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
                    }
                }
            }
        ]
        
        for url in url_variants:
            for variant in param_variants:
                try:
                    logger.debug(f"Тестування: {variant['method']} {url}")
                    
                    if variant['method'] == 'GET':
                        async with self.session.get(url, params=variant['params']) as response:
                            status = response.status
                            if status == 200:
                                data = await response.json()
                                if self._validate_user_response(data):
                                    logger.info(f"✅ UserByScreenName працює: {variant['method']} {url}")
                                    return {
                                        'url': url,
                                        'method': variant['method'],
                                        'params': variant['params']
                                    }
                            logger.debug(f"Статус {status} для {variant['method']} {url}")
                    
                    elif variant['method'] == 'POST':
                        async with self.session.post(url, json=variant['json']) as response:
                            status = response.status
                            if status == 200:
                                data = await response.json()
                                if self._validate_user_response(data):
                                    logger.info(f"✅ UserByScreenName працює: {variant['method']} {url}")
                                    return {
                                        'url': url,
                                        'method': variant['method'],
                                        'json': variant['json']
                                    }
                            logger.debug(f"Статус {status} для {variant['method']} {url}")
                
                except Exception as e:
                    logger.debug(f"Помилка тестування {variant['method']} {url}: {e}")
                    continue
        
        logger.warning("❌ UserByScreenName не працює з жодним варіантом")
        return None
    
    def _validate_user_response(self, data: Dict) -> bool:
        """Валідувати відповідь UserByScreenName"""
        try:
            if 'data' in data and 'user' in data['data']:
                user_data = data['data']['user']
                if 'result' in user_data:
                    result = user_data['result']
                    if 'rest_id' in result:
                        logger.info(f"Знайдено user_id: {result['rest_id']}")
                        return True
            return False
        except:
            return False
    
    async def test_user_tweets(self, user_id: str = "1923350225114001408") -> Optional[Dict]:
        """Тестувати отримання твітів користувача"""
        logger.info("🔍 Тестування UserTweets...")
        
        query_id = "9jV-614Qopr4Eg6_JNNoqQ"
        
        # Різні варіанти URL
        url_variants = [
            f"https://x.com/i/api/graphql/{query_id}/UserTweets",
            f"https://x.com/i/api/graphql/{query_id}",
        ]
        
        # Різні варіанти параметрів
        param_variants = [
            # Варіант 1: GET з query параметрами
            {
                'method': 'GET',
                'params': {
                    'variables': json.dumps({
                        'userId': user_id,
                        'count': 20,
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
            },
            # Варіант 2: POST з JSON body
            {
                'method': 'POST',
                'json': {
                    'variables': {
                        'userId': user_id,
                        'count': 20,
                        'includePromotedContent': True,
                        'withQuickPromoteEligibilityTweetFields': True,
                        'withVoice': True
                    },
                    'features': {
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
                    },
                    'fieldToggles': {
                        'withArticlePlainText': False
                    }
                }
            }
        ]
        
        for url in url_variants:
            for variant in param_variants:
                try:
                    logger.debug(f"Тестування: {variant['method']} {url}")
                    
                    if variant['method'] == 'GET':
                        async with self.session.get(url, params=variant['params']) as response:
                            status = response.status
                            if status == 200:
                                data = await response.json()
                                if self._validate_tweets_response(data):
                                    logger.info(f"✅ UserTweets працює: {variant['method']} {url}")
                                    return {
                                        'url': url,
                                        'method': variant['method'],
                                        'params': variant['params']
                                    }
                            logger.debug(f"Статус {status} для {variant['method']} {url}")
                    
                    elif variant['method'] == 'POST':
                        async with self.session.post(url, json=variant['json']) as response:
                            status = response.status
                            if status == 200:
                                data = await response.json()
                                if self._validate_tweets_response(data):
                                    logger.info(f"✅ UserTweets працює: {variant['method']} {url}")
                                    return {
                                        'url': url,
                                        'method': variant['method'],
                                        'json': variant['json']
                                    }
                            logger.debug(f"Статус {status} для {variant['method']} {url}")
                
                except Exception as e:
                    logger.debug(f"Помилка тестування {variant['method']} {url}: {e}")
                    continue
        
        logger.warning("❌ UserTweets не працює з жодним варіантом")
        return None
    
    def _validate_tweets_response(self, data: Dict) -> bool:
        """Валідувати відповідь UserTweets"""
        try:
            if 'data' in data and 'user' in data['data']:
                user_data = data['data']['user']
                if 'result' in user_data and 'timeline_v2' in user_data['result']:
                    timeline = user_data['result']['timeline_v2']
                    if 'timeline' in timeline:
                        logger.info("Знайдено timeline з твітами")
                        return True
            return False
        except:
            return False
    
    def save_working_config(self, user_config: Optional[Dict], tweets_config: Optional[Dict]):
        """Зберегти робочу конфігурацію"""
        config = {
            'user_by_screen_name': user_config,
            'user_tweets': tweets_config,
            'timestamp': asyncio.get_event_loop().time()
        }
        
        with open('working_twitter_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info("💾 Робочу конфігурацію збережено у working_twitter_config.json")

async def main():
    """Головна функція"""
    print("🧪 Smart Twitter/X Endpoint Tester")
    print("=" * 50)
    
    async with SmartEndpointTester() as tester:
        # Тестуємо UserByScreenName
        user_config = await tester.test_user_by_screen_name()
        
        # Тестуємо UserTweets
        tweets_config = await tester.test_user_tweets()
        
        # Зберігаємо результати
        tester.save_working_config(user_config, tweets_config)
        
        # Виводимо результати
        print("\n📊 Результати:")
        print("-" * 30)
        
        if user_config:
            print(f"✅ UserByScreenName: {user_config['method']} {user_config['url']}")
        else:
            print("❌ UserByScreenName: не працює")
        
        if tweets_config:
            print(f"✅ UserTweets: {tweets_config['method']} {tweets_config['url']}")
        else:
            print("❌ UserTweets: не працює")
        
        print(f"\n🎯 Знайдено {sum([1 for x in [user_config, tweets_config] if x])} робочих endpoints")
        print("✨ Тестування завершено!")

if __name__ == "__main__":
    asyncio.run(main())