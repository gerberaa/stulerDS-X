import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
import json
import re

class DiscordMonitor:
    def __init__(self, authorization_token: str):
        self.authorization = authorization_token
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)
        self.last_message_ids: Dict[str, str] = {}  # channel_id -> last_message_id
        self.monitoring_channels: Set[str] = set()
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                'Authorization': self.authorization,
                'User-Agent': 'DiscordBot (https://github.com/discord/discord-api-docs, 1.0)',
                'Content-Type': 'application/json',
                'X-RateLimit-Precision': 'millisecond'
            },
            timeout=aiohttp.ClientTimeout(total=10)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
    def add_channel(self, channel_url: str) -> bool:
        """Додати канал для моніторингу"""
        try:
            # Парсимо URL Discord каналу
            # Формат: https://discord.com/channels/server_id/channel_id
            match = re.search(r'discord\.com/channels/(\d+)/(\d+)', channel_url)
            if not match:
                self.logger.error(f"Неправильний формат URL Discord: {channel_url}")
                return False
                
            server_id, channel_id = match.groups()
            self.monitoring_channels.add(channel_id)
            self.logger.info(f"Додано канал для моніторингу: {channel_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка додавання каналу: {e}")
            return False
            
    def remove_channel(self, channel_id: str) -> None:
        """Видалити канал з моніторингу"""
        self.monitoring_channels.discard(channel_id)
        self.last_message_ids.pop(channel_id, None)
        self.logger.info(f"Видалено канал з моніторингу: {channel_id}")
        
    async def get_channel_messages(self, channel_id: str, limit: int = 5) -> List[Dict]:
        """Отримати повідомлення з каналу (безпечно)"""
        if not self.session:
            return []
            
        try:
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}"
            async with self.session.get(url) as response:
                # Перевіряємо rate limit
                if response.status == 429:
                    retry_after = float(response.headers.get('Retry-After', 1))
                    self.logger.warning(f"Rate limited, чекаємо {retry_after} секунд")
                    await asyncio.sleep(retry_after)
                    return await self.get_channel_messages(channel_id, limit)
                
                if response.status == 200:
                    messages = await response.json()
                    return messages
                elif response.status == 401:
                    self.logger.error("Unauthorized: неправильний authorization токен")
                elif response.status == 403:
                    self.logger.error("Forbidden: немає доступу до каналу")
                else:
                    self.logger.error(f"Помилка отримання повідомлень: {response.status}")
                return []
                
        except Exception as e:
            self.logger.error(f"Помилка запиту до Discord API: {e}")
            return []
            
    async def check_new_messages(self) -> List[Dict]:
        """Перевірити нові повідомлення у всіх каналах (виправлено)"""
        new_messages = []
        
        for i, channel_id in enumerate(self.monitoring_channels):
            try:
                # Додаємо затримку між запитами до різних каналів
                if i > 0:
                    await asyncio.sleep(1)  # 1 секунда між каналами
                
                # Отримуємо повідомлення
                messages = await self.get_channel_messages(channel_id, limit=5)
                if not messages:
                    continue
                    
                # Знаходимо нові повідомлення
                last_id = self.last_message_ids.get(channel_id)
                
                # Якщо це перша перевірка - зберігаємо останнє повідомлення як базове
                if last_id is None:
                    self.last_message_ids[channel_id] = messages[0]['id']
                    continue
                
                # Шукаємо нові повідомлення (від найновіших до найстаріших)
                found_new = False
                for message in messages:
                    message_id = message['id']
                    
                    # Якщо знайшли останнє відоме повідомлення - зупиняємося
                    if message_id == last_id:
                        break
                        
                    # Це нове повідомлення
                    found_new = True
                    new_messages.append({
                        'channel_id': channel_id,
                        'message_id': message_id,
                        'content': message.get('content', ''),
                        'author': message.get('author', {}).get('username', 'Unknown'),
                        'timestamp': message.get('timestamp', ''),
                        'url': f"https://discord.com/channels/{message.get('guild_id', '')}/{channel_id}/{message_id}"
                    })
                
                # Діагностичне логування
                if found_new:
                    self.logger.info(f"Канал {channel_id}: знайдено нові повідомлення, останнє відоме: {last_id}")
                    
                # Оновлюємо останнє повідомлення на найновіше
                if messages:
                    self.last_message_ids[channel_id] = messages[0]['id']
                    
            except Exception as e:
                self.logger.error(f"Помилка перевірки каналу {channel_id}: {e}")
                
        return new_messages
        
    async def start_monitoring(self, callback_func, interval: int = 15):
        """Запустити моніторинг з callback функцією (безпечно)"""
        while True:
            try:
                new_messages = await self.check_new_messages()
                
                if new_messages:
                    # Логуємо для діагностики
                    self.logger.info(f"Знайдено {len(new_messages)} нових повідомлень")
                    if asyncio.iscoroutinefunction(callback_func):
                        await callback_func(new_messages)
                    else:
                        callback_func(new_messages)
                    
                # Додаємо випадкову затримку для уникнення підозрілої активності
                import random
                random_delay = random.uniform(0.5, 2.0)
                await asyncio.sleep(interval + random_delay)
                
            except Exception as e:
                self.logger.error(f"Помилка в циклі моніторингу: {e}")
                # При помилці чекаємо довше
                await asyncio.sleep(interval * 2)
                
    def get_monitoring_status(self) -> Dict:
        """Отримати статус моніторингу"""
        return {
            'channels_count': len(self.monitoring_channels),
            'channels': list(self.monitoring_channels),
            'last_checks': dict(self.last_message_ids)
        }
        
    def format_message_notification(self, message: Dict) -> str:
        """Форматувати повідомлення для сповіщення"""
        content = message['content'][:200] + "..." if len(message['content']) > 200 else message['content']
        
        # Екрануємо спеціальні символи для Markdown
        content = content.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`').replace('[', '\\[')
        author = message['author'].replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
        
        return (
            f"💬 *Нове повідомлення в Discord*\n\n"
            f"👤 Автор: {author}\n"
            f"📝 Текст: {content}\n"
            f"🔗 [Перейти до повідомлення]({message['url']})"
        )