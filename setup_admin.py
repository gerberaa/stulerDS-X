#!/usr/bin/env python3
"""
Скрипт для налаштування першого адміністратора системи
"""

import sys
from access_manager import access_manager

def setup_admin():
    """Налаштувати першого адміністратора"""
    print("🔧 Налаштування системи доступу")
    print("=" * 50)
    
    try:
        # Запитуємо дані адміністратора
        print("\n📝 Введіть дані адміністратора:")
        telegram_id = input("Telegram ID: ").strip()
        username = input("Username (опціонально): ").strip()
        password = input("Пароль: ").strip()
        
        if not telegram_id or not password:
            print("❌ Telegram ID та пароль обов'язкові!")
            return False
        
        try:
            telegram_id = int(telegram_id)
        except ValueError:
            print("❌ Telegram ID повинен бути числом!")
            return False
        
        # Додаємо адміністратора
        user_id = access_manager.add_user(telegram_id, username, password)
        
        if user_id:
            # Встановлюємо права адміністратора
            access_manager.set_permission(telegram_id, "can_manage_users", True)
            access_manager.set_permission(telegram_id, "can_view_logs", True)
            access_manager.set_permission(telegram_id, "can_monitor_twitter", True)
            access_manager.set_permission(telegram_id, "can_monitor_discord", True)
            
            print(f"\n✅ Адміністратор успішно створений!")
            print(f"• Telegram ID: {telegram_id}")
            print(f"• Username: {username or 'Не вказано'}")
            print(f"• User ID: {user_id}")
            print(f"• Пароль: {password}")
            print(f"\n🔐 Тепер ви можете використовувати команду /login в боті")
            return True
        else:
            print("❌ Помилка створення адміністратора!")
            return False
            
    except KeyboardInterrupt:
        print("\n\n❌ Скасовано користувачем")
        return False
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        return False

def list_users():
    """Показати список користувачів"""
    print("\n👥 Список користувачів:")
    print("=" * 50)
    
    users = access_manager.get_all_users()
    if not users:
        print("Користувачів не знайдено")
        return
    
    for user in users:
        status = "✅ Активний" if user["is_active"] else "❌ Деактивований"
        print(f"• {user['username'] or 'Без username'} (ID: {user['telegram_id']}) - {status}")
        print(f"  Створено: {user['created_at']}")
        if user['last_login']:
            print(f"  Останній вхід: {user['last_login']}")
        print()

def main():
    """Головна функція"""
    print("🚀 Менеджер доступу для Telegram Monitor Bot")
    print("=" * 50)
    
    while True:
        print("\n📋 Доступні команди:")
        print("1. Створити адміністратора")
        print("2. Показати користувачів")
        print("3. Вийти")
        
        choice = input("\nОберіть команду (1-3): ").strip()
        
        if choice == "1":
            setup_admin()
        elif choice == "2":
            list_users()
        elif choice == "3":
            print("👋 До побачення!")
            break
        else:
            print("❌ Неправильний вибір!")

if __name__ == "__main__":
    main()