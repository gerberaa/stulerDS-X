import logging
import asyncio
import threading
from datetime import datetime
from typing import List, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, JobQueue
from security_manager import SecurityManager
from project_manager import ProjectManager
from discord_monitor import DiscordMonitor
from twitter_monitor import TwitterMonitor
from selenium_twitter_monitor import SeleniumTwitterMonitor
from config import BOT_TOKEN, ADMIN_PASSWORD, SECURITY_TIMEOUT, MESSAGES, DISCORD_AUTHORIZATION, MONITORING_INTERVAL, TWITTER_AUTH_TOKEN, TWITTER_CSRF_TOKEN, TWITTER_MONITORING_INTERVAL

# Налаштування логування - тільки критичні помилки для швидкості
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger(__name__)

# Ініціалізація менеджерів
security_manager = SecurityManager(SECURITY_TIMEOUT)
project_manager = ProjectManager()
discord_monitor = DiscordMonitor(DISCORD_AUTHORIZATION) if DISCORD_AUTHORIZATION else None
twitter_monitor = TwitterMonitor(TWITTER_AUTH_TOKEN, TWITTER_CSRF_TOKEN) if TWITTER_AUTH_TOKEN else None
selenium_twitter_monitor = None  # Ініціалізується при потребі

# Словник для зберігання стану користувачів (очікують пароль)
waiting_for_password = {}

# Словник для зберігання стану додавання проектів
user_states = {}  # user_id -> {'state': 'adding_project', 'data': {...}}

# Глобальна змінна для зберігання активного бота
bot_instance = None

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Створити головне меню"""
    keyboard = [
        [InlineKeyboardButton("➕ Додати проект", callback_data="add_project")],
        [InlineKeyboardButton("📋 Мої проекти", callback_data="my_projects")],
        [InlineKeyboardButton("🔧 Менеджер акаунтів", callback_data="account_manager")],
        [InlineKeyboardButton("📜 Історія Discord", callback_data="discord_history")],
        [InlineKeyboardButton("🐦 Selenium Twitter", callback_data="selenium_twitter")],
        [InlineKeyboardButton("📢 Пересилання", callback_data="forward_settings")],
        [InlineKeyboardButton("🔧 Діагностика", callback_data="diagnostics")],
        [InlineKeyboardButton("⚙️ Налаштування", callback_data="settings")],
        [InlineKeyboardButton("❓ Допомога", callback_data="help")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_platform_keyboard() -> InlineKeyboardMarkup:
    """Створити клавіатуру вибору платформи"""
    keyboard = [
        [InlineKeyboardButton("🐦 Twitter/X", callback_data="platform_twitter")],
        [InlineKeyboardButton("💬 Discord", callback_data="platform_discord")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_history_count_keyboard() -> InlineKeyboardMarkup:
    """Створити клавіатуру вибору кількості повідомлень"""
    keyboard = [
        [InlineKeyboardButton("📄 Останні 5", callback_data="history_5")],
        [InlineKeyboardButton("📄 Останні 10", callback_data="history_10")],
        [InlineKeyboardButton("📄 Останні 20", callback_data="history_20")],
        [InlineKeyboardButton("📄 Останні 50", callback_data="history_50")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_discord_channels_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Створити клавіатуру з Discord каналами користувача"""
    projects = project_manager.get_user_projects(user_id)
    discord_projects = [p for p in projects if p['platform'] == 'discord']
    
    keyboard = []
    for project in discord_projects:
        keyboard.append([InlineKeyboardButton(
            f"💬 {project['name']}", 
            callback_data=f"channel_{project['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def get_forward_settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Створити клавіатуру налаштувань пересилання"""
    forward_status = project_manager.get_forward_status(user_id)
    
    keyboard = []
    
    if forward_status['enabled']:
        keyboard.append([InlineKeyboardButton("🔴 Вимкнути пересилання", callback_data="disable_forward")])
        keyboard.append([InlineKeyboardButton("✏️ Змінити канал", callback_data="change_channel")])
    else:
        keyboard.append([InlineKeyboardButton("🟢 Увімкнути пересилання", callback_data="enable_forward")])
        keyboard.append([InlineKeyboardButton("📝 Встановити канал", callback_data="set_channel")])
    
    keyboard.append([InlineKeyboardButton("🤖 Автоналаштування", callback_data="auto_setup")])
    keyboard.append([InlineKeyboardButton("📊 Статус", callback_data="forward_status")])
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")])
    
    return InlineKeyboardMarkup(keyboard)

def get_diagnostics_keyboard() -> InlineKeyboardMarkup:
    """Створити клавіатуру діагностики"""
    keyboard = [
        [InlineKeyboardButton("🔍 Перевірити бота", callback_data="check_bot_status")],
        [InlineKeyboardButton("📺 Тест каналів", callback_data="test_channels")],
        [InlineKeyboardButton("🔗 Discord API", callback_data="test_discord_api")],
        [InlineKeyboardButton("📊 Статистика", callback_data="show_stats")],
        [InlineKeyboardButton("🔄 Перезавантажити", callback_data="reload_data")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def escape_markdown(text: str) -> str:
    """Екранувати спеціальні символи для Markdown"""
    if not text:
        return ""
    return str(text).replace('*', '\\*').replace('_', '\\_').replace('`', '\\`').replace('[', '\\[').replace(']', '\\]')

def extract_twitter_username(url: str) -> str:
    """Витягти username з Twitter URL"""
    try:
        # Підтримуємо різні формати URL
        if 'twitter.com' in url or 'x.com' in url:
            # Видаляємо протокол
            url = url.replace('https://', '').replace('http://', '')
            
            # Видаляємо www
            if url.startswith('www.'):
                url = url[4:]
                
            # Витягуємо username
            if url.startswith('twitter.com/'):
                username = url.split('/')[1]
            elif url.startswith('x.com/'):
                username = url.split('/')[1]
            else:
                return None
                
            # Очищаємо від зайвих символів
            username = username.split('?')[0].split('#')[0]
            
            return username if username else None
            
        return None
    except Exception as e:
        logger.error(f"Помилка витягування Twitter username: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник команди /start"""
    user_id = update.effective_user.id
    
    if security_manager.is_user_authorized(user_id):
        welcome_text = (
            f"Привіт {update.effective_user.first_name}! 👋\n\n"
            f"🔐 Час до закінчення сесії: {security_manager.get_session_time_left(user_id)} секунд\n\n"
            f"Оберіть дію з меню нижче:"
        )
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        waiting_for_password[user_id] = True
        await update.message.reply_text(MESSAGES['password_request'])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник повідомлень"""
    # Перевіряємо чи це повідомлення від користувача (не від каналу)
    if not update.effective_user:
        return
    
    # Перевіряємо чи це не канал
    if update.message.chat.type in ['channel', 'supergroup']:
        # Якщо це канал, перевіряємо чи бота пінгнули
        if update.message.text and '@' in update.message.text:
            # Шукаємо username бота в тексті
            bot_username = context.bot.username
            if bot_username and f'@{bot_username}' in update.message.text:
                # Бота пінгнули в каналі - автоматично встановлюємо канал для пересилання
                await handle_channel_ping(update, context)
        return
        
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Якщо користувач очікує введення пароля
    if user_id in waiting_for_password:
        if message_text == ADMIN_PASSWORD:
            security_manager.authorize_user(user_id)
            del waiting_for_password[user_id]
            welcome_text = (
                f"{MESSAGES['password_correct']}\n\n"
                f"Оберіть дію з меню нижче:"
            )
            await update.message.reply_text(
                welcome_text,
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await update.message.reply_text(MESSAGES['password_incorrect'])
        return
    
    # Перевіряємо авторизацію для інших повідомлень
    if not security_manager.is_user_authorized(user_id):
        waiting_for_password[user_id] = True
        await update.message.reply_text(MESSAGES['session_expired'])
        return
    
    # Оновлюємо активність користувача
    security_manager.update_user_activity(user_id)
    
    # Обробляємо стан додавання проекту
    if user_id in user_states:
        if user_states[user_id]['state'] == 'adding_project':
            await handle_project_creation(update, context)
        elif user_states[user_id]['state'] == 'setting_forward_channel':
            await handle_forward_channel_setting(update, context)
        return
    
    # Обробляємо команди
    if message_text.startswith('/'):
        await handle_command(update, context, message_text)
    else:
        await update.message.reply_text(
            f"Ви написали: {message_text}\n"
            f"Час до закінчення сесії: {security_manager.get_session_time_left(user_id)} секунд\n\n"
            f"Використайте меню для навігації:",
            reply_markup=get_main_menu_keyboard()
        )

async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> None:
    """Обробник команд"""
    user_id = update.effective_user.id
    
    if command == '/status':
        time_left = security_manager.get_session_time_left(user_id)
        await update.message.reply_text(
            f"Статус сесії:\n"
            f"Авторизований: {'Так' if security_manager.is_user_authorized(user_id) else 'Ні'}\n"
            f"Час до закінчення: {time_left} секунд"
        )
    elif command == '/logout':
        security_manager.deauthorize_user(user_id)
        await update.message.reply_text("Ви вийшли з системи.")
    elif command == '/help':
        await update.message.reply_text(
            "Доступні команди:\n"
            "/start - Почати роботу з ботом\n"
            "/status - Перевірити статус сесії\n"
            "/logout - Вийти з системи\n"
            "/help - Показати цю довідку"
        )
    else:
        await update.message.reply_text("Невідома команда. Використайте /help для довідки.")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник callback запитів"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Перевіряємо авторизацію
    if not security_manager.is_user_authorized(user_id):
        await query.edit_message_text(MESSAGES['session_expired'])
        return
    
    # Оновлюємо активність користувача
    security_manager.update_user_activity(user_id)
    
    # Додаємо/оновлюємо користувача в базі даних
    if not project_manager.get_user_data(user_id):
        project_manager.add_user(user_id, {
            'first_name': update.effective_user.first_name,
            'username': update.effective_user.username
        })
    else:
        project_manager.update_user_last_seen(user_id)
    
    callback_data = query.data
    
    if callback_data == "main_menu":
        await query.edit_message_text(
            "🏠 Головне меню\n\nОберіть дію:",
            reply_markup=get_main_menu_keyboard()
        )
    elif callback_data == "add_project":
        await query.edit_message_text(
            "➕ Додавання нового проекту\n\nОберіть платформу для моніторингу:",
            reply_markup=get_platform_keyboard()
        )
    elif callback_data == "my_projects":
        projects_text = project_manager.format_projects_list(user_id)
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]]
        await query.edit_message_text(
            projects_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif callback_data == "platform_twitter":
        user_states[user_id] = {
            'state': 'adding_project',
            'data': {'platform': 'twitter'}
        }
        await query.edit_message_text(
            "🐦 Додавання проекту Twitter/X\n\nВведіть назву проекту:"
        )
    elif callback_data == "platform_discord":
        user_states[user_id] = {
            'state': 'adding_project',
            'data': {'platform': 'discord'}
        }
        await query.edit_message_text(
            "💬 Додавання проекту Discord\n\nВведіть назву проекту:"
        )
    elif callback_data == "help":
        help_text = (
            "❓ Допомога\n\n"
            "📋 Доступні функції:\n"
            "• Додавання проектів для моніторингу\n"
            "• Підтримка Twitter/X та Discord\n"
            "• Перегляд ваших проектів\n"
            "• Автоматична безпека з паролем\n\n"
            "🔐 Безпека:\n"
            "• Сесія закінчується через 5 хвилин неактивності\n"
            "• Для продовження потрібно ввести пароль\n\n"
            "📝 Формат посилань:\n"
            "• Twitter: https://twitter.com/username\n"
            "• Discord: https://discord.com/channels/server_id/channel_id"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]]
        await query.edit_message_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif callback_data == "selenium_twitter":
        selenium_text = (
            "🐦 **Selenium Twitter Моніторинг**\n\n"
            "🔧 **Доступні команди:**\n"
            "• `/selenium_auth` - Авторизація в Twitter\n"
            "• `/selenium_add username` - Додати акаунт\n"
            "• `/selenium_test username` - Тестувати моніторинг\n"
            "• `/selenium_start` - Запустити моніторинг\n"
            "• `/selenium_stop` - Зупинити моніторинг\n\n"
            "📝 **Приклад використання:**\n"
            "1. `/selenium_auth` - увійдіть в Twitter\n"
            "2. `/selenium_add pilk_xz` - додайте акаунт\n"
            "3. `/selenium_test pilk_xz` - протестуйте\n"
            "4. `/selenium_start` - запустіть моніторинг\n\n"
            "💡 **Переваги Selenium:**\n"
            "• Реальний браузер\n"
            "• Авторизований доступ\n"
            "• Надійний парсинг\n"
            "• Обхід обмежень API"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]]
        await query.edit_message_text(
            selenium_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    elif callback_data == "account_manager":
        # Показуємо менеджер акаунтів
        projects = project_manager.get_user_projects(user_id)
        
        if not projects:
            await query.edit_message_text(
                "🔧 **Менеджер акаунтів**\n\n❌ У вас немає проектів для моніторингу.\n\nДодайте проекти через меню бота.",
                reply_markup=get_main_menu_keyboard()
            )
            return
        
        # Групуємо по платформах
        twitter_projects = [p for p in projects if p['platform'] == 'twitter']
        discord_projects = [p for p in projects if p['platform'] == 'discord']
        
        # Форматуємо список
        text = "🔧 **Менеджер акаунтів**\n\n"
        
        if twitter_projects:
            text += "🐦 **Twitter/X акаунти:**\n"
            for i, project in enumerate(twitter_projects, 1):
                username = extract_twitter_username(project['url'])
                text += f"{i}. @{username} ({project['name']})\n"
            text += "\n"
        
        if discord_projects:
            text += "💬 **Discord канали:**\n"
            for i, project in enumerate(discord_projects, 1):
                channel_id = extract_discord_channel_id(project['url'])
                text += f"{i}. Канал {channel_id} ({project['name']})\n"
            text += "\n"
        
        # Додаємо команди для видалення
        text += "🔧 **Команди для управління:**\n"
        text += "• /remove_twitter username - видалити Twitter акаунт\n"
        text += "• /remove_discord channel_id - видалити Discord канал\n"
        text += "• /accounts - показати список акаунтів"
        
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    elif callback_data == "discord_history":
        # Перевіряємо чи є Discord проекти
        projects = project_manager.get_user_projects(user_id)
        discord_projects = [p for p in projects if p['platform'] == 'discord']
        
        if not discord_projects:
            await query.edit_message_text(
                "📜 Історія Discord\n\n❌ У вас немає Discord проектів для перегляду історії.\n\nДодайте Discord проект спочатку.",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await query.edit_message_text(
                "📜 Історія Discord\n\nОберіть канал для перегляду історії повідомлень:",
                reply_markup=get_discord_channels_keyboard(user_id)
            )
    elif callback_data.startswith("channel_"):
        # Зберігаємо вибраний канал для історії
        project_id = int(callback_data.split("_")[1])
        project = project_manager.get_project_by_id(user_id, project_id)
        
        if project:
            user_states[user_id] = {
                'state': 'viewing_history',
                'data': {'project': project}
            }
            await query.edit_message_text(
                f"📜 Історія каналу: {project['name']}\n\nОберіть кількість повідомлень для перегляду:",
                reply_markup=get_history_count_keyboard()
            )
    elif callback_data.startswith("history_"):
        # Отримуємо історію повідомлень
        count = int(callback_data.split("_")[1])
        await handle_discord_history(update, context, count)
    elif callback_data == "settings":
        stats = project_manager.get_statistics()
        user_projects = project_manager.get_user_projects(user_id)
        
        settings_text = (
            "⚙️ Налаштування\n\n"
            f"🔐 Час до закінчення сесії: {security_manager.get_session_time_left(user_id)} секунд\n"
            f"📊 Ваші проекти: {len(user_projects)}\n"
            f"👥 Всього користувачів: {stats['total_users']}\n"
            f"📋 Всього проектів: {stats['total_projects']}\n"
            f"💬 Discord проектів: {stats['discord_projects']}\n"
            f"🐦 Twitter проектів: {stats['twitter_projects']}\n"
            f"📁 Розмір файлу даних: {stats['data_file_size']} байт\n"
            f"🕒 Останнє оновлення: {stats['last_updated'][:19]}\n\n"
            "Доступні налаштування:\n"
            "• Зміна пароля\n"
            "• Налаштування часу сесії\n"
            "• Експорт даних"
        )
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="main_menu")]]
        await query.edit_message_text(
            settings_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif callback_data == "forward_settings":
        forward_status = project_manager.get_forward_status(user_id)
        
        if forward_status['enabled']:
            status_text = f"📢 Налаштування пересилання\n\n✅ Пересилання увімкнено\n📺 Канал: {forward_status['channel_id']}\n🕒 Налаштовано: {forward_status['created_at'][:19] if forward_status['created_at'] else 'Невідомо'}\n\n💡 Сповіщення відправляються тільки в налаштований канал, не в особисті повідомлення."
        else:
            status_text = "📢 Налаштування пересилання\n\n❌ Пересилання вимкнено\n\nНалаштуйте канал для автоматичного пересилання сповіщень з ваших проектів.\n\n💡 Сповіщення будуть відправлятися тільки в налаштований канал."
        
        await query.edit_message_text(
            status_text,
            reply_markup=get_forward_settings_keyboard(user_id)
        )
    elif callback_data == "enable_forward":
        if project_manager.enable_forward(user_id):
            await query.edit_message_text(
                "✅ Пересилання увімкнено!\n\nТепер потрібно встановити канал для пересилання.",
                reply_markup=get_forward_settings_keyboard(user_id)
            )
        else:
            await query.edit_message_text(
                "❌ Помилка увімкнення пересилання",
                reply_markup=get_forward_settings_keyboard(user_id)
            )
    elif callback_data == "disable_forward":
        if project_manager.disable_forward(user_id):
            await query.edit_message_text(
                "🔴 Пересилання вимкнено",
                reply_markup=get_forward_settings_keyboard(user_id)
            )
        else:
            await query.edit_message_text(
                "❌ Помилка вимкнення пересилання",
                reply_markup=get_forward_settings_keyboard(user_id)
            )
    elif callback_data in ["set_channel", "change_channel"]:
        user_states[user_id] = {
            'state': 'setting_forward_channel',
            'data': {}
        }
        await query.edit_message_text(
            "📝 Встановлення каналу для пересилання\n\n"
            "**Спосіб 1 - Автоматичне налаштування:**\n"
            "1. Додайте бота в канал як адміністратора\n"
            "2. Пінгніть бота в каналі: @bot_username\n"
            "3. Бот автоматично налаштує канал\n\n"
            "**Спосіб 2 - Ручне налаштування:**\n"
            "Введіть ID каналу або username каналу:\n\n"
            "Приклади:\n"
            "• @channel_username\n"
            "• -1001234567890 (ID каналу)\n"
            "• channel_username (без @)\n\n"
            "💡 Рекомендуємо використовувати автоматичне налаштування!"
        )
    elif callback_data == "auto_setup":
        bot_username = context.bot.username
        await query.edit_message_text(
            f"🤖 **Автоматичне налаштування каналу**\n\n"
            f"Для автоматичного налаштування каналу:\n\n"
            f"1️⃣ **Додайте бота в канал**\n"
            f"   • Додайте @{bot_username} в канал як адміністратора\n"
            f"   • Надайте права на відправку повідомлень\n\n"
            f"2️⃣ **Пінгніть бота в каналі**\n"
            f"   • Напишіть в каналі: @{bot_username}\n"
            f"   • Бот автоматично налаштує канал\n\n"
            f"3️⃣ **Готово!**\n"
            f"   • Канал буде налаштовано для пересилання\n"
            f"   • Ви отримаєте підтвердження\n\n"
            f"💡 **Переваги:**\n"
            f"• Не потрібно знати ID каналу\n"
            f"• Автоматичне налаштування\n"
            f"• Миттєве підтвердження",
            reply_markup=get_forward_settings_keyboard(user_id)
        )
    elif callback_data == "forward_status":
        forward_status = project_manager.get_forward_status(user_id)
        user_projects = project_manager.get_user_projects(user_id)
        discord_projects = [p for p in user_projects if p['platform'] == 'discord']
        
        status_text = (
            f"📊 Статус пересилання\n\n"
            f"🔄 Статус: {'✅ Увімкнено' if forward_status['enabled'] else '❌ Вимкнено'}\n"
            f"📺 Канал: {forward_status['channel_id'] or 'Не встановлено'}\n"
            f"📋 Discord проектів: {len(discord_projects)}\n"
            f"🕒 Налаштовано: {forward_status['created_at'][:19] if forward_status['created_at'] else 'Невідомо'}\n\n"
            f"💡 Сповіщення відправляються тільки в налаштований канал, не в особисті повідомлення.\n\n"
        )
        
        if forward_status['enabled'] and discord_projects:
            status_text += "📢 Сповіщення будуть пересилатися з:\n"
            for project in discord_projects:
                status_text += f"• {project['name']}\n"
        elif not discord_projects:
            status_text += "⚠️ У вас немає Discord проектів для моніторингу."
        
        await query.edit_message_text(
            status_text,
            reply_markup=get_forward_settings_keyboard(user_id)
        )
    elif callback_data == "diagnostics":
        diagnostics_text = (
            "🔧 **Діагностика системи**\n\n"
            "Оберіть тип перевірки:\n\n"
            "🔍 **Перевірити бота** - статус бота та підключення\n"
            "📺 **Тест каналів** - перевірка доступу до каналів\n"
            "🔗 **Discord API** - тест підключення до Discord\n"
            "📊 **Статистика** - детальна статистика системи\n"
            "🔄 **Перезавантажити** - оновити дані"
        )
        await query.edit_message_text(
            diagnostics_text,
            reply_markup=get_diagnostics_keyboard()
        )
    elif callback_data == "check_bot_status":
        try:
            # Перевіряємо статус бота
            bot_info = await context.bot.get_me()
            bot_status = "✅ Активний"
            
            # Перевіряємо кількість авторизованих користувачів
            auth_users = len(security_manager.authorized_users)
            
            # Перевіряємо Discord моніторинг
            discord_status = "✅ Активний" if discord_monitor else "❌ Вимкнено"
            
            status_text = (
                f"🔍 **Статус бота**\n\n"
                f"🤖 Бот: {bot_status}\n"
                f"📛 Ім'я: {bot_info.first_name}\n"
                f"🆔 ID: {bot_info.id}\n"
                f"👤 Username: @{bot_info.username}\n\n"
                f"👥 Авторизованих користувачів: {auth_users}\n"
                f"🔗 Discord моніторинг: {discord_status}\n"
                f"📊 Проектів: {len(project_manager.get_user_projects(user_id))}\n"
                f"🕒 Час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            await query.edit_message_text(
                status_text,
                reply_markup=get_diagnostics_keyboard()
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ **Помилка перевірки бота**\n\n{str(e)}",
                reply_markup=get_diagnostics_keyboard()
            )
    elif callback_data == "test_channels":
        try:
            forward_channel = project_manager.get_forward_channel(user_id)
            
            if forward_channel:
                # Спробуємо відправити тестове повідомлення
                test_message = (
                    f"🧪 **Тестове повідомлення**\n\n"
                    f"📺 Канал: {forward_channel}\n"
                    f"👤 Від: {update.effective_user.first_name}\n"
                    f"🕒 Час: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    f"✅ Якщо ви бачите це повідомлення, канал працює!"
                )
                
                await context.bot.send_message(
                    chat_id=forward_channel,
                    text=test_message,
                    parse_mode='Markdown'
                )
                
                result_text = f"✅ **Тест каналу пройшов успішно!**\n\n📺 Канал: `{forward_channel}`\n📤 Тестове повідомлення відправлено"
            else:
                result_text = "❌ **Канал не налаштовано**\n\nСпочатку встановіть канал для пересилання в налаштуваннях."
            
            await query.edit_message_text(
                result_text,
                reply_markup=get_diagnostics_keyboard()
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ **Помилка тесту каналу**\n\n{str(e)}\n\n💡 Перевірте:\n• Чи додано бота в канал\n• Чи є у бота права адміністратора\n• Чи правильний ID каналу",
                reply_markup=get_diagnostics_keyboard()
            )
    elif callback_data == "test_discord_api":
        try:
            if not DISCORD_AUTHORIZATION:
                await query.edit_message_text(
                    "❌ **Discord API не налаштовано**\n\nВстановіть AUTHORIZATION токен в .env файлі",
                    reply_markup=get_diagnostics_keyboard()
                )
                return
            
            # Тестуємо Discord API
            import aiohttp
            headers = {
                'Authorization': DISCORD_AUTHORIZATION,
                'User-Agent': 'DiscordBot (https://github.com/discord/discord-api-docs, 1.0)'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get('https://discord.com/api/v10/users/@me', headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        result_text = (
                            f"✅ **Discord API працює**\n\n"
                            f"👤 Користувач: {user_data.get('username', 'Невідомо')}\n"
                            f"🆔 ID: {user_data.get('id', 'Невідомо')}\n"
                            f"📧 Email: {user_data.get('email', 'Приховано')}\n"
                            f"🔐 Верифікований: {'✅' if user_data.get('verified', False) else '❌'}\n"
                            f"📊 Статус: {response.status}"
                        )
                    else:
                        result_text = f"❌ **Discord API помилка**\n\nСтатус: {response.status}\nВідповідь: {await response.text()}"
            
            await query.edit_message_text(
                result_text,
                reply_markup=get_diagnostics_keyboard()
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ **Помилка Discord API**\n\n{str(e)}",
                reply_markup=get_diagnostics_keyboard()
            )
    elif callback_data == "show_stats":
        try:
            stats = project_manager.get_statistics()
            user_projects = project_manager.get_user_projects(user_id)
            discord_projects = [p for p in user_projects if p['platform'] == 'discord']
            forward_status = project_manager.get_forward_status(user_id)
            
            # Підраховуємо відстежені повідомлення
            sent_messages = project_manager.data['settings'].get('sent_messages', {})
            total_tracked = sum(
                len(channel_messages) 
                for user_messages in sent_messages.values() 
                for channel_messages in user_messages.values()
            )
            
            stats_text = (
                f"📊 **Статистика системи**\n\n"
                f"👥 Всього користувачів: {stats['total_users']}\n"
                f"📋 Всього проектів: {stats['total_projects']}\n"
                f"🔗 Discord проектів: {len(discord_projects)}\n"
                f"🐦 Twitter проектів: {len([p for p in user_projects if p['platform'] == 'twitter'])}\n\n"
                f"📢 **Пересилання:**\n"
                f"🔄 Статус: {'✅ Увімкнено' if forward_status['enabled'] else '❌ Вимкнено'}\n"
                f"📺 Канал: {forward_status['channel_id'] or 'Не встановлено'}\n\n"
                f"💾 **Дані:**\n"
                f"📁 Розмір файлу: {stats.get('data_size', 'Невідомо')}\n"
                f"📨 Відстежених повідомлень: {total_tracked}\n"
                f"🕒 Останнє оновлення: {stats.get('last_update', 'Невідомо')}"
            )
            
            await query.edit_message_text(
                stats_text,
                reply_markup=get_diagnostics_keyboard()
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ **Помилка отримання статистики**\n\n{str(e)}",
                reply_markup=get_diagnostics_keyboard()
            )
    elif callback_data == "reload_data":
        try:
            # Перезавантажуємо дані
            project_manager.load_data()
            
            # Перезапускаємо Discord моніторинг
            if discord_monitor:
                discord_monitor.channels.clear()
                for user_id_str, projects in project_manager.data['projects'].items():
                    for project in projects:
                        if project['platform'] == 'discord':
                            channel_id = project['link'].split('/')[-1]
                            discord_monitor.add_channel(channel_id)
            
            await query.edit_message_text(
                "🔄 **Дані перезавантажено**\n\n✅ Проекти оновлено\n✅ Discord канали оновлено\n✅ Налаштування оновлено",
                reply_markup=get_diagnostics_keyboard()
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ **Помилка перезавантаження**\n\n{str(e)}",
                reply_markup=get_diagnostics_keyboard()
            )

async def handle_project_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник створення проекту"""
    user_id = update.effective_user.id
    message_text = update.message.text
    state_data = user_states[user_id]['data']
    
    if 'name' not in state_data:
        # Зберігаємо назву проекту
        state_data['name'] = message_text
        platform = state_data['platform']
        
        if platform == 'twitter':
            await update.message.reply_text(
                f"✅ Назва проекту: {message_text}\n\n"
                f"🐦 Тепер введіть посилання на Twitter/X сторінку:\n"
                f"Приклад: https://twitter.com/username"
            )
        else:  # discord
            await update.message.reply_text(
                f"✅ Назва проекту: {message_text}\n\n"
                f"💬 Тепер введіть посилання на Discord канал:\n"
                f"Приклад: https://discord.com/channels/1408570777275469866/1413243132467871839"
            )
    else:
        # Зберігаємо посилання та завершуємо створення
        state_data['url'] = message_text
        
        # Додаємо проект
        if project_manager.add_project(user_id, state_data):
            # Додаємо до відповідного моніторингу
            if state_data['platform'] == 'discord' and discord_monitor:
                try:
                    discord_monitor.add_channel(state_data['url'])
                    logger.info(f"Додано Discord канал до моніторингу: {state_data['url']}")
                except Exception as e:
                    logger.error(f"Помилка додавання Discord каналу до моніторингу: {e}")
            elif state_data['platform'] == 'twitter' and twitter_monitor:
                try:
                    # Витягуємо username з URL
                    username = extract_twitter_username(state_data['url'])
                    if username:
                        twitter_monitor.add_account(username)
                        logger.info(f"Додано Twitter акаунт до моніторингу: {username}")
                except Exception as e:
                    logger.error(f"Помилка додавання Twitter акаунта до моніторингу: {e}")
                    
            success_text = (
                f"🎉 Проект успішно додано!\n\n"
                f"📝 Назва: {state_data['name']}\n"
                f"🌐 Платформа: {state_data['platform'].title()}\n"
                f"🔗 Посилання: {state_data['url']}\n\n"
                f"Проект додано до списку моніторингу."
            )
            await update.message.reply_text(
                success_text,
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Помилка при додаванні проекту. Спробуйте ще раз.",
                reply_markup=get_main_menu_keyboard()
            )
        
        # Очищуємо стан користувача
        del user_states[user_id]

async def handle_forward_channel_setting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник встановлення каналу для пересилання"""
    user_id = update.effective_user.id
    message_text = update.message.text.strip()
    
    # Очищаємо @ якщо є
    if message_text.startswith('@'):
        message_text = message_text[1:]
    
    # Валідація каналу
    if not message_text:
        await update.message.reply_text("❌ Введіть правильний ID або username каналу.")
        return
    
    # Спробуємо встановити канал
    if project_manager.set_forward_channel(user_id, message_text):
        success_text = (
            f"✅ Канал для пересилання встановлено!\n\n"
            f"📺 Канал: {message_text}\n"
            f"🔄 Статус: Увімкнено\n\n"
            f"Тепер всі нові повідомлення з ваших Discord проектів будуть автоматично пересилатися в цей канал."
        )
        await update.message.reply_text(
            success_text,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Помилка встановлення каналу. Спробуйте ще раз.",
            reply_markup=get_main_menu_keyboard()
        )
    
    # Очищуємо стан користувача
    if user_id in user_states:
        del user_states[user_id]

async def handle_channel_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник пінгу бота в каналі"""
    try:
        # Отримуємо інформацію про канал
        channel_id = update.message.chat.id
        channel_title = update.message.chat.title or "Unknown Channel"
        
        # Отримуємо інформацію про користувача, який пінгнув
        if update.message.from_user:
            user_id = update.message.from_user.id
            username = update.message.from_user.username or update.message.from_user.first_name
            
            # Перевіряємо чи користувач авторизований
            if not security_manager.is_user_authorized(user_id):
                # Відправляємо повідомлення в особисті повідомлення
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"🔒 Ви не авторизовані для налаштування пересилання.\n\nСпочатку авторизуйтесь в боті: @{context.bot.username}"
                    )
                except:
                    pass  # Якщо не можемо відправити в особисті повідомлення
                return
            
            # Встановлюємо канал для пересилання
            if project_manager.set_forward_channel(user_id, str(channel_id)):
                # Відправляємо підтвердження в канал
                safe_channel_title = escape_markdown(channel_title)
                safe_username = escape_markdown(username)
                
                confirmation_text = (
                    f"✅ **Канал налаштовано для пересилання!**\n\n"
                    f"📺 Канал: {safe_channel_title}\n"
                    f"👤 Налаштовано: @{safe_username}\n"
                    f"🔄 Статус: Увімкнено\n\n"
                    f"Тепер всі нові повідомлення з Discord проектів будуть автоматично пересилатися в цей канал."
                )
                
                await context.bot.send_message(
                    chat_id=channel_id,
                    text=confirmation_text,
                    parse_mode='Markdown'
                )
                
                # Відправляємо повідомлення в особисті повідомлення
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"✅ Канал '{channel_title}' успішно налаштовано для пересилання сповіщень!"
                    )
                except:
                    pass
                    
                logger.info(f"Канал {channel_id} ({channel_title}) налаштовано для користувача {user_id}")
            else:
                # Відправляємо повідомлення про помилку в особисті повідомлення
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"❌ Помилка налаштування каналу '{channel_title}'. Спробуйте ще раз."
                    )
                except:
                    pass
        else:
            # Якщо не можемо визначити користувача
            await context.bot.send_message(
                chat_id=channel_id,
                text="❌ Не вдалося визначити користувача для налаштування пересилання."
            )
            
    except Exception as e:
        logger.error(f"Помилка обробки пінгу в каналі: {e}")
        try:
            await context.bot.send_message(
                chat_id=update.message.chat.id,
                text="❌ Помилка налаштування пересилання. Спробуйте ще раз."
            )
        except:
            pass

async def handle_discord_history(update: Update, context: ContextTypes.DEFAULT_TYPE, count: int) -> None:
    """Обробник перегляду історії Discord"""
    query = update.callback_query
    user_id = update.effective_user.id
    
    if user_id not in user_states or user_states[user_id]['state'] != 'viewing_history':
        await query.edit_message_text("❌ Помилка: стан сесії втрачено.", reply_markup=get_main_menu_keyboard())
        return
    
    project = user_states[user_id]['data']['project']
    
    # Показуємо завантаження
    await query.edit_message_text(f"📥 Завантаження останніх {count} повідомлень з каналу {project['name']}...")
    
    try:
        # Отримуємо повідомлення з Discord
        messages = await get_discord_messages_history(project['url'], count)
        
        if not messages:
            await query.edit_message_text(
                f"📜 Історія каналу: {project['name']}\n\n❌ Не вдалося отримати повідомлення.\nМожливо, немає доступу до каналу або канал порожній.",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            # Форматуємо повідомлення
            history_text = format_discord_history(messages, project['name'], count)
            
            # Розбиваємо на частини якщо текст занадто довгий
            if len(history_text) > 4000:
                # Telegram має ліміт на довжину повідомлення
                parts = [history_text[i:i+4000] for i in range(0, len(history_text), 4000)]
                for i, part in enumerate(parts):
                    if i == 0:
                        await query.edit_message_text(part)
                    else:
                        await context.bot.send_message(chat_id=user_id, text=part)
            else:
                await query.edit_message_text(history_text, reply_markup=get_main_menu_keyboard())
                
    except Exception as e:
        logger.error(f"Помилка отримання історії Discord: {e}")
        await query.edit_message_text(
            f"❌ Помилка при отриманні історії каналу {project['name']}:\n{str(e)}",
            reply_markup=get_main_menu_keyboard()
        )
    finally:
        # Очищуємо стан користувача
        if user_id in user_states:
            del user_states[user_id]

async def get_discord_messages_history(channel_url: str, limit: int) -> List[Dict]:
    """Отримати історію повідомлень з Discord каналу"""
    if not DISCORD_AUTHORIZATION:
        return []
    
    try:
        # Парсимо URL для отримання channel_id
        import re
        match = re.search(r'discord\.com/channels/(\d+)/(\d+)', channel_url)
        if not match:
            return []
        
        channel_id = match.group(2)
        
        # Створюємо новий session для цього запиту
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://discord.com/api/v9/channels/{channel_id}/messages?limit={limit}",
                headers={
                    'Authorization': DISCORD_AUTHORIZATION,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Помилка отримання повідомлень: {response.status}")
                    return []
                
    except Exception as e:
        logger.error(f"Помилка в get_discord_messages_history: {e}")
        return []

def format_discord_history(messages: List[Dict], channel_name: str, count: int) -> str:
    """Форматувати історію повідомлень Discord"""
    from datetime import datetime
    
    header = f"📜 **Історія каналу: {channel_name}**\n"
    header += f"📊 Останні {count} повідомлень:\n\n"
    
    if not messages:
        return header + "❌ Повідомлення не знайдено."
    
    formatted_messages = []
    for i, message in enumerate(messages, 1):
        author = message.get('author', {}).get('username', 'Unknown')
        content = message.get('content', '')
        timestamp = message.get('timestamp', '')
        
        # Форматуємо час
        try:
            if timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%d.%m.%Y %H:%M')
            else:
                time_str = 'Unknown time'
        except:
            time_str = 'Unknown time'
        
        # Обмежуємо довжину повідомлення
        if len(content) > 200:
            content = content[:200] + "..."
        
        formatted_msg = f"**{i}.** 👤 {author} | 🕒 {time_str}\n"
        if content:
            formatted_msg += f"💬 {content}\n"
        formatted_msg += "─" * 30 + "\n"
        
        formatted_messages.append(formatted_msg)
    
    return header + "\n".join(formatted_messages)

def handle_discord_notifications_sync(new_messages: List[Dict]) -> None:
    """Обробник нових повідомлень Discord (оптимізована версія)"""
    global bot_instance
    
    if not bot_instance:
        return
        
    try:
        # Отримуємо всіх користувачів з налаштованими каналами пересилання
        # (не залежить від авторизації)
        all_users = project_manager.get_all_users()
        users_with_forwarding = []
        
        for user_id in all_users:
            forward_channel = project_manager.get_forward_channel(user_id)
            if forward_channel:
                users_with_forwarding.append(user_id)
        
        if not users_with_forwarding:
            return
                
        # Швидка обробка повідомлень
        for message in new_messages:
            message_id = message.get('message_id', '')
            channel_id = message.get('channel_id', '')
            
            # Красиве форматування
            author = escape_markdown(message['author'])
            content = escape_markdown(message['content'])
            
            # Обрізаємо текст якщо він занадто довгий
            if len(content) > 200:
                content = content[:200] + "..."
            
            # Форматуємо дату
            timestamp = message.get('timestamp', '')
            formatted_date = "Не відомо"
            time_ago = ""
            
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%d %B, %H:%M UTC")
                    time_ago = _get_time_ago(dt)
                except:
                    formatted_date = timestamp[:19] if len(timestamp) > 19 else timestamp
            
            # Отримуємо інформацію про сервер з URL
            server_name = "Discord"
            try:
                # Спробуємо витягти guild_id з URL
                url_parts = message['url'].split('/')
                if len(url_parts) >= 5:
                    guild_id = url_parts[4]
                    server_name = f"Discord Server ({guild_id})"
            except:
                pass
            
            forward_text = (
                f"📢 **Нове повідомлення з Discord**\n"
                f"• Сервер: {server_name}\n"
                f"• Автор: {author}\n"
                f"• Дата: {formatted_date} ({time_ago})\n"
                f"• Текст: {content}\n"
                f"🔗 [Перейти до повідомлення]({message['url']})"
            )
            
            for user_id in users_with_forwarding:
                try:
                    # Швидка перевірка каналу
                    forward_channel = project_manager.get_forward_channel(user_id)
                    if not forward_channel:
                        continue
                    
                    # Швидка перевірка дублікатів
                    forward_key = f"forward_{channel_id}_{message_id}"
                    if project_manager.is_message_sent(forward_key, forward_channel, user_id):
                        continue
                    
                    # Швидка відправка
                    import requests
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    data = {
                        'chat_id': forward_channel,
                        'text': forward_text,
                        'parse_mode': 'Markdown'
                    }
                    response = requests.post(url, data=data, timeout=3)  # Зменшений timeout
                    
                    if response.status_code == 200:
                        project_manager.add_sent_message(forward_key, forward_channel, user_id)
                        logger.info(f"✅ Переслано в канал {forward_channel} (користувач {user_id})")
                    else:
                        logger.error(f"❌ Помилка відправки в канал {forward_channel}: {response.status_code}")
                    
                except Exception as e:
                    logger.error(f"Помилка обробки користувача {user_id}: {e}")
                    
    except Exception as e:
        logger.error(f"Помилка обробки Discord сповіщень: {e}")

def handle_twitter_notifications_sync(new_tweets: List[Dict]) -> None:
    """Обробник нових твітів Twitter (оптимізована версія)"""
    global bot_instance
    
    if not bot_instance:
        return
        
    try:
        # Отримуємо всіх користувачів з налаштованими каналами пересилання
        all_users = project_manager.get_all_users()
        users_with_forwarding = []
        
        for user_id in all_users:
            forward_channel = project_manager.get_forward_channel(user_id)
            if forward_channel:
                users_with_forwarding.append(user_id)
        
        if not users_with_forwarding:
            return
                
        # Швидка обробка твітів
        for tweet in new_tweets:
            tweet_id = tweet.get('tweet_id', '')
            account = tweet.get('account', '')
            
            # Красиве форматування
            author = escape_markdown(tweet.get('author', 'Unknown'))
            text = escape_markdown(tweet.get('text', ''))
            
            # Обрізаємо текст якщо він занадто довгий
            if len(text) > 200:
                text = text[:200] + "..."
            
            # Форматуємо дату
            timestamp = tweet.get('timestamp', '')
            formatted_date = "Не відомо"
            time_ago = ""
            
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_date = dt.strftime("%d %B, %H:%M UTC")
                    time_ago = _get_time_ago(dt)
                except:
                    formatted_date = timestamp[:19] if len(timestamp) > 19 else timestamp
            
            forward_text = (
                f"🐦 **Новий твіт з Twitter**\n"
                f"• Профіль: @{account}\n"
                f"• Автор: {author}\n"
                f"• Дата: {formatted_date} ({time_ago})\n"
                f"• Текст: {text}\n"
                f"🔗 [Перейти до твіта]({tweet.get('url', '')})"
            )
            
            for user_id in users_with_forwarding:
                try:
                    # Швидка перевірка каналу
                    forward_channel = project_manager.get_forward_channel(user_id)
                    if not forward_channel:
                        continue
                    
                    # Швидка перевірка дублікатів
                    forward_key = f"twitter_{account}_{tweet_id}"
                    if project_manager.is_message_sent(forward_key, forward_channel, user_id):
                        continue
                    
                    # Швидка відправка
                    import requests
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    data = {
                        'chat_id': forward_channel,
                        'text': forward_text,
                        'parse_mode': 'Markdown'
                    }
                    response = requests.post(url, data=data, timeout=3)
                    
                    if response.status_code == 200:
                        project_manager.add_sent_message(forward_key, forward_channel, user_id)
                        logger.info(f"✅ Переслано Twitter твіт в канал {forward_channel} (користувач {user_id})")
                    else:
                        logger.error(f"❌ Помилка відправки Twitter твіта в канал {forward_channel}: {response.status_code}")
                    
                except Exception as e:
                    logger.error(f"Помилка обробки Twitter користувача {user_id}: {e}")
                    
    except Exception as e:
        logger.error(f"Помилка обробки Twitter сповіщень: {e}")

async def start_discord_monitoring():
    """Запустити моніторинг Discord"""
    global discord_monitor
    
    if not discord_monitor or not DISCORD_AUTHORIZATION:
        logger.warning("Discord authorization токен не налаштовано")
        return
        
    try:
        async with discord_monitor:
            # Додаємо всі Discord канали з проектів користувачів
            for user_id, projects in project_manager.data['projects'].items():
                for project in projects:
                    if project['platform'] == 'discord':
                        discord_monitor.add_channel(project['url'])
                        
            logger.info(f"Запуск моніторингу Discord каналів")
            await discord_monitor.start_monitoring(handle_discord_notifications_sync, MONITORING_INTERVAL)
            
    except Exception as e:
        logger.error(f"Помилка моніторингу Discord: {e}")

async def start_twitter_monitoring():
    """Запустити моніторинг Twitter з покращеним HTML парсингом"""
    global twitter_monitor
    
    if not twitter_monitor or not TWITTER_AUTH_TOKEN:
        logger.warning("Twitter auth_token не налаштовано")
        return
        
    try:
        async with twitter_monitor:
            # Додаємо всі Twitter акаунти з проектів користувачів
            for user_id, projects in project_manager.data['projects'].items():
                for project in projects:
                    if project['platform'] == 'twitter':
                        username = extract_twitter_username(project['url'])
                        if username:
                            twitter_monitor.add_account(username)
                            
            logger.info(f"Запуск моніторингу Twitter акаунтів з HTML парсингом")
            
            # Запускаємо власний цикл моніторингу з HTML парсингом
            while True:
                try:
                    # Отримуємо нові твіти через покращений HTML парсинг
                    new_tweets = await twitter_monitor.check_new_tweets()
                    
                    if new_tweets:
                        # Конвертуємо формат для сумісності з існуючим кодом
                        formatted_tweets = []
                        for tweet in new_tweets:
                            formatted_tweets.append({
                                'tweet_id': tweet.get('id', ''),
                                'account': tweet.get('user', {}).get('screen_name', ''),
                                'author': tweet.get('user', {}).get('name', ''),
                                'text': tweet.get('text', ''),
                                'url': tweet.get('url', ''),
                                'timestamp': tweet.get('created_at', '')
                            })
                        
                        # Відправляємо сповіщення
                        handle_twitter_notifications_sync(formatted_tweets)
                        logger.info(f"Оброблено {len(formatted_tweets)} нових твітів")
                    
                    # Чекаємо перед наступною перевіркою
                    await asyncio.sleep(TWITTER_MONITORING_INTERVAL)
                    
                except Exception as e:
                    logger.error(f"Помилка в циклі моніторингу Twitter: {e}")
                    await asyncio.sleep(30)  # Коротша затримка при помилці
            
    except Exception as e:
        logger.error(f"Помилка моніторингу Twitter: {e}")

async def start_selenium_twitter_monitoring():
    """Запустити Selenium Twitter моніторинг"""
    global selenium_twitter_monitor
    
    if not selenium_twitter_monitor:
        logger.warning("Selenium Twitter монітор не ініціалізовано")
        return
        
    try:
        selenium_twitter_monitor.monitoring_active = True
        
        logger.info(f"Запуск Selenium моніторингу Twitter акаунтів: {list(selenium_twitter_monitor.monitoring_accounts)}")
        
        # Основний цикл моніторингу
        while selenium_twitter_monitor.monitoring_active:
            try:
                # Отримуємо нові твіти через Selenium
                new_tweets = await selenium_twitter_monitor.check_new_tweets()
                
                if new_tweets:
                    # Конвертуємо формат для сумісності з існуючим кодом
                    formatted_tweets = []
                    for tweet in new_tweets:
                        formatted_tweets.append({
                            'tweet_id': tweet.get('id', ''),
                            'account': tweet.get('user', {}).get('screen_name', ''),
                            'author': tweet.get('user', {}).get('name', ''),
                            'text': tweet.get('text', ''),
                            'url': tweet.get('url', ''),
                            'timestamp': tweet.get('created_at', '')
                        })
                    
                    # Відправляємо сповіщення
                    handle_twitter_notifications_sync(formatted_tweets)
                    logger.info(f"Selenium: оброблено {len(formatted_tweets)} нових твітів")
                
                # Чекаємо перед наступною перевіркою
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Помилка в циклі Selenium моніторингу Twitter: {e}")
                await asyncio.sleep(30)  # Коротша затримка при помилці
            
    except Exception as e:
        logger.error(f"Помилка Selenium моніторингу Twitter: {e}")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробник помилок"""
    logger.error(f"Update {update} caused error {context.error}")

def check_sessions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Перевірити закінчені сесії"""
    try:
        security_manager.check_expired_sessions(context.bot)
    except Exception as e:
        logger.error(f"Помилка перевірки сесій: {e}")

def cleanup_old_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Очистити старі повідомлення"""
    try:
        project_manager.cleanup_old_messages(hours=24)
    except Exception as e:
        logger.error(f"Помилка очищення старих повідомлень: {e}")

def _get_time_ago(dt: datetime) -> str:
    """Отримати час тому"""
    try:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # Переконуємося що dt має timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        diff = now - dt
        
        total_seconds = int(diff.total_seconds())
        
        if total_seconds < 0:
            return "щойно"
        elif total_seconds < 60:
            return f"{total_seconds} секунд тому"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes} хвилин тому"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"{hours} годин тому"
        else:
            days = total_seconds // 86400
            return f"{days} днів тому"
    except Exception as e:
        logger.error(f"Помилка обчислення часу: {e}")
        return ""

# Selenium Twitter команди
async def selenium_auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для ручної авторизації в Twitter через Selenium"""
    global selenium_twitter_monitor
    
    if not selenium_twitter_monitor:
        selenium_twitter_monitor = SeleniumTwitterMonitor()
        await selenium_twitter_monitor.__aenter__()
    
    await update.message.reply_text("🔐 Відкриваю браузер для авторизації в Twitter...")
    
    try:
        if selenium_twitter_monitor.open_manual_auth():
            selenium_twitter_monitor.save_profile()
            await update.message.reply_text("✅ Авторизація завершена! Профіль збережено.")
        else:
            await update.message.reply_text("❌ Помилка відкриття авторизації")
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка авторизації: {str(e)}")

async def selenium_add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Додати акаунт для Selenium моніторингу"""
    global selenium_twitter_monitor
    
    if not context.args:
        await update.message.reply_text("❌ Вкажіть username Twitter акаунта!\n\n**Приклад:** /selenium_add pilk_xz")
        return
    
    username = context.args[0].replace('@', '').strip()
    
    if not selenium_twitter_monitor:
        selenium_twitter_monitor = SeleniumTwitterMonitor()
        await selenium_twitter_monitor.__aenter__()
    
    if selenium_twitter_monitor.add_account(username):
        await update.message.reply_text(f"✅ Додано Twitter акаунт для Selenium моніторингу: @{username}")
    else:
        await update.message.reply_text(f"❌ Помилка додавання акаунта: @{username}")

async def selenium_test_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Тестувати Selenium моніторинг"""
    global selenium_twitter_monitor
    
    if not context.args:
        await update.message.reply_text("❌ Вкажіть username Twitter акаунта!\n\n**Приклад:** /selenium_test pilk_xz")
        return
    
    username = context.args[0].replace('@', '').strip()
    
    if not selenium_twitter_monitor:
        selenium_twitter_monitor = SeleniumTwitterMonitor()
        await selenium_twitter_monitor.__aenter__()
    
    await update.message.reply_text(f"🔍 Тестування Selenium моніторингу для @{username}...")
    
    try:
        tweets = await selenium_twitter_monitor.get_user_tweets(username, limit=3)
        
        if tweets:
            result_text = f"✅ **Selenium тест успішний!**\n\nЗнайдено {len(tweets)} твітів:\n\n"
            
            for i, tweet in enumerate(tweets, 1):
                text_preview = tweet['text'][:100] + "..." if len(tweet['text']) > 100 else tweet['text']
                result_text += f"{i}. {text_preview}\n"
                result_text += f"   🔗 [Перейти]({tweet['url']})\n\n"
                
            await update.message.reply_text(result_text, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Твіти не знайдено для @{username}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Помилка тестування: {str(e)}")

async def selenium_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запустити Selenium Twitter моніторинг"""
    global selenium_twitter_monitor
    
    if not selenium_twitter_monitor:
        selenium_twitter_monitor = SeleniumTwitterMonitor()
        await selenium_twitter_monitor.__aenter__()
    
    if not selenium_twitter_monitor.monitoring_accounts:
        await update.message.reply_text("❌ Немає акаунтів для моніторингу! Додайте Twitter акаунти спочатку.")
        return
    
    # Запускаємо Selenium моніторинг в окремому потоці
    import threading
    selenium_thread = threading.Thread(target=lambda: asyncio.run(start_selenium_twitter_monitoring()))
    selenium_thread.daemon = True
    selenium_thread.start()
    
    await update.message.reply_text("🚀 **Selenium Twitter моніторинг запущено!**\n\nБот буде перевіряти нові твіти кожні 30 секунд.", parse_mode='Markdown')

async def selenium_stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Зупинити Selenium Twitter моніторинг"""
    global selenium_twitter_monitor
    
    if selenium_twitter_monitor:
        selenium_twitter_monitor.monitoring_active = False
        await selenium_twitter_monitor.__aexit__(None, None, None)
        selenium_twitter_monitor = None
    
    await update.message.reply_text("⏹️ **Selenium Twitter моніторинг зупинено!**", parse_mode='Markdown')

# Менеджер акаунтів
async def accounts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показати всі акаунти для моніторингу"""
    user_id = update.effective_user.id
    
    # Отримуємо проекти користувача
    projects = project_manager.get_user_projects(user_id)
    
    if not projects:
        await update.message.reply_text("❌ У вас немає проектів для моніторингу.\n\nДодайте проекти через меню бота.")
        return
    
    # Групуємо по платформах
    twitter_projects = [p for p in projects if p['platform'] == 'twitter']
    discord_projects = [p for p in projects if p['platform'] == 'discord']
    
    # Форматуємо список
    text = "📋 **Ваші акаунти для моніторингу:**\n\n"
    
    if twitter_projects:
        text += "🐦 **Twitter/X акаунти:**\n"
        for i, project in enumerate(twitter_projects, 1):
            username = extract_twitter_username(project['url'])
            text += f"{i}. @{username} ({project['name']})\n"
        text += "\n"
    
    if discord_projects:
        text += "💬 **Discord канали:**\n"
        for i, project in enumerate(discord_projects, 1):
            channel_id = extract_discord_channel_id(project['url'])
            text += f"{i}. Канал {channel_id} ({project['name']})\n"
        text += "\n"
    
    # Додаємо команди для видалення
    text += "🔧 **Команди для управління:**\n"
    text += "• /remove_twitter username - видалити Twitter акаунт\n"
    text += "• /remove_discord channel_id - видалити Discord канал\n"
    text += "• /accounts - показати цей список"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def remove_twitter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Видалити Twitter акаунт з моніторингу"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ Вкажіть username Twitter акаунта!\n\n**Приклад:** /remove_twitter pilk_xz")
        return
    
    username = context.args[0].replace('@', '').strip()
    
    # Знаходимо проект для видалення
    projects = project_manager.get_user_projects(user_id)
    twitter_projects = [p for p in projects if p['platform'] == 'twitter']
    
    project_to_remove = None
    for project in twitter_projects:
        if extract_twitter_username(project['url']) == username:
            project_to_remove = project
            break
    
    if not project_to_remove:
        await update.message.reply_text(f"❌ Twitter акаунт @{username} не знайдено в ваших проектах.")
        return
    
    # Видаляємо проект
    if project_manager.remove_project(user_id, project_to_remove['name']):
        await update.message.reply_text(f"✅ Twitter акаунт @{username} видалено з моніторингу.")
        
        # Також видаляємо з Selenium монітора якщо він активний
        global selenium_twitter_monitor
        if selenium_twitter_monitor and username in selenium_twitter_monitor.monitoring_accounts:
            selenium_twitter_monitor.monitoring_accounts.discard(username)
            if username in selenium_twitter_monitor.seen_tweets:
                del selenium_twitter_monitor.seen_tweets[username]
            await update.message.reply_text(f"✅ Акаунт @{username} також видалено з Selenium моніторингу.")
    else:
        await update.message.reply_text(f"❌ Помилка видалення Twitter акаунта @{username}.")

async def remove_discord_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Видалити Discord канал з моніторингу"""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text("❌ Вкажіть ID Discord каналу!\n\n**Приклад:** /remove_discord 1358806016648544326")
        return
    
    channel_id = context.args[0].strip()
    
    # Знаходимо проект для видалення
    projects = project_manager.get_user_projects(user_id)
    discord_projects = [p for p in projects if p['platform'] == 'discord']
    
    project_to_remove = None
    for project in discord_projects:
        if extract_discord_channel_id(project['url']) == channel_id:
            project_to_remove = project
            break
    
    if not project_to_remove:
        await update.message.reply_text(f"❌ Discord канал {channel_id} не знайдено в ваших проектах.")
        return
    
    # Видаляємо проект
    if project_manager.remove_project(user_id, project_to_remove['name']):
        await update.message.reply_text(f"✅ Discord канал {channel_id} видалено з моніторингу.")
        
        # Також видаляємо з Discord монітора якщо він активний
        global discord_monitor
        if discord_monitor and channel_id in discord_monitor.monitoring_channels:
            discord_monitor.monitoring_channels.discard(channel_id)
            if channel_id in discord_monitor.last_message_ids:
                del discord_monitor.last_message_ids[channel_id]
            await update.message.reply_text(f"✅ Канал {channel_id} також видалено з Discord моніторингу.")
    else:
        await update.message.reply_text(f"❌ Помилка видалення Discord каналу {channel_id}.")

def extract_twitter_username(url: str) -> str:
    """Витягти username з Twitter URL"""
    import re
    match = re.search(r'twitter\.com/([^/?]+)', url)
    return match.group(1) if match else url

def extract_discord_channel_id(url: str) -> str:
    """Витягти channel_id з Discord URL"""
    import re
    match = re.search(r'discord\.com/channels/\d+/(\d+)', url)
    return match.group(1) if match else url

def main() -> None:
    """Головна функція"""
    global bot_instance
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не встановлено! Створіть файл .env з BOT_TOKEN")
        return
    
    if not DISCORD_AUTHORIZATION:
        logger.warning("AUTHORIZATION токен не встановлено! Discord моніторинг буде відключено")
    
    # Створюємо додаток
    application = Application.builder().token(BOT_TOKEN).build()
    bot_instance = application.bot
    
    # Додаємо обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Selenium Twitter команди
    application.add_handler(CommandHandler("selenium_auth", selenium_auth_command))
    application.add_handler(CommandHandler("selenium_add", selenium_add_command))
    application.add_handler(CommandHandler("selenium_test", selenium_test_command))
    application.add_handler(CommandHandler("selenium_start", selenium_start_command))
    application.add_handler(CommandHandler("selenium_stop", selenium_stop_command))
    
    # Менеджер акаунтів
    application.add_handler(CommandHandler("accounts", accounts_command))
    application.add_handler(CommandHandler("remove_twitter", remove_twitter_command))
    application.add_handler(CommandHandler("remove_discord", remove_discord_command))
    
    application.add_error_handler(error_handler)
    
    # Додаємо періодичну перевірку сесій (кожну хвилину)
    job_queue = application.job_queue
    job_queue.run_repeating(check_sessions, interval=300, first=300)  # Кожні 5 хвилин
    
    # Додаємо періодичне очищення старих повідомлень (кожні 2 години)
    job_queue.run_repeating(cleanup_old_messages, interval=7200, first=7200)
    
    logger.info("Бот запускається...")
    
    # Запускаємо Discord моніторинг в окремому потоці
    if discord_monitor and DISCORD_AUTHORIZATION:
        import threading
        discord_thread = threading.Thread(target=lambda: asyncio.run(start_discord_monitoring()))
        discord_thread.daemon = True
        discord_thread.start()
        logger.info("Discord моніторинг запущено")
    
    # Запускаємо Twitter моніторинг в окремому потоці
    if twitter_monitor and TWITTER_AUTH_TOKEN:
        import threading
        twitter_thread = threading.Thread(target=lambda: asyncio.run(start_twitter_monitoring()))
        twitter_thread.daemon = True
        twitter_thread.start()
        logger.info("Twitter моніторинг запущено")
    
    # Запускаємо бота
    try:
        application.run_polling()
    except KeyboardInterrupt:
        # Примусово зберігаємо дані при завершенні
        project_manager.save_data(force=True)
        logger.info("Бот зупинено, дані збережено")

if __name__ == '__main__':
    main()