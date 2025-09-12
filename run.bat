@echo off
echo Запуск телеграм бота...
echo.

REM Перевіряємо чи існує файл .env
if not exist .env (
    echo Помилка: Файл .env не знайдено!
    echo Створіть файл .env на основі .env.example
    echo та встановіть BOT_TOKEN та ADMIN_PASSWORD
    pause
    exit /b 1
)

REM Встановлюємо залежності якщо потрібно
echo Встановлення залежностей...
pip install -r requirements.txt

echo.
echo Запуск бота...
python bot.py

pause