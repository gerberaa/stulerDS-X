@echo off
chcp 65001 >nul
echo 🚀 Компіляція Telegram Monitor Bot для Windows
echo ================================================
echo.

REM Перевіряємо чи існує Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не знайдено! Встановіть Python 3.8+ з python.org
    pause
    exit /b 1
)

echo ✅ Python знайдено
echo.

REM Встановлюємо PyInstaller якщо потрібно
echo 📦 Перевірка PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 📦 Встановлення PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Помилка встановлення PyInstaller
        pause
        exit /b 1
    )
) else (
    echo ✅ PyInstaller вже встановлений
)

echo.
echo 🔨 Запуск компіляції...
python build.py

if errorlevel 1 (
    echo.
    echo ❌ Помилка компіляції!
    pause
    exit /b 1
)

echo.
echo 🎉 Компіляція завершена успішно!
echo 📁 Готовий проект знаходиться в папці: dist_package\
echo.
echo Для запуску:
echo 1. Перейдіть в папку dist_package\
echo 2. Скопіюйте .env.example в .env
echo 3. Налаштуйте параметри в .env файлі
echo 4. Запустіть run.bat
echo.
pause