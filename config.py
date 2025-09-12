import os
from dotenv import load_dotenv

load_dotenv()

# Конфігурація бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '401483')  # За замовчуванням
SECURITY_TIMEOUT = 300  # 5 хвилин в секундах

# Discord моніторинг
DISCORD_AUTHORIZATION = os.getenv('AUTHORIZATION')  # Discord authorization токен
MONITORING_INTERVAL = 15  # Інтервал перевірки нових повідомлень (секунди) - безпечно

# Twitter/X моніторинг
TWITTER_AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')  # Twitter auth_token
TWITTER_CSRF_TOKEN = os.getenv('TWITTER_CSRF_TOKEN')  # Twitter csrf_token (ct0)
TWITTER_MONITORING_INTERVAL = 30  # Інтервал перевірки нових твітів (секунди)

# Повідомлення
MESSAGES = {
    'welcome': 'Привіт! Я телеграм бот з базовою безпекою.',
    'password_request': 'Введіть пароль для доступу:',
    'password_correct': 'Пароль правильний! Доступ надано.',
    'password_incorrect': 'Неправильний пароль! Спробуйте ще раз.',
    'session_expired': 'Ваша сесія закінчилася. Введіть пароль знову.',
    'unauthorized': 'У вас немає доступу до цієї команди.'
}