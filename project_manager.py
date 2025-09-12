import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class ProjectManager:
    def __init__(self, data_file: str = "data.json"):
        self.data_file = data_file
        self.data: Dict[str, Any] = {
            'projects': {},  # user_id -> projects
            'users': {},    # user_id -> user_data
            'settings': {}, # global settings
            'metadata': {
                'version': '1.0',
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        }
        self.logger = logging.getLogger(__name__)
        self._last_save = datetime.now()
        self._save_interval = 30  # Зберігаємо кожні 30 секунд
        self.load_data()
        
    def load_data(self) -> None:
        """Завантажити дані з файлу"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    
                # Міграція зі старої структури (projects.json)
                if 'projects' not in loaded_data and isinstance(loaded_data, dict):
                    # Стара структура - весь файл це проекти
                    self.data['projects'] = loaded_data
                    self.logger.info("Міграція зі старої структури даних")
                else:
                    # Нова структура
                    self.data.update(loaded_data)
                    
                self.logger.info(f"Завантажено дані: {len(self.data['projects'])} користувачів з проектами")
            else:
                self.logger.info("Створено новий файл даних")
        except Exception as e:
            self.logger.error(f"Помилка завантаження даних: {e}")
            
    def save_data(self, force: bool = False) -> None:
        """Зберегти дані в файл (з кешуванням)"""
        try:
            now = datetime.now()
            
            # Зберігаємо тільки якщо пройшло достатньо часу або примусово
            if not force and (now - self._last_save).seconds < self._save_interval:
                return
                
            self.data['metadata']['last_updated'] = now.isoformat()
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self._last_save = now
        except Exception as e:
            self.logger.error(f"Помилка збереження даних: {e}")
            
    def add_project(self, user_id: int, project_data: Dict) -> bool:
        """Додати новий проект"""
        try:
            user_id_str = str(user_id)
            if user_id_str not in self.data['projects']:
                self.data['projects'][user_id_str] = []
                
            # Додаємо ID проекту та час створення
            project_data['id'] = len(self.data['projects'][user_id_str]) + 1
            project_data['created_at'] = datetime.now().isoformat()
            
            self.data['projects'][user_id_str].append(project_data)
            self.save_data()
            self.logger.info(f"Додано проект для користувача {user_id}: {project_data['name']}")
            return True
        except Exception as e:
            self.logger.error(f"Помилка додавання проекту: {e}")
            return False
            
    def get_user_projects(self, user_id: int) -> List[Dict]:
        """Отримати проекти користувача"""
        return self.data['projects'].get(str(user_id), [])
        
    def delete_project(self, user_id: int, project_id: int) -> bool:
        """Видалити проект"""
        try:
            user_id_str = str(user_id)
            if user_id_str in self.data['projects']:
                projects = self.data['projects'][user_id_str]
                for i, project in enumerate(projects):
                    if project['id'] == project_id:
                        del projects[i]
                        self.save_data()
                        self.logger.info(f"Видалено проект {project_id} для користувача {user_id}")
                        return True
            return False
        except Exception as e:
            self.logger.error(f"Помилка видалення проекту: {e}")
            return False
            
    def get_project_by_id(self, user_id: int, project_id: int) -> Optional[Dict]:
        """Отримати проект за ID"""
        projects = self.get_user_projects(user_id)
        for project in projects:
            if project['id'] == project_id:
                return project
        return None
        
    def format_projects_list(self, user_id: int) -> str:
        """Форматований список проектів користувача"""
        projects = self.get_user_projects(user_id)
        if not projects:
            return "У вас поки немає проектів для моніторингу."
            
        result = "📋 Ваші проекти для моніторингу:\n\n"
        for project in projects:
            platform_emoji = "🐦" if project['platform'] == 'twitter' else "💬"
            result += f"{platform_emoji} **{project['name']}**\n"
            result += f"   Платформа: {project['platform'].title()}\n"
            result += f"   Посилання: {project['url']}\n"
            result += f"   Створено: {project['created_at'][:10]}\n\n"
            
        return result
    
    # Методи для роботи з користувачами
    def add_user(self, user_id: int, user_data: Dict) -> bool:
        """Додати користувача"""
        try:
            user_id_str = str(user_id)
            self.data['users'][user_id_str] = {
                'id': user_id,
                'first_name': user_data.get('first_name', ''),
                'username': user_data.get('username', ''),
                'created_at': datetime.now().isoformat(),
                'last_seen': datetime.now().isoformat()
            }
            self.save_data()
            self.logger.info(f"Додано користувача {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Помилка додавання користувача: {e}")
            return False
    
    def update_user_last_seen(self, user_id: int) -> None:
        """Оновити час останнього візиту користувача"""
        try:
            user_id_str = str(user_id)
            if user_id_str in self.data['users']:
                self.data['users'][user_id_str]['last_seen'] = datetime.now().isoformat()
                self.save_data()
        except Exception as e:
            self.logger.error(f"Помилка оновлення користувача: {e}")
    
    def get_user_data(self, user_id: int) -> Optional[Dict]:
        """Отримати дані користувача"""
        return self.data['users'].get(str(user_id))
    
    def get_all_users(self) -> Dict:
        """Отримати всіх користувачів"""
        return self.data['users']
    
    # Методи для роботи з налаштуваннями
    def set_setting(self, key: str, value: Any) -> bool:
        """Встановити налаштування"""
        try:
            self.data['settings'][key] = value
            self.save_data()
            self.logger.info(f"Встановлено налаштування {key}")
            return True
        except Exception as e:
            self.logger.error(f"Помилка встановлення налаштування: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Отримати налаштування"""
        return self.data['settings'].get(key, default)
    
    def get_all_settings(self) -> Dict:
        """Отримати всі налаштування"""
        return self.data['settings']
    
    # Методи для роботи з налаштуваннями пересилання
    def set_forward_channel(self, user_id: int, channel_id: str) -> bool:
        """Встановити канал для пересилання сповіщень"""
        try:
            user_id_str = str(user_id)
            if 'forward_settings' not in self.data['settings']:
                self.data['settings']['forward_settings'] = {}
            
            self.data['settings']['forward_settings'][user_id_str] = {
                'channel_id': channel_id,
                'enabled': True,
                'created_at': datetime.now().isoformat()
            }
            self.save_data()
            self.logger.info(f"Встановлено канал пересилання для користувача {user_id}: {channel_id}")
            return True
        except Exception as e:
            self.logger.error(f"Помилка встановлення каналу пересилання: {e}")
            return False
    
    def get_forward_channel(self, user_id: int) -> Optional[str]:
        """Отримати канал для пересилання сповіщень"""
        user_id_str = str(user_id)
        forward_settings = self.data['settings'].get('forward_settings', {})
        user_settings = forward_settings.get(user_id_str, {})
        
        if user_settings.get('enabled', False):
            return user_settings.get('channel_id')
        return None
    
    def enable_forward(self, user_id: int) -> bool:
        """Увімкнути пересилання сповіщень"""
        try:
            user_id_str = str(user_id)
            if 'forward_settings' not in self.data['settings']:
                self.data['settings']['forward_settings'] = {}
            
            if user_id_str not in self.data['settings']['forward_settings']:
                self.data['settings']['forward_settings'][user_id_str] = {}
            
            self.data['settings']['forward_settings'][user_id_str]['enabled'] = True
            self.save_data()
            self.logger.info(f"Увімкнено пересилання для користувача {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Помилка увімкнення пересилання: {e}")
            return False
    
    def disable_forward(self, user_id: int) -> bool:
        """Вимкнути пересилання сповіщень"""
        try:
            user_id_str = str(user_id)
            if 'forward_settings' not in self.data['settings']:
                self.data['settings']['forward_settings'] = {}
            
            if user_id_str not in self.data['settings']['forward_settings']:
                self.data['settings']['forward_settings'][user_id_str] = {}
            
            self.data['settings']['forward_settings'][user_id_str]['enabled'] = False
            self.save_data()
            self.logger.info(f"Вимкнено пересилання для користувача {user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Помилка вимкнення пересилання: {e}")
            return False
    
    def get_forward_status(self, user_id: int) -> Dict:
        """Отримати статус пересилання"""
        user_id_str = str(user_id)
        forward_settings = self.data['settings'].get('forward_settings', {})
        user_settings = forward_settings.get(user_id_str, {})
        
        return {
            'enabled': user_settings.get('enabled', False),
            'channel_id': user_settings.get('channel_id', ''),
            'created_at': user_settings.get('created_at', '')
        }
    
    # Методи для відстеження повідомлень
    def add_sent_message(self, message_id: str, channel_id: str, user_id: int) -> bool:
        """Додати ID відправленого повідомлення (оптимізовано)"""
        try:
            if 'sent_messages' not in self.data['settings']:
                self.data['settings']['sent_messages'] = {}
            
            user_id_str = str(user_id)
            if user_id_str not in self.data['settings']['sent_messages']:
                self.data['settings']['sent_messages'][user_id_str] = {}
            
            if channel_id not in self.data['settings']['sent_messages'][user_id_str]:
                self.data['settings']['sent_messages'][user_id_str][channel_id] = []
            
            # Додаємо ID повідомлення з часом
            self.data['settings']['sent_messages'][user_id_str][channel_id].append({
                'message_id': message_id,
                'timestamp': datetime.now().isoformat()
            })
            
            # Обмежуємо кількість збережених повідомлень (останні 500 для швидкості)
            if len(self.data['settings']['sent_messages'][user_id_str][channel_id]) > 500:
                self.data['settings']['sent_messages'][user_id_str][channel_id] = \
                    self.data['settings']['sent_messages'][user_id_str][channel_id][-500:]
            
            # Зберігаємо тільки при необхідності
            self.save_data()
            return True
        except Exception as e:
            self.logger.error(f"Помилка додавання відправленого повідомлення: {e}")
            return False
    
    def is_message_sent(self, message_id: str, channel_id: str, user_id: int) -> bool:
        """Перевірити чи повідомлення вже було відправлено"""
        try:
            user_id_str = str(user_id)
            sent_messages = self.data['settings'].get('sent_messages', {})
            user_messages = sent_messages.get(user_id_str, {})
            channel_messages = user_messages.get(channel_id, [])
            
            for msg in channel_messages:
                if msg['message_id'] == message_id:
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Помилка перевірки відправленого повідомлення: {e}")
            return False
    
    def cleanup_old_messages(self, hours: int = 24) -> None:
        """Очистити старі повідомлення (старші за вказану кількість годин)"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            if 'sent_messages' not in self.data['settings']:
                return
            
            for user_id_str in self.data['settings']['sent_messages']:
                for channel_id in self.data['settings']['sent_messages'][user_id_str]:
                    messages = self.data['settings']['sent_messages'][user_id_str][channel_id]
                    # Фільтруємо повідомлення новіші за cutoff_time
                    self.data['settings']['sent_messages'][user_id_str][channel_id] = [
                        msg for msg in messages 
                        if datetime.fromisoformat(msg['timestamp']) > cutoff_time
                    ]
            
            self.save_data()
            self.logger.info(f"Очищено старі повідомлення (старші за {hours} годин)")
        except Exception as e:
            self.logger.error(f"Помилка очищення старих повідомлень: {e}")
    
    # Методи для статистики
    def get_statistics(self) -> Dict:
        """Отримати статистику"""
        total_users = len(self.data['users'])
        total_projects = sum(len(projects) for projects in self.data['projects'].values())
        
        discord_projects = 0
        twitter_projects = 0
        
        for projects in self.data['projects'].values():
            for project in projects:
                if project.get('platform') == 'discord':
                    discord_projects += 1
                elif project.get('platform') == 'twitter':
                    twitter_projects += 1
        
        return {
            'total_users': total_users,
            'total_projects': total_projects,
            'discord_projects': discord_projects,
            'twitter_projects': twitter_projects,
            'data_file_size': os.path.getsize(self.data_file) if os.path.exists(self.data_file) else 0,
            'last_updated': self.data['metadata']['last_updated']
        }
    
    def export_data(self, export_file: str = None) -> str:
        """Експортувати дані"""
        if not export_file:
            export_file = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Дані експортовано в {export_file}")
            return export_file
        except Exception as e:
            self.logger.error(f"Помилка експорту: {e}")
            return ""
    
    def import_data(self, import_file: str) -> bool:
        """Імпортувати дані"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
            
            # Створюємо резервну копію
            backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.export_data(backup_file)
            
            # Імпортуємо дані
            self.data.update(imported_data)
            self.save_data()
            
            self.logger.info(f"Дані імпортовано з {import_file}")
            return True
        except Exception as e:
            self.logger.error(f"Помилка імпорту: {e}")
            return False