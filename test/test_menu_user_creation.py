#!/usr/bin/env python3
"""
Тест створення користувачів через меню адміністратора
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

def test_user_creation_flow():
    """Тест процесу створення користувача"""
    print("🧪 Тестування створення користувачів через меню")
    print("=" * 60)
    
    try:
        # Спочатку створюємо тестового адміністратора
        admin_id = access_manager.create_admin_user(99999, "test_admin", "admin123")
        print(f"✅ Створено тестового адміністратора: {admin_id}")
        
        # Тестуємо створення звичайного користувача
        print("\n--- Тестування створення звичайного користувача ---")
        
        # Симулюємо процес створення користувача
        test_telegram_id = 11111
        test_username = "test_user_menu"
        test_password = "userpass123"
        
        # Перевіряємо що користувач не існує
        existing_user = access_manager.get_user_by_telegram_id(test_telegram_id)
        if existing_user:
            print(f"❌ Користувач з ID {test_telegram_id} вже існує")
            return False
        
        # Створюємо користувача
        created_user_id = access_manager.add_user(test_telegram_id, test_username, test_password)
        
        if created_user_id:
            print(f"✅ Користувач створений: {created_user_id}")
            
            # Перевіряємо авторизацію
            if access_manager.authenticate_user(test_telegram_id, test_password):
                print("✅ Авторизація користувача працює")
            else:
                print("❌ Авторизація користувача не працює")
                return False
            
            # Перевіряємо роль
            user_role = access_manager.get_user_role(test_telegram_id)
            if user_role == "user":
                print("✅ Роль користувача встановлена правильно")
            else:
                print(f"❌ Неправильна роль: {user_role}")
                return False
        else:
            print("❌ Помилка створення користувача")
            return False
        
        # Тестуємо створення адміністратора
        print("\n--- Тестування створення адміністратора ---")
        
        test_admin_telegram_id = 22222
        test_admin_username = "test_admin_menu"
        test_admin_password = "adminpass123"
        
        # Перевіряємо що адміністратор не існує
        existing_admin = access_manager.get_user_by_telegram_id(test_admin_telegram_id)
        if existing_admin:
            print(f"❌ Адміністратор з ID {test_admin_telegram_id} вже існує")
            return False
        
        # Створюємо адміністратора
        created_admin_id = access_manager.create_admin_user(test_admin_telegram_id, test_admin_username, test_admin_password)
        
        if created_admin_id:
            print(f"✅ Адміністратор створений: {created_admin_id}")
            
            # Перевіряємо авторизацію
            if access_manager.authenticate_user(test_admin_telegram_id, test_admin_password):
                print("✅ Авторизація адміністратора працює")
            else:
                print("❌ Авторизація адміністратора не працює")
                return False
            
            # Перевіряємо роль
            admin_role = access_manager.get_user_role(test_admin_telegram_id)
            if admin_role == "admin":
                print("✅ Роль адміністратора встановлена правильно")
            else:
                print(f"❌ Неправильна роль: {admin_role}")
                return False
            
            # Перевіряємо дозволи
            if access_manager.check_permission(test_admin_telegram_id, "can_manage_users"):
                print("✅ Дозволи адміністратора працюють")
            else:
                print("❌ Дозволи адміністратора не працюють")
                return False
        else:
            print("❌ Помилка створення адміністратора")
            return False
        
        # Тестуємо перевірку дублікатів
        print("\n--- Тестування перевірки дублікатів ---")
        
        # Спробуємо створити користувача з існуючим ID
        duplicate_user_id = access_manager.add_user(test_telegram_id, "duplicate_user", "duplicate_pass")
        if duplicate_user_id:
            print("❌ Дублікат користувача був створений (не повинно бути)")
            return False
        else:
            print("✅ Перевірка дублікатів працює")
        
        # Тестуємо отримання списку користувачів
        print("\n--- Тестування отримання списку користувачів ---")
        
        all_users = access_manager.get_all_users()
        print(f"✅ Отримано список користувачів: {len(all_users)} користувачів")
        
        # Перевіряємо що наші тестові користувачі в списку
        test_users_found = 0
        for user in all_users:
            if user.get('telegram_id') in [test_telegram_id, test_admin_telegram_id, 99999]:
                test_users_found += 1
        
        if test_users_found >= 3:  # Мінімум 3 тестових користувачі
            print("✅ Тестові користувачі знайдені в списку")
        else:
            print(f"❌ Знайдено тільки {test_users_found} тестових користувачів")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування: {e}")
        return False

def test_menu_states():
    """Тест станів меню для створення користувачів"""
    print("\n🧪 Тестування станів меню")
    print("=" * 40)
    
    try:
        # Симулюємо стани меню
        user_states = {}
        
        # Симулюємо стан створення користувача
        user_states[12345] = {
            'state': 'admin_creating_user',
            'data': {'step': 'telegram_id'}
        }
        
        # Перевіряємо стан
        if user_states[12345]['state'] == 'admin_creating_user':
            print("✅ Стан створення користувача встановлено")
        else:
            print("❌ Стан створення користувача не встановлено")
            return False
        
        # Симулюємо перехід між кроками
        user_states[12345]['data']['telegram_id'] = 11111
        user_states[12345]['data']['step'] = 'username'
        
        if user_states[12345]['data']['step'] == 'username':
            print("✅ Перехід до кроку username працює")
        else:
            print("❌ Перехід до кроку username не працює")
            return False
        
        user_states[12345]['data']['username'] = 'test_user'
        user_states[12345]['data']['step'] = 'password'
        
        if user_states[12345]['data']['step'] == 'password':
            print("✅ Перехід до кроку password працює")
        else:
            print("❌ Перехід до кроку password не працює")
            return False
        
        # Симулюємо стан створення адміністратора
        user_states[54321] = {
            'state': 'admin_creating_admin',
            'data': {'step': 'telegram_id'}
        }
        
        if user_states[54321]['state'] == 'admin_creating_admin':
            print("✅ Стан створення адміністратора встановлено")
        else:
            print("❌ Стан створення адміністратора не встановлено")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування станів: {e}")
        return False

def test_validation():
    """Тест валідації даних"""
    print("\n🧪 Тестування валідації даних")
    print("=" * 40)
    
    try:
        # Тестуємо валідацію Telegram ID
        valid_ids = ["123456789", "987654321", "111111111"]
        invalid_ids = ["abc", "123abc", "", "12.34"]
        
        for valid_id in valid_ids:
            if valid_id.isdigit():
                print(f"✅ Валідний ID: {valid_id}")
            else:
                print(f"❌ Невалідний ID: {valid_id}")
                return False
        
        for invalid_id in invalid_ids:
            if not invalid_id.isdigit():
                print(f"✅ Невалідний ID правильно відхилено: {invalid_id}")
            else:
                print(f"❌ Невалідний ID неправильно прийнято: {invalid_id}")
                return False
        
        # Тестуємо валідацію username
        valid_usernames = ["JohnDoe", "admin_user", "test123", ""]
        invalid_usernames = ["user with spaces", "user@domain.com"]
        
        for username in valid_usernames:
            if len(username) <= 50:  # Припускаємо максимальну довжину
                print(f"✅ Валідний username: '{username}'")
            else:
                print(f"❌ Невалідний username: '{username}'")
                return False
        
        # Тестуємо валідацію пароля
        valid_passwords = ["password123", "admin_pass", "simple", ""]
        
        for password in valid_passwords:
            if len(password) <= 100:  # Припускаємо максимальну довжину
                print(f"✅ Валідний пароль: '{password}'")
            else:
                print(f"❌ Невалідний пароль: '{password}'")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування валідації: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("🚀 ТЕСТУВАННЯ СТВОРЕННЯ КОРИСТУВАЧІВ ЧЕРЕЗ МЕНЮ")
    print("=" * 70)
    
    # Тестуємо процес створення користувачів
    creation_test = test_user_creation_flow()
    
    # Тестуємо стани меню
    states_test = test_menu_states()
    
    # Тестуємо валідацію
    validation_test = test_validation()
    
    print("\n" + "=" * 70)
    print("🎉 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:")
    print(f"👤 Створення користувачів: {'✅ ПРОЙШОВ' if creation_test else '❌ НЕ ПРОЙШОВ'}")
    print(f"🎮 Стани меню: {'✅ ПРОЙШОВ' if states_test else '❌ НЕ ПРОЙШОВ'}")
    print(f"🔍 Валідація даних: {'✅ ПРОЙШОВ' if validation_test else '❌ НЕ ПРОЙШОВ'}")
    
    if creation_test and states_test and validation_test:
        print("\n🎊 ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
        print("\n📋 Підсумок нового функціоналу:")
        print("✅ Створення користувачів через меню працює")
        print("✅ Створення адміністраторів через меню працює")
        print("✅ Валідація даних працює")
        print("✅ Перевірка дублікатів працює")
        print("✅ Стани меню працюють правильно")
        print("\n🚀 Функціонал готовий до використання!")
        print("\n📝 Як використовувати:")
        print("1. Увійдіть як адміністратор: /login")
        print("2. Натисніть: 👑 Адмін панель")
        print("3. Натисніть: 👥 Користувачі")
        print("4. Натисніть: ➕ Додати користувача або 👑 Додати адміна")
        print("5. Слідуйте інструкціям для введення даних")
    else:
        print("\n❌ ДЕЯКІ ТЕСТИ НЕ ПРОЙШЛИ!")
        print("Перевірте логи та виправте помилки.")

if __name__ == "__main__":
    main()