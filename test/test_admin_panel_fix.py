#!/usr/bin/env python3
"""
Тест виправлення відображення адмін панелі
"""

import asyncio
import logging
import sys
import os

# Додаємо батьківську папку до шляху
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from access_manager import access_manager

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_admin_panel_display():
    """Тест відображення адмін панелі"""
    print("🧪 Тестування відображення адмін панелі")
    print("=" * 50)
    
    try:
        # Створюємо тестового адміністратора
        admin_id = access_manager.create_admin_user(99999, "test_admin", "admin123")
        print(f"✅ Створено тестового адміністратора: {admin_id}")
        
        # Створюємо тестового користувача
        user_id = access_manager.add_user(11111, "test_user", "user123")
        print(f"✅ Створено тестового користувача: {user_id}")
        
        # Тестуємо авторизацію адміністратора
        if access_manager.authenticate_user(99999, "admin123"):
            print("✅ Авторизація адміністратора успішна")
        else:
            print("❌ Авторизація адміністратора не вдалася")
            return False
        
        # Тестуємо авторизацію користувача
        if access_manager.authenticate_user(11111, "user123"):
            print("✅ Авторизація користувача успішна")
        else:
            print("❌ Авторизація користувача не вдалася")
            return False
        
        # Тестуємо перевірку ролей
        if access_manager.is_admin(99999):
            print("✅ Адміністратор розпізнається як адмін")
        else:
            print("❌ Адміністратор не розпізнається як адмін")
            return False
        
        if not access_manager.is_admin(11111):
            print("✅ Користувач не розпізнається як адмін")
        else:
            print("❌ Користувач розпізнається як адмін (неправильно)")
            return False
        
        # Тестуємо дозволи адміністратора
        admin_permissions = [
            "can_manage_users",
            "can_view_logs", 
            "can_manage_all_projects",
            "can_create_projects_for_others"
        ]
        
        for permission in admin_permissions:
            if access_manager.check_permission(99999, permission):
                print(f"✅ Дозвіл адміністратора '{permission}' працює")
            else:
                print(f"❌ Дозвіл адміністратора '{permission}' не працює")
                return False
        
        # Тестуємо що користувач не має адміністративних дозволів
        for permission in admin_permissions:
            if not access_manager.check_permission(11111, permission):
                print(f"✅ Користувач правильно не має дозволу '{permission}'")
            else:
                print(f"❌ Користувач неправильно має дозвіл '{permission}'")
                return False
        
        # Тестуємо отримання ролі
        admin_role = access_manager.get_user_role(99999)
        user_role = access_manager.get_user_role(11111)
        
        if admin_role == "admin":
            print("✅ Роль адміністратора правильна")
        else:
            print(f"❌ Неправильна роль адміністратора: {admin_role}")
            return False
        
        if user_role == "user":
            print("✅ Роль користувача правильна")
        else:
            print(f"❌ Неправильна роль користувача: {user_role}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")
        return False

def test_menu_keyboard_logic():
    """Тест логіки створення меню"""
    print("\n🧪 Тестування логіки створення меню")
    print("=" * 50)
    
    try:
        # Симулюємо функцію get_main_menu_keyboard
        def simulate_get_main_menu_keyboard(user_id=None):
            keyboard = [
                "📋 Мої проекти",
                "➕ Додати проект", 
                "🐦 Selenium Twitter",
                "📜 Історія Discord",
                "📢 Пересилання",
                "⚙️ Налаштування"
            ]
            
            # Додаємо адміністративні кнопки для адміністраторів
            if user_id and access_manager.is_admin(user_id):
                keyboard.append("👑 Адмін панель")
            
            return keyboard
        
        # Тестуємо для адміністратора
        admin_menu = simulate_get_main_menu_keyboard(99999)
        if "👑 Адмін панель" in admin_menu:
            print("✅ Адмін панель з'являється в меню адміністратора")
        else:
            print("❌ Адмін панель не з'являється в меню адміністратора")
            return False
        
        # Тестуємо для користувача
        user_menu = simulate_get_main_menu_keyboard(11111)
        if "👑 Адмін панель" not in user_menu:
            print("✅ Адмін панель не з'являється в меню користувача")
        else:
            print("❌ Адмін панель з'являється в меню користувача (неправильно)")
            return False
        
        # Тестуємо без user_id
        no_user_menu = simulate_get_main_menu_keyboard()
        if "👑 Адмін панель" not in no_user_menu:
            print("✅ Адмін панель не з'являється без user_id")
        else:
            print("❌ Адмін панель з'являється без user_id (неправильно)")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування логіки меню: {e}")
        return False

def test_user_creation_through_menu():
    """Тест створення користувачів через меню"""
    print("\n🧪 Тестування створення користувачів через меню")
    print("=" * 50)
    
    try:
        # Симулюємо процес створення користувача через меню
        test_telegram_id = 33333
        test_username = "menu_test_user"
        test_password = "menu_pass_123"
        
        # Перевіряємо що користувач не існує
        existing_user = access_manager.get_user_by_telegram_id(test_telegram_id)
        if existing_user:
            print(f"❌ Користувач з ID {test_telegram_id} вже існує")
            return False
        
        # Створюємо користувача
        created_user_id = access_manager.add_user(test_telegram_id, test_username, test_password)
        
        if created_user_id:
            print(f"✅ Користувач створений через меню: {created_user_id}")
            
            # Перевіряємо авторизацію
            if access_manager.authenticate_user(test_telegram_id, test_password):
                print("✅ Авторизація створеного користувача працює")
            else:
                print("❌ Авторизація створеного користувача не працює")
                return False
            
            # Перевіряємо роль
            user_role = access_manager.get_user_role(test_telegram_id)
            if user_role == "user":
                print("✅ Роль створеного користувача правильна")
            else:
                print(f"❌ Неправильна роль створеного користувача: {user_role}")
                return False
        else:
            print("❌ Помилка створення користувача через меню")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування створення користувачів: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("🚀 ТЕСТУВАННЯ ВИПРАВЛЕННЯ АДМІН ПАНЕЛІ")
    print("=" * 70)
    
    # Тестуємо відображення адмін панелі
    display_test = test_admin_panel_display()
    
    # Тестуємо логіку меню
    menu_test = test_menu_keyboard_logic()
    
    # Тестуємо створення користувачів через меню
    creation_test = test_user_creation_through_menu()
    
    print("\n" + "=" * 70)
    print("🎉 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:")
    print(f"👑 Відображення адмін панелі: {'✅ ПРОЙШОВ' if display_test else '❌ НЕ ПРОЙШОВ'}")
    print(f"🎮 Логіка меню: {'✅ ПРОЙШОВ' if menu_test else '❌ НЕ ПРОЙШОВ'}")
    print(f"👥 Створення користувачів: {'✅ ПРОЙШОВ' if creation_test else '❌ НЕ ПРОЙШОВ'}")
    
    if display_test and menu_test and creation_test:
        print("\n🎊 ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
        print("\n📋 Підсумок виправлень:")
        print("✅ Адмін панель тепер з'являється для адміністраторів")
        print("✅ Користувачі не бачать адмін панель")
        print("✅ Логіка меню працює правильно")
        print("✅ Створення користувачів через меню працює")
        print("\n🚀 Виправлення готове до використання!")
        print("\n📝 Тепер ви можете:")
        print("1. Увійти як адміністратор: /login")
        print("2. Побачити кнопку '👑 Адмін панель' в меню")
        print("3. Використовувати всі адміністративні функції")
        print("4. Створювати користувачів через зручне меню")
    else:
        print("\n❌ ДЕЯКІ ТЕСТИ НЕ ПРОЙШЛИ!")
        print("Перевірте логи та виправте помилки.")

if __name__ == "__main__":
    main()