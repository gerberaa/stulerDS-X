#!/usr/bin/env python3
"""
Скрипт для створення першого адміністратора системи
"""

import json
import hashlib
import secrets
from datetime import datetime

def setup_first_admin():
    """Створити першого адміністратора"""
    print("🔧 Налаштування першого адміністратора системи")
    print("=" * 50)
    
    # Запитуємо дані адміністратора
    telegram_id = input("Введіть ваш Telegram ID: ").strip()
    username = input("Введіть username (необов'язково): ").strip()
    password = input("Введіть пароль (Enter для 'admin123'): ").strip()
    
    if not telegram_id.isdigit():
        print("❌ Telegram ID повинен бути числом!")
        return False
    
    telegram_id = int(telegram_id)
    
    if not username:
        username = f"admin_{telegram_id}"
    
    if not password:
        password = "admin123"
    
    # Хешуємо пароль
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Створюємо структуру даних
    access_data = {
        "users": {
            secrets.token_hex(8): {
                "telegram_id": telegram_id,
                "username": username,
                "password_hash": password_hash,
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "login_attempts": 0,
                "is_active": True,
                "role": "admin",
                "permissions": {
                    "can_monitor_twitter": True,
                    "can_monitor_discord": True,
                    "can_manage_users": True,
                    "can_view_logs": True,
                    "can_manage_all_projects": True,
                    "can_create_projects_for_others": True
                }
            }
        },
        "settings": {
            "default_password": "admin123",
            "session_timeout_minutes": 30,
            "max_login_attempts": 3
        }
    }
    
    # Зберігаємо в файл
    try:
        with open("access_data.json", "w", encoding="utf-8") as f:
            json.dump(access_data, f, ensure_ascii=False, indent=2)
        
        print("\n✅ Перший адміністратор успішно створений!")
        print(f"👤 Username: {username}")
        print(f"🆔 Telegram ID: {telegram_id}")
        print(f"🔐 Пароль: {password}")
        print(f"👑 Роль: Адміністратор")
        print("\n📝 Тепер ви можете:")
        print("1. Запустити бота: python bot.py")
        print("2. Увійти в систему: /login")
        print("3. Використовувати адмін панель: 👑 Адмін панель")
        print("4. Створювати нових користувачів: /admin_create_user")
        print("5. Створювати нових адмінів: /admin_create_admin")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка створення адміністратора: {e}")
        return False

if __name__ == "__main__":
    setup_first_admin()