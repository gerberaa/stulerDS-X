import json
import hashlib
import secrets
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AccessManager:
    """Менеджер доступу для управління користувачами та авторизацією"""
    
    def __init__(self, data_file: str = "access_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
        self.authorized_users: Set[int] = set()  # Telegram ID авторизованих користувачів
        self.user_sessions: Dict[int, datetime] = {}  # Сесії користувачів з часом авторизації
        
    def _load_data(self) -> Dict:
        """Завантажити дані з файлу"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Створюємо новий файл з базовою структурою
            default_data = {
                "users": {},
            "settings": {
                "default_password": "admin123",  # Пароль за замовчуванням
                "session_timeout_minutes": 30,  # 30 хвилин
                "max_login_attempts": 3
            }
            }
            self._save_data(default_data)
            return default_data
        except Exception as e:
            logger.error(f"Помилка завантаження даних доступу: {e}")
            return {"users": {}, "settings": {"default_password": "admin123", "session_timeout_minutes": 30, "max_login_attempts": 3}}
    
    def _save_data(self, data: Dict = None) -> None:
        """Зберегти дані в файл"""
        try:
            if data is None:
                data = self.data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Помилка збереження даних доступу: {e}")
    
    def _hash_password(self, password: str) -> str:
        """Хешувати пароль"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_user_id(self) -> str:
        """Згенерувати унікальний ID користувача"""
        return secrets.token_hex(8)
    
    def add_user(self, telegram_id: int, username: str = "", password: str = None) -> str:
        """Додати нового користувача"""
        try:
            # Перевіряємо чи користувач вже існує
            for user_id, user_data in self.data["users"].items():
                if user_data.get("telegram_id") == telegram_id:
                    logger.warning(f"Користувач з Telegram ID {telegram_id} вже існує")
                    return user_id
            
            # Генеруємо новий ID користувача
            user_id = self._generate_user_id()
            
            # Використовуємо пароль за замовчуванням якщо не вказано
            if password is None:
                password = self.data["settings"]["default_password"]
            
            # Створюємо користувача
            user_data = {
                "telegram_id": telegram_id,
                "username": username,
                "password_hash": self._hash_password(password),
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "login_attempts": 0,
                "is_active": True,
                "role": "user",  # Роль користувача (user/admin)
                "permissions": {
                    "can_monitor_twitter": True,
                    "can_monitor_discord": True,
                    "can_manage_users": False,  # Тільки адміністратор
                    "can_view_logs": False,
                    "can_manage_all_projects": False,  # Тільки адміністратор
                    "can_create_projects_for_others": False  # Тільки адміністратор
                }
            }
            
            self.data["users"][user_id] = user_data
            self._save_data()
            
            logger.info(f"Додано нового користувача: {username} (Telegram ID: {telegram_id})")
            return user_id
            
        except Exception as e:
            logger.error(f"Помилка додавання користувача: {e}")
            return ""
    
    def authenticate_user(self, telegram_id: int, password: str) -> bool:
        """Авторизувати користувача"""
        try:
            # Знаходимо користувача за Telegram ID
            user_data = self.get_user_by_telegram_id(telegram_id)
            if not user_data:
                logger.warning(f"Спроба авторизації неіснуючого користувача: {telegram_id}")
                return False
            
            # Перевіряємо чи користувач активний
            if not user_data.get("is_active", True):
                logger.warning(f"Спроба авторизації неактивного користувача: {telegram_id}")
                return False
            
            # Перевіряємо кількість спроб входу
            max_attempts = self.data["settings"]["max_login_attempts"]
            if user_data.get("login_attempts", 0) >= max_attempts:
                logger.warning(f"Перевищено кількість спроб входу для користувача: {telegram_id}")
                return False
            
            # Перевіряємо пароль
            password_hash = self._hash_password(password)
            if user_data["password_hash"] == password_hash:
                # Успішна авторизація
                user_data["last_login"] = datetime.now().isoformat()
                user_data["login_attempts"] = 0
                self.authorized_users.add(telegram_id)
                self.user_sessions[telegram_id] = datetime.now()
                
                # Оновлюємо дані
                self._save_data()
                
                logger.info(f"Користувач {telegram_id} успішно авторизований")
                return True
            else:
                # Невдала спроба
                user_data["login_attempts"] = user_data.get("login_attempts", 0) + 1
                self._save_data()
                
                logger.warning(f"Невдала спроба авторизації користувача: {telegram_id}")
                return False
                
        except Exception as e:
            logger.error(f"Помилка авторизації користувача: {e}")
            return False
    
    def is_authorized(self, telegram_id: int) -> bool:
        """Перевірити чи авторизований користувач"""
        if telegram_id not in self.authorized_users:
            return False
        
        # Перевіряємо чи не закінчилася сесія
        if telegram_id in self.user_sessions:
            session_timeout = timedelta(minutes=self.data["settings"]["session_timeout_minutes"])
            if datetime.now() - self.user_sessions[telegram_id] > session_timeout:
                self.logout_user(telegram_id)
                return False
        
        return True
    
    def update_session_activity(self, telegram_id: int) -> None:
        """Оновити час активності сесії користувача"""
        if telegram_id in self.authorized_users:
            self.user_sessions[telegram_id] = datetime.now()
            logger.debug(f"Оновлено активність сесії користувача {telegram_id}")
    
    def logout_user(self, telegram_id: int) -> None:
        """Вийти з системи"""
        self.authorized_users.discard(telegram_id)
        self.user_sessions.pop(telegram_id, None)
        logger.info(f"Користувач {telegram_id} вийшов з системи")
    
    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict]:
        """Отримати дані користувача за Telegram ID"""
        for user_id, user_data in self.data["users"].items():
            if user_data.get("telegram_id") == telegram_id:
                return user_data
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Отримати дані користувача за ID"""
        return self.data["users"].get(user_id)
    
    def update_user_password(self, telegram_id: int, new_password: str) -> bool:
        """Оновити пароль користувача"""
        try:
            user_data = self.get_user_by_telegram_id(telegram_id)
            if not user_data:
                return False
            
            user_data["password_hash"] = self._hash_password(new_password)
            self._save_data()
            
            logger.info(f"Пароль користувача {telegram_id} оновлено")
            return True
            
        except Exception as e:
            logger.error(f"Помилка оновлення паролю: {e}")
            return False
    
    def deactivate_user(self, telegram_id: int) -> bool:
        """Деактивувати користувача"""
        try:
            user_data = self.get_user_by_telegram_id(telegram_id)
            if not user_data:
                return False
            
            user_data["is_active"] = False
            self.logout_user(telegram_id)
            self._save_data()
            
            logger.info(f"Користувач {telegram_id} деактивований")
            return True
            
        except Exception as e:
            logger.error(f"Помилка деактивації користувача: {e}")
            return False
    
    def activate_user(self, telegram_id: int) -> bool:
        """Активувати користувача"""
        try:
            user_data = self.get_user_by_telegram_id(telegram_id)
            if not user_data:
                return False
            
            user_data["is_active"] = True
            user_data["login_attempts"] = 0  # Скидаємо спроби входу
            self._save_data()
            
            logger.info(f"Користувач {telegram_id} активований")
            return True
            
        except Exception as e:
            logger.error(f"Помилка активації користувача: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Отримати список всіх користувачів"""
        users = []
        for user_id, user_data in self.data["users"].items():
            user_info = {
                "user_id": user_id,
                "telegram_id": user_data.get("telegram_id"),
                "username": user_data.get("username", ""),
                "is_active": user_data.get("is_active", True),
                "last_login": user_data.get("last_login"),
                "created_at": user_data.get("created_at")
            }
            users.append(user_info)
        return users
    
    def check_permission(self, telegram_id: int, permission: str) -> bool:
        """Перевірити дозвіл користувача"""
        if not self.is_authorized(telegram_id):
            return False
        
        user_data = self.get_user_by_telegram_id(telegram_id)
        if not user_data:
            return False
        
        return user_data.get("permissions", {}).get(permission, False)
    
    def set_permission(self, telegram_id: int, permission: str, value: bool) -> bool:
        """Встановити дозвіл користувача"""
        try:
            user_data = self.get_user_by_telegram_id(telegram_id)
            if not user_data:
                return False
            
            if "permissions" not in user_data:
                user_data["permissions"] = {}
            
            user_data["permissions"][permission] = value
            self._save_data()
            
            logger.info(f"Дозвіл {permission} для користувача {telegram_id} встановлено: {value}")
            return True
            
        except Exception as e:
            logger.error(f"Помилка встановлення дозволу: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> None:
        """Очистити закінчені сесії"""
        current_time = datetime.now()
        session_timeout = timedelta(minutes=self.data["settings"]["session_timeout_minutes"])
        
        expired_users = []
        for telegram_id, login_time in self.user_sessions.items():
            if current_time - login_time > session_timeout:
                expired_users.append(telegram_id)
        
        for telegram_id in expired_users:
            self.logout_user(telegram_id)
        
        if expired_users:
            logger.info(f"Очищено {len(expired_users)} закінчених сесій")
    
    def get_user_role(self, telegram_id: int) -> str:
        """Отримати роль користувача"""
        user_data = self.get_user_by_telegram_id(telegram_id)
        if not user_data:
            return "guest"
        return user_data.get("role", "user")
    
    def is_admin(self, telegram_id: int) -> bool:
        """Перевірити чи користувач є адміністратором"""
        return self.get_user_role(telegram_id) == "admin"
    
    def set_user_role(self, telegram_id: int, role: str) -> bool:
        """Встановити роль користувача"""
        try:
            user_data = self.get_user_by_telegram_id(telegram_id)
            if not user_data:
                return False
            
            if role not in ["user", "admin"]:
                logger.error(f"Невірна роль: {role}")
                return False
            
            user_data["role"] = role
            
            # Оновлюємо дозволи залежно від ролі
            if role == "admin":
                user_data["permissions"] = {
                    "can_monitor_twitter": True,
                    "can_monitor_discord": True,
                    "can_manage_users": True,
                    "can_view_logs": True,
                    "can_manage_all_projects": True,
                    "can_create_projects_for_others": True
                }
            else:
                user_data["permissions"] = {
                    "can_monitor_twitter": True,
                    "can_monitor_discord": True,
                    "can_manage_users": False,
                    "can_view_logs": False,
                    "can_manage_all_projects": False,
                    "can_create_projects_for_others": False
                }
            
            self._save_data()
            logger.info(f"Роль користувача {telegram_id} встановлено: {role}")
            return True
            
        except Exception as e:
            logger.error(f"Помилка встановлення ролі: {e}")
            return False
    
    def create_admin_user(self, telegram_id: int, username: str = "", password: str = None) -> str:
        """Створити адміністратора"""
        try:
            # Створюємо користувача
            user_id = self.add_user(telegram_id, username, password)
            
            if user_id:
                # Встановлюємо роль адміністратора
                self.set_user_role(telegram_id, "admin")
                logger.info(f"Створено адміністратора: {username} (Telegram ID: {telegram_id})")
            
            return user_id
            
        except Exception as e:
            logger.error(f"Помилка створення адміністратора: {e}")
            return ""
    
    def get_all_admins(self) -> List[Dict]:
        """Отримати список всіх адміністраторів"""
        admins = []
        for user_id, user_data in self.data["users"].items():
            if user_data.get("role") == "admin":
                admin_info = {
                    "user_id": user_id,
                    "telegram_id": user_data.get("telegram_id"),
                    "username": user_data.get("username", ""),
                    "is_active": user_data.get("is_active", True),
                    "last_login": user_data.get("last_login"),
                    "created_at": user_data.get("created_at")
                }
                admins.append(admin_info)
        return admins
    
    def get_all_users_by_role(self, role: str) -> List[Dict]:
        """Отримати користувачів за роллю"""
        users = []
        for user_id, user_data in self.data["users"].items():
            if user_data.get("role") == role:
                user_info = {
                    "user_id": user_id,
                    "telegram_id": user_data.get("telegram_id"),
                    "username": user_data.get("username", ""),
                    "is_active": user_data.get("is_active", True),
                    "last_login": user_data.get("last_login"),
                    "created_at": user_data.get("created_at")
                }
                users.append(user_info)
        return users
    
    def delete_user(self, telegram_id: int) -> bool:
        """Видалити користувача повністю"""
        try:
            # Знаходимо користувача
            user_to_delete = None
            user_id_to_delete = None
            
            for user_id, user_data in self.data["users"].items():
                if user_data.get("telegram_id") == telegram_id:
                    user_to_delete = user_data
                    user_id_to_delete = user_id
                    break
            
            if not user_to_delete:
                logger.warning(f"Спроба видалення неіснуючого користувача: {telegram_id}")
                return False
            
            # Видаляємо користувача
            del self.data["users"][user_id_to_delete]
            
            # Видаляємо з активних сесій
            self.authorized_users.discard(telegram_id)
            self.user_sessions.pop(telegram_id, None)
            
            self._save_data()
            logger.info(f"Користувач {telegram_id} повністю видалений")
            return True
            
        except Exception as e:
            logger.error(f"Помилка видалення користувача: {e}")
            return False
    
    def search_users(self, query: str) -> List[Dict]:
        """Пошук користувачів за username або Telegram ID"""
        try:
            query = query.lower().strip()
            results = []
            
            for user_id, user_data in self.data["users"].items():
                telegram_id = user_data.get("telegram_id")
                username = user_data.get("username", "").lower()
                
                # Пошук за username
                if query in username:
                    results.append({
                        "user_id": user_id,
                        "telegram_id": telegram_id,
                        "username": user_data.get("username", ""),
                        "role": user_data.get("role", "user"),
                        "is_active": user_data.get("is_active", True),
                        "last_login": user_data.get("last_login"),
                        "created_at": user_data.get("created_at"),
                        "match_type": "username"
                    })
                # Пошук за Telegram ID
                elif query.isdigit() and str(telegram_id) == query:
                    results.append({
                        "user_id": user_id,
                        "telegram_id": telegram_id,
                        "username": user_data.get("username", ""),
                        "role": user_data.get("role", "user"),
                        "is_active": user_data.get("is_active", True),
                        "last_login": user_data.get("last_login"),
                        "created_at": user_data.get("created_at"),
                        "match_type": "telegram_id"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Помилка пошуку користувачів: {e}")
            return []
    
    def change_user_role(self, telegram_id: int, new_role: str) -> bool:
        """Змінити роль користувача"""
        try:
            user_data = self.get_user_by_telegram_id(telegram_id)
            if not user_data:
                logger.warning(f"Спроба зміни ролі неіснуючого користувача: {telegram_id}")
                return False
            
            if new_role not in ["user", "admin"]:
                logger.error(f"Невірна роль: {new_role}")
                return False
            
            old_role = user_data.get("role", "user")
            user_data["role"] = new_role
            
            # Оновлюємо дозволи залежно від ролі
            if new_role == "admin":
                user_data["permissions"] = {
                    "can_monitor_twitter": True,
                    "can_monitor_discord": True,
                    "can_manage_users": True,
                    "can_view_logs": True,
                    "can_manage_all_projects": True,
                    "can_create_projects_for_others": True
                }
            else:
                user_data["permissions"] = {
                    "can_monitor_twitter": True,
                    "can_monitor_discord": True,
                    "can_manage_users": False,
                    "can_view_logs": False,
                    "can_manage_all_projects": False,
                    "can_create_projects_for_others": False
                }
            
            self._save_data()
            logger.info(f"Роль користувача {telegram_id} змінено з {old_role} на {new_role}")
            return True
            
        except Exception as e:
            logger.error(f"Помилка зміни ролі користувача: {e}")
            return False
    
    def reset_user_password(self, telegram_id: int, new_password: str = None) -> bool:
        """Скинути пароль користувача"""
        try:
            user_data = self.get_user_by_telegram_id(telegram_id)
            if not user_data:
                logger.warning(f"Спроба скидання паролю неіснуючого користувача: {telegram_id}")
                return False
            
            if new_password is None:
                new_password = self.data["settings"]["default_password"]
            
            user_data["password_hash"] = self._hash_password(new_password)
            user_data["login_attempts"] = 0  # Скидаємо спроби входу
            
            # Видаляємо з активних сесій
            self.authorized_users.discard(telegram_id)
            self.user_sessions.pop(telegram_id, None)
            
            self._save_data()
            logger.info(f"Пароль користувача {telegram_id} скинуто")
            return True
            
        except Exception as e:
            logger.error(f"Помилка скидання паролю: {e}")
            return False
    
    def get_user_statistics(self) -> Dict:
        """Отримати статистику користувачів"""
        try:
            stats = {
                "total_users": 0,
                "active_users": 0,
                "inactive_users": 0,
                "admin_users": 0,
                "regular_users": 0,
                "online_users": 0,
                "recent_logins": 0
            }
            
            current_time = datetime.now()
            recent_threshold = timedelta(hours=24)  # Останні 24 години
            
            for user_data in self.data["users"].values():
                stats["total_users"] += 1
                
                if user_data.get("is_active", True):
                    stats["active_users"] += 1
                else:
                    stats["inactive_users"] += 1
                
                if user_data.get("role") == "admin":
                    stats["admin_users"] += 1
                else:
                    stats["regular_users"] += 1
                
                # Перевіряємо чи користувач онлайн (має активну сесію)
                telegram_id = user_data.get("telegram_id")
                if telegram_id in self.authorized_users:
                    stats["online_users"] += 1
                
                # Перевіряємо останній вхід
                last_login = user_data.get("last_login")
                if last_login:
                    try:
                        last_login_time = datetime.fromisoformat(last_login)
                        if current_time - last_login_time <= recent_threshold:
                            stats["recent_logins"] += 1
                    except:
                        pass
            
            return stats
            
        except Exception as e:
            logger.error(f"Помилка отримання статистики користувачів: {e}")
            return {}
    
    def get_system_statistics(self) -> Dict:
        """Отримати системну статистику"""
        try:
            stats = {
                "total_users": len(self.data["users"]),
                "active_sessions": len(self.authorized_users),
                "total_projects": 0,
                "active_monitors": 0,
                "system_uptime": "",
                "last_backup": "",
                "storage_usage": 0
            }
            
            # Підраховуємо проекти (якщо є доступ до project_manager)
            try:
                from project_manager import project_manager
                all_projects = project_manager.get_all_projects()
                stats["total_projects"] = len(all_projects)
                
                # Підраховуємо активні монітори
                for project in all_projects:
                    if project.get('is_active', True):
                        stats["active_monitors"] += 1
            except:
                pass
            
            # Системний час роботи (спрощено)
            stats["system_uptime"] = "Доступно"
            
            # Останнє резервне копіювання
            stats["last_backup"] = "Автоматично"
            
            # Використання сховища (спрощено)
            stats["storage_usage"] = len(str(self.data))
            
            return stats
            
        except Exception as e:
            logger.error(f"Помилка отримання системної статистики: {e}")
            return {}
    
    def cleanup_inactive_sessions(self) -> int:
        """Очистити неактивні сесії"""
        try:
            current_time = datetime.now()
            cleaned_count = 0
            
            inactive_users = []
            for telegram_id, session_data in self.user_sessions.items():
                last_activity = session_data.get('last_activity')
                if last_activity:
                    try:
                        last_activity_time = datetime.fromisoformat(last_activity)
                        if current_time - last_activity_time > timedelta(hours=24):  # 24 години неактивності
                            inactive_users.append(telegram_id)
                    except:
                        inactive_users.append(telegram_id)
            
            # Видаляємо неактивні сесії
            for telegram_id in inactive_users:
                self.authorized_users.discard(telegram_id)
                self.user_sessions.pop(telegram_id, None)
                cleaned_count += 1
            
            if cleaned_count > 0:
                self._save_data()
                logger.info(f"Очищено {cleaned_count} неактивних сесій")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Помилка очищення сесій: {e}")
            return 0
    
    def backup_data(self) -> bool:
        """Створити резервну копію даних"""
        try:
            import shutil
            import os
            from datetime import datetime
            
            backup_dir = "backups"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"access_data_backup_{timestamp}.json")
            
            shutil.copy2(self.data_file, backup_file)
            logger.info(f"Резервна копія створена: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Помилка створення резервної копії: {e}")
            return False
    
    def get_logs(self, limit: int = 50) -> List[str]:
        """Отримати логи системи"""
        try:
            # Спрощена реалізація логів
            logs = []
            
            # Додаємо інформацію про користувачів
            logs.append(f"[INFO] Загальна кількість користувачів: {len(self.data['users'])}")
            logs.append(f"[INFO] Активних сесій: {len(self.authorized_users)}")
            
            # Додаємо інформацію про останні дії
            for user_data in list(self.data["users"].values())[-5:]:  # Останні 5 користувачів
                username = user_data.get('username', 'Без імені')
                telegram_id = user_data.get('telegram_id')
                role = user_data.get('role', 'user')
                logs.append(f"[USER] {username} (ID: {telegram_id}, Роль: {role})")
            
            return logs[-limit:]  # Повертаємо останні записи
            
        except Exception as e:
            logger.error(f"Помилка отримання логів: {e}")
            return [f"[ERROR] Помилка отримання логів: {str(e)}"]
    
    def reset_system(self) -> bool:
        """Скинути систему (видалити всіх користувачів крім адміністраторів)"""
        try:
            # Створюємо резервну копію перед скиданням
            self.backup_data()
            
            # Зберігаємо тільки адміністраторів
            admin_users = {}
            for user_id, user_data in self.data["users"].items():
                if user_data.get('role') == 'admin':
                    admin_users[user_id] = user_data
            
            # Очищаємо всіх користувачів
            self.data["users"] = admin_users
            self.authorized_users.clear()
            self.user_sessions.clear()
            
            self._save_data()
            logger.info("Система скинута, збережено тільки адміністраторів")
            return True
            
        except Exception as e:
            logger.error(f"Помилка скидання системи: {e}")
            return False

# Глобальний екземпляр менеджера доступу
access_manager = AccessManager()