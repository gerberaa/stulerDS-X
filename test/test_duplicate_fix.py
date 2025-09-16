#!/usr/bin/env python3
"""
Тест виправлення проблеми з безкінечним детектуванням твітів
"""

import asyncio
import logging
from twitter_monitor import TwitterMonitor
from selenium_twitter_monitor import SeleniumTwitterMonitor

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_twitter_monitor_duplicates():
    """Тест TwitterMonitor на дублікати"""
    print("🧪 Тестування TwitterMonitor на дублікати")
    print("=" * 50)
    
    try:
        async with TwitterMonitor() as monitor:
            # Додаємо тестовий акаунт
            test_username = "pilk_xz"
            monitor.add_account(test_username)
            
            print(f"✅ Додано акаунт: {test_username}")
            print(f"📊 Відправлених твітів: {len(monitor.sent_tweets.get(test_username, set()))}")
            
            # Перша перевірка
            print("\n🔍 Перша перевірка...")
            tweets1 = await monitor.check_new_tweets()
            print(f"📝 Знайдено твітів: {len(tweets1)}")
            print(f"📊 Відправлених твітів після першої перевірки: {len(monitor.sent_tweets.get(test_username, set()))}")
            
            # Друга перевірка (має бути 0 нових)
            print("\n🔍 Друга перевірка (має бути 0 нових)...")
            tweets2 = await monitor.check_new_tweets()
            print(f"📝 Знайдено твітів: {len(tweets2)}")
            print(f"📊 Відправлених твітів після другої перевірки: {len(monitor.sent_tweets.get(test_username, set()))}")
            
            # Третя перевірка (має бути 0 нових)
            print("\n🔍 Третя перевірка (має бути 0 нових)...")
            tweets3 = await monitor.check_new_tweets()
            print(f"📝 Знайдено твітів: {len(tweets3)}")
            print(f"📊 Відправлених твітів після третьої перевірки: {len(monitor.sent_tweets.get(test_username, set()))}")
            
            # Перевіряємо результат
            if len(tweets2) == 0 and len(tweets3) == 0:
                print("\n✅ ТЕСТ ПРОЙШОВ: Дублікати успішно відфільтровані!")
            else:
                print(f"\n❌ ТЕСТ НЕ ПРОЙШОВ: Знайдено {len(tweets2)} та {len(tweets3)} дублікатів")
                
    except Exception as e:
        print(f"\n❌ Помилка тестування TwitterMonitor: {e}")

async def test_selenium_monitor_duplicates():
    """Тест SeleniumTwitterMonitor на дублікати"""
    print("\n🧪 Тестування SeleniumTwitterMonitor на дублікати")
    print("=" * 50)
    
    try:
        async with SeleniumTwitterMonitor() as monitor:
            # Додаємо тестовий акаунт
            test_username = "pilk_xz"
            monitor.add_account(test_username)
            
            print(f"✅ Додано акаунт: {test_username}")
            print(f"📊 Відправлених твітів: {len(monitor.sent_tweets.get(test_username, set()))}")
            
            # Перша перевірка
            print("\n🔍 Перша перевірка...")
            tweets1 = await monitor.check_new_tweets()
            print(f"📝 Знайдено твітів: {len(tweets1)}")
            print(f"📊 Відправлених твітів після першої перевірки: {len(monitor.sent_tweets.get(test_username, set()))}")
            
            # Друга перевірка (має бути 0 нових)
            print("\n🔍 Друга перевірка (має бути 0 нових)...")
            tweets2 = await monitor.check_new_tweets()
            print(f"📝 Знайдено твітів: {len(tweets2)}")
            print(f"📊 Відправлених твітів після другої перевірки: {len(monitor.sent_tweets.get(test_username, set()))}")
            
            # Третя перевірка (має бути 0 нових)
            print("\n🔍 Третя перевірка (має бути 0 нових)...")
            tweets3 = await monitor.check_new_tweets()
            print(f"📝 Знайдено твітів: {len(tweets3)}")
            print(f"📊 Відправлених твітів після третьої перевірки: {len(monitor.sent_tweets.get(test_username, set()))}")
            
            # Перевіряємо результат
            if len(tweets2) == 0 and len(tweets3) == 0:
                print("\n✅ ТЕСТ ПРОЙШОВ: Дублікати успішно відфільтровані!")
            else:
                print(f"\n❌ ТЕСТ НЕ ПРОЙШОВ: Знайдено {len(tweets2)} та {len(tweets3)} дублікатів")
                
    except Exception as e:
        print(f"\n❌ Помилка тестування SeleniumTwitterMonitor: {e}")

async def test_stable_ids():
    """Тест стабільності ID твітів"""
    print("\n🧪 Тестування стабільності ID твітів")
    print("=" * 50)
    
    try:
        async with TwitterMonitor() as monitor:
            test_username = "pilk_xz"
            monitor.add_account(test_username)
            
            # Отримуємо твіти двічі
            tweets1 = await monitor.get_user_tweets(test_username, limit=3)
            tweets2 = await monitor.get_user_tweets(test_username, limit=3)
            
            print(f"📝 Перша перевірка: {len(tweets1)} твітів")
            print(f"📝 Друга перевірка: {len(tweets2)} твітів")
            
            # Перевіряємо чи ID стабільні
            stable_ids = 0
            for i, tweet1 in enumerate(tweets1):
                if i < len(tweets2):
                    tweet2 = tweets2[i]
                    if tweet1['id'] == tweet2['id']:
                        stable_ids += 1
                        print(f"✅ Твіт {i+1}: ID стабільний ({tweet1['id']})")
                    else:
                        print(f"❌ Твіт {i+1}: ID нестабільний ({tweet1['id']} != {tweet2['id']})")
            
            if stable_ids == len(tweets1):
                print(f"\n✅ ТЕСТ ПРОЙШОВ: Всі {stable_ids} ID стабільні!")
            else:
                print(f"\n❌ ТЕСТ НЕ ПРОЙШОВ: Тільки {stable_ids}/{len(tweets1)} ID стабільні")
                
    except Exception as e:
        print(f"\n❌ Помилка тестування стабільності ID: {e}")

async def main():
    """Головна функція тестування"""
    print("🚀 ТЕСТУВАННЯ ВИПРАВЛЕННЯ ДУБЛІКАТІВ ТВІТІВ")
    print("=" * 60)
    
    # Тестуємо TwitterMonitor
    await test_twitter_monitor_duplicates()
    
    # Тестуємо SeleniumTwitterMonitor
    await test_selenium_monitor_duplicates()
    
    # Тестуємо стабільність ID
    await test_stable_ids()
    
    print("\n" + "=" * 60)
    print("🎉 ТЕСТУВАННЯ ЗАВЕРШЕНО!")
    print("\n📋 Підсумок виправлень:")
    print("✅ Додано sent_tweets для відстеження відправлених твітів")
    print("✅ Додано глобальну систему відстеження в bot.py")
    print("✅ Покращено генерацію стабільних ID для HTML парсингу")
    print("✅ Додано автоматичне очищення старих твітів")
    print("✅ Додано детальне логування для діагностики")

if __name__ == "__main__":
    asyncio.run(main())