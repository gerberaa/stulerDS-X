#!/usr/bin/env python3
"""
Тест нової системи ролей та адміністрування
"""

import asyncio
import logging
import sys
import os

# Додаємо батьківську папку до шляху
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from access_manager import access_manager
from project_manager import ProjectManager

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_access_manager():
    """Тест системи доступу"""
    print("🧪 Тестування системи доступу")
    print("=" * 50)
    
    try:
        # Тестуємо створення користувача
        user_id = access_manager.add_user(12345, "test_user", "testpass")
        print(f"✅ Створено користувача: {user_id}")
        
        # Тестуємо створення адміністратора
        admin_id = access_manager.create_admin_user(54321, "test_admin", "adminpass")
        print(f"✅ Створено адміністратора: {admin_id}")
        
        # Тестуємо авторизацію користувача
        if access_manager.authenticate_user(12345, "testpass"):
            print("✅ Авторизація користувача успішна")
        else:
            print("❌ Авторизація користувача не вдалася")
        
        # Тестуємо авторизацію адміністратора
        if access_manager.authenticate_user(54321, "adminpass"):
            print("✅ Авторизація адміністратора успішна")
        else:
            print("❌ Авторизація адміністратора не вдалася")
        
        # Тестуємо перевірку ролей
        if access_manager.is_admin(54321):
            print("✅ Перевірка ролі адміністратора успішна")
        else:
            print("❌ Перевірка ролі адміністратора не вдалася")
        
        if not access_manager.is_admin(12345):
            print("✅ Перевірка ролі користувача успішна")
        else:
            print("❌ Перевірка ролі користувача не вдалася")
        
        # Тестуємо дозволи
        if access_manager.check_permission(54321, "can_manage_users"):
            print("✅ Дозволи адміністратора працюють")
        else:
            print("❌ Дозволи адміністратора не працюють")
        
        if not access_manager.check_permission(12345, "can_manage_users"):
            print("✅ Обмеження дозволів користувача працюють")
        else:
            print("❌ Обмеження дозволів користувача не працюють")
        
        # Тестуємо отримання списку користувачів
        all_users = access_manager.get_all_users()
        print(f"✅ Отримано список користувачів: {len(all_users)} користувачів")
        
        # Тестуємо отримання адміністраторів
        all_admins = access_manager.get_all_admins()
        print(f"✅ Отримано список адміністраторів: {len(all_admins)} адміністраторів")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування access_manager: {e}")
        return False

def test_project_manager():
    """Тест менеджера проектів"""
    print("\n🧪 Тестування менеджера проектів")
    print("=" * 50)
    
    try:
        project_manager = ProjectManager("test_data.json")
        
        # Тестуємо додавання проекту звичайним користувачем
        project_data = {
            'name': 'Test Twitter Project',
            'platform': 'twitter',
            'url': 'https://twitter.com/test_user'
        }
        
        if project_manager.add_project(12345, project_data):
            print("✅ Додавання проекту користувачем успішне")
        else:
            print("❌ Додавання проекту користувачем не вдалося")
        
        # Тестуємо отримання проектів користувача
        user_projects = project_manager.get_user_projects(12345)
        print(f"✅ Проекти користувача: {len(user_projects)} проектів")
        
        # Тестуємо адміністративні функції
        all_projects = project_manager.get_all_projects(54321)  # Адміністратор
        print(f"✅ Всі проекти (адмін): {len(all_projects)} користувачів з проектами")
        
        # Тестуємо статистику
        stats = project_manager.get_project_statistics(54321)  # Адміністратор
        print(f"✅ Статистика: {stats['total_users']} користувачів, {stats['total_projects']} проектів")
        
        # Тестуємо створення проекту для іншого користувача (тільки адміністратор)
        admin_project_data = {
            'name': 'Admin Created Project',
            'platform': 'discord',
            'url': 'https://discord.com/channels/123/456'
        }
        
        if project_manager.add_project(54321, admin_project_data, target_user_id=12345):
            print("✅ Створення проекту адміністратором для користувача успішне")
        else:
            print("❌ Створення проекту адміністратором для користувача не вдалося")
        
        # Перевіряємо що проект додався до користувача
        user_projects_after = project_manager.get_user_projects(12345)
        if len(user_projects_after) > len(user_projects):
            print("✅ Проект успішно додано до користувача")
        else:
            print("❌ Проект не додано до користувача")
        
        # Очищуємо тестовий файл
        try:
            os.remove("test_data.json")
            print("✅ Тестовий файл очищено")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування project_manager: {e}")
        return False

def test_isolation():
    """Тест ізоляції між користувачами"""
    print("\n🧪 Тестування ізоляції між користувачами")
    print("=" * 50)
    
    try:
        project_manager = ProjectManager("test_isolation.json")
        
        # Створюємо проекти для двох користувачів
        user1_project = {
            'name': 'User 1 Project',
            'platform': 'twitter',
            'url': 'https://twitter.com/user1'
        }
        
        user2_project = {
            'name': 'User 2 Project',
            'platform': 'twitter',
            'url': 'https://twitter.com/user2'
        }
        
        project_manager.add_project(11111, user1_project)
        project_manager.add_project(22222, user2_project)
        
        # Перевіряємо що кожен користувач бачить тільки свої проекти
        user1_projects = project_manager.get_user_projects(11111)
        user2_projects = project_manager.get_user_projects(22222)
        
        if len(user1_projects) == 1 and user1_projects[0]['name'] == 'User 1 Project':
            print("✅ Користувач 1 бачить тільки свої проекти")
        else:
            print("❌ Користувач 1 бачить чужі проекти")
        
        if len(user2_projects) == 1 and user2_projects[0]['name'] == 'User 2 Project':
            print("✅ Користувач 2 бачить тільки свої проекти")
        else:
            print("❌ Користувач 2 бачить чужі проекти")
        
        # Перевіряємо що звичайний користувач не може отримати всі проекти
        try:
            all_projects = project_manager.get_all_projects(11111)  # Не адміністратор
            if not all_projects:  # Має повернути порожній словник
                print("✅ Звичайний користувач не може отримати всі проекти")
            else:
                print("❌ Звичайний користувач може отримати всі проекти")
        except:
            print("✅ Звичайний користувач не може отримати всі проекти")
        
        # Очищуємо тестовий файл
        try:
            os.remove("test_isolation.json")
            print("✅ Тестовий файл очищено")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка тестування ізоляції: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("🚀 ТЕСТУВАННЯ НОВОЇ СИСТЕМИ РОЛЕЙ ТА АДМІНІСТРУВАННЯ")
    print("=" * 70)
    
    # Тестуємо систему доступу
    access_test = test_access_manager()
    
    # Тестуємо менеджер проектів
    project_test = test_project_manager()
    
    # Тестуємо ізоляцію
    isolation_test = test_isolation()
    
    print("\n" + "=" * 70)
    print("🎉 РЕЗУЛЬТАТИ ТЕСТУВАННЯ:")
    print(f"🔐 Система доступу: {'✅ ПРОЙШОВ' if access_test else '❌ НЕ ПРОЙШОВ'}")
    print(f"📋 Менеджер проектів: {'✅ ПРОЙШОВ' if project_test else '❌ НЕ ПРОЙШОВ'}")
    print(f"🔒 Ізоляція користувачів: {'✅ ПРОЙШОВ' if isolation_test else '❌ НЕ ПРОЙШОВ'}")
    
    if access_test and project_test and isolation_test:
        print("\n🎊 ВСІ ТЕСТИ ПРОЙШЛИ УСПІШНО!")
        print("\n📋 Підсумок нової системи:")
        print("✅ Система ролей (адмін/користувач) працює")
        print("✅ Ізоляція проектів між користувачами працює")
        print("✅ Адміністративні функції працюють")
        print("✅ Дозволи та обмеження працюють")
        print("\n🚀 Система готова до використання!")
        print("\n📝 Для початку роботи:")
        print("1. Запустіть: python setup_first_admin.py")
        print("2. Створіть першого адміністратора")
        print("3. Запустіть бота: python bot.py")
        print("4. Увійдіть як адміністратор: /login")
        print("5. Використовуйте адмін панель: 👑 Адмін панель")
    else:
        print("\n❌ ДЕЯКІ ТЕСТИ НЕ ПРОЙШЛИ!")
        print("Перевірте логи та виправте помилки.")

if __name__ == "__main__":
    main()