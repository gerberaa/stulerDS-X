import asyncio
from datetime import datetime, timedelta
from typing import Dict, Set
import logging

class SecurityManager:
    def __init__(self, timeout_seconds: int = 300):
        self.timeout_seconds = timeout_seconds
        self.user_sessions: Dict[int, datetime] = {}
        self.authorized_users: Set[int] = set()
        self.logger = logging.getLogger(__name__)
        
    def authorize_user(self, user_id: int) -> None:
        """Авторизувати користувача"""
        self.authorized_users.add(user_id)
        self.user_sessions[user_id] = datetime.now()
        self.logger.info(f"User {user_id} authorized")
        
    def is_user_authorized(self, user_id: int) -> bool:
        """Перевірити чи авторизований користувач"""
        if user_id not in self.authorized_users:
            return False
            
        if user_id not in self.user_sessions:
            self.authorized_users.discard(user_id)
            return False
            
        # Перевіряємо чи не закінчилася сесія
        session_time = self.user_sessions[user_id]
        if datetime.now() - session_time > timedelta(seconds=self.timeout_seconds):
            self.deauthorize_user(user_id)
            return False
            
        return True
        
    def deauthorize_user(self, user_id: int) -> None:
        """Деавторизувати користувача"""
        self.authorized_users.discard(user_id)
        self.user_sessions.pop(user_id, None)
        self.logger.info(f"User {user_id} deauthorized")
        
    def update_user_activity(self, user_id: int) -> None:
        """Оновити активність користувача"""
        if user_id in self.authorized_users:
            self.user_sessions[user_id] = datetime.now()
            
    def get_session_time_left(self, user_id: int) -> int:
        """Отримати час що залишився до закінчення сесії"""
        if user_id not in self.user_sessions:
            return 0
            
        session_time = self.user_sessions[user_id]
        time_left = self.timeout_seconds - (datetime.now() - session_time).total_seconds()
        return max(0, int(time_left))
        
    def check_expired_sessions(self, bot):
        """Перевірити закінчені сесії (синхронна версія)"""
        expired_users = []
        
        for user_id in list(self.authorized_users):
            if not self.is_user_authorized(user_id):
                expired_users.append(user_id)
                
        # Відправляємо повідомлення про закінчення сесії
        for user_id in expired_users:
            try:
                # Використовуємо синхронний метод через requests
                import requests
                from config import BOT_TOKEN
                
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                data = {
                    'chat_id': user_id,
                    'text': "🔒 Ваша сесія закінчилася. Введіть пароль знову для продовження роботи."
                }
                response = requests.post(url, data=data, timeout=10)
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to send session expired message to {user_id}: {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"Failed to send session expired message to {user_id}: {e}")