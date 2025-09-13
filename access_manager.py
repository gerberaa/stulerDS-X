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
                "permissions": {
                    "can_monitor_twitter": True,
                    "can_monitor_discord": True,
                    "can_manage_users": False,  # Тільки адміністратор
                    "can_view_logs": False
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

# Глобальний екземпляр менеджера доступу
access_manager = AccessManager()