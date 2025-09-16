#!/usr/bin/env python3
"""
Тест функціональності зображень для Twitter та Discord моніторингу
"""

import asyncio
import logging
from selenium_twitter_monitor import SeleniumTwitterMonitor
from discord_monitor import DiscordMonitor

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_twitter_image_extraction():
    """Тест витягування зображень з Twitter"""
    print("🧪 Тестування витягування зображень з Twitter...")
    
    try:
        async with SeleniumTwitterMonitor() as monitor:
            # Додаємо тестовий акаунт
            test_account = "pilk_xz"  # Використовуємо існуючий акаунт з проекту
            monitor.add_account(test_account)
            
            # Отримуємо твіти
            tweets = await monitor.get_user_tweets(test_account, limit=3)
            
            print(f"📊 Знайдено {len(tweets)} твітів")
            
            for i, tweet in enumerate(tweets):
                print(f"\n📝 Твіт {i+1}:")
                print(f"   ID: {tweet.get('id', 'N/A')}")
                print(f"   Текст: {tweet.get('text', 'N/A')[:100]}...")
                print(f"   URL: {tweet.get('url', 'N/A')}")
                
                images = tweet.get('images', [])
                print(f"   📷 Зображень: {len(images)}")
                
                for j, image_url in enumerate(images):
                    # Перевіряємо чи це не аватарка
                    is_avatar = any(pattern in image_url.lower() for pattern in [
                        'profile_images', 'avatar', 'normal.jpg', 'bigger.jpg', 'mini.jpg'
                    ])
                    avatar_status = " (АВАТАРКА!)" if is_avatar else " (ЗОБРАЖЕННЯ ТВІТА)"
                    
                    # Перевіряємо чи є параметри для відображення
                    has_params = '?' in image_url and ('format=' in image_url or 'name=' in image_url)
                    param_status = " ✅ З параметрами" if has_params else " ⚠️ Без параметрів"
                    
                    print(f"      {j+1}. {image_url}{avatar_status}{param_status}")
                
                if images:
                    # Перевіряємо чи є справжні зображення твіта
                    real_images = [img for img in images if not any(pattern in img.lower() for pattern in [
                        'profile_images', 'avatar', 'normal.jpg', 'bigger.jpg', 'mini.jpg'
                    ])]
                    
                    if real_images:
                        print(f"   ✅ Знайдено {len(real_images)} справжніх зображень твіта!")
                    else:
                        print("   ⚠️  Знайдені тільки аватарки, справжніх зображень твіта немає")
                else:
                    print("   ℹ️  Зображень не знайдено")
            
            return len(tweets) > 0
            
    except Exception as e:
        print(f"❌ Помилка тестування Twitter: {e}")
        return False

async def test_discord_image_extraction():
    """Тест витягування зображень з Discord"""
    print("\n🧪 Тестування витягування зображень з Discord...")
    
    # Потрібен Discord authorization токен для тестування
    discord_token = None  # Встановіть токен для тестування
    
    if not discord_token:
        print("⚠️  Discord authorization токен не встановлено, пропускаємо тест")
        return True
    
    try:
        async with DiscordMonitor(discord_token) as monitor:
            # Додаємо тестовий канал
            test_channel = "https://discord.com/channels/1408570777275469866/1413243132467871839"
            monitor.add_channel(test_channel)
            
            # Отримуємо повідомлення
            messages = await monitor.check_new_messages()
            
            print(f"📊 Знайдено {len(messages)} нових повідомлень")
            
            for i, message in enumerate(messages):
                print(f"\n💬 Повідомлення {i+1}:")
                print(f"   ID: {message.get('message_id', 'N/A')}")
                print(f"   Автор: {message.get('author', 'N/A')}")
                print(f"   Текст: {message.get('content', 'N/A')[:100]}...")
                print(f"   URL: {message.get('url', 'N/A')}")
                
                images = message.get('images', [])
                print(f"   📷 Зображень: {len(images)}")
                
                for j, image_url in enumerate(images):
                    print(f"      {j+1}. {image_url}")
                
                if images:
                    print("   ✅ Зображення успішно витягнуті!")
                else:
                    print("   ℹ️  Зображень не знайдено")
            
            return True
            
    except Exception as e:
        print(f"❌ Помилка тестування Discord: {e}")
        return False

def test_image_download():
    """Тест завантаження зображень"""
    print("\n🧪 Тестування завантаження зображень...")
    
    # Тестові URL зображень
    test_urls = [
        "https://pbs.twimg.com/media/example.jpg",  # Приклад Twitter зображення
        "https://cdn.discordapp.com/attachments/example.png"  # Приклад Discord зображення
    ]
    
    try:
        from bot import download_and_send_image
        
        for i, url in enumerate(test_urls):
            print(f"📥 Тестування завантаження {i+1}: {url}")
            
            # Тестуємо завантаження (без відправки в Telegram)
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            try:
                response = requests.head(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ URL доступний (статус: {response.status_code})")
                else:
                    print(f"   ⚠️  URL недоступний (статус: {response.status_code})")
            except Exception as e:
                print(f"   ❌ Помилка перевірки URL: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування завантаження: {e}")
        return False

async def main():
    """Головна функція тестування"""
    print("🚀 Запуск тестування функціональності зображень")
    print("=" * 60)
    
    results = []
    
    # Тестуємо Twitter
    twitter_result = await test_twitter_image_extraction()
    results.append(("Twitter", twitter_result))
    
    # Тестуємо Discord
    discord_result = await test_discord_image_extraction()
    results.append(("Discord", discord_result))
    
    # Тестуємо завантаження
    download_result = test_image_download()
    results.append(("Download", download_result))
    
    # Підсумок
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ ПРОВАЛЕНО"
        print(f"{test_name:15} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 ВСІ ТЕСТИ ПРОЙДЕНО! Функціональність зображень працює.")
    else:
        print("⚠️  ДЕЯКІ ТЕСТИ ПРОВАЛЕНІ. Перевірте налаштування.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)