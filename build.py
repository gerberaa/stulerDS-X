#!/usr/bin/env python3
"""
Скрипт для компіляції проекту в один виконуваний файл
Підтримує Windows та Linux
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def check_pyinstaller():
    """Перевірити чи встановлений PyInstaller"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller встановлений: версія {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller не встановлений")
        return False

def install_pyinstaller():
    """Встановити PyInstaller"""
    print("📦 Встановлення PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller успішно встановлений")
        return True
    except subprocess.CalledProcessError:
        print("❌ Помилка встановлення PyInstaller")
        return False

def create_spec_file():
    """Створити .spec файл для PyInstaller"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Список всіх Python файлів проекту
a = Analysis(
    ['bot.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data.json', '.'),
        ('projects.json', '.'),
        ('browser_profile', 'browser_profile'),
        ('*.md', '.'),
    ],
    hiddenimports=[
        'telegram',
        'telegram.ext',
        'telegram.ext.filters',
        'aiohttp',
        'requests',
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.wait',
        'selenium.webdriver.support.expected_conditions',
        'selenium.common.exceptions',
        'dotenv',
        'asyncio',
        'threading',
        'logging',
        'datetime',
        'json',
        'os',
        'sys',
        'pathlib',
        'typing',
        'security_manager',
        'project_manager',
        'discord_monitor',
        'twitter_monitor',
        'selenium_twitter_monitor',
        'config',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='telegram_monitor_bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open('telegram_monitor_bot.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Створено файл telegram_monitor_bot.spec")

def build_executable():
    """Скомпілювати виконуваний файл"""
    print("🔨 Компіляція виконуваного файлу...")
    
    try:
        # Використовуємо .spec файл для більш точного контролю
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller", 
            "--clean", 
            "telegram_monitor_bot.spec"
        ])
        
        print("✅ Компіляція завершена успішно!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Помилка компіляції: {e}")
        return False

def create_distribution():
    """Створити папку з готовим проектом"""
    print("📁 Створення папки розповсюдження...")
    
    dist_dir = Path("dist_package")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir()
    
    # Копіюємо виконуваний файл
    exe_name = "telegram_monitor_bot.exe" if platform.system() == "Windows" else "telegram_monitor_bot"
    exe_path = Path("dist") / exe_name
    
    if exe_path.exists():
        shutil.copy2(exe_path, dist_dir / exe_name)
        print(f"✅ Скопійовано виконуваний файл: {exe_name}")
    else:
        print(f"❌ Виконуваний файл не знайдено: {exe_path}")
        return False
    
    # Копіюємо необхідні файли
    files_to_copy = [
        "data.json",
        "projects.json", 
        "browser_profile",
        "README.md",
        "ACCOUNT_MANAGER_GUIDE.md",
        "SELENIUM_TWITTER_GUIDE.md",
        "TWITTER_IMPROVEMENTS_SUMMARY.md"
    ]
    
    for file_name in files_to_copy:
        src_path = Path(file_name)
        if src_path.exists():
            if src_path.is_file():
                shutil.copy2(src_path, dist_dir / file_name)
            else:
                shutil.copytree(src_path, dist_dir / file_name)
            print(f"✅ Скопійовано: {file_name}")
    
    # Створюємо .env.example
    env_example = """# Конфігурація бота
BOT_TOKEN=your_bot_token_here
ADMIN_PASSWORD=401483

# Discord моніторинг (опціонально)
AUTHORIZATION=your_discord_authorization_token

# Twitter/X моніторинг (опціонально)
TWITTER_AUTH_TOKEN=your_twitter_auth_token
TWITTER_CSRF_TOKEN=your_twitter_csrf_token
"""
    
    with open(dist_dir / ".env.example", 'w', encoding='utf-8') as f:
        f.write(env_example)
    
    print("✅ Створено .env.example")
    
    # Створюємо скрипт запуску
    if platform.system() == "Windows":
        run_script = f"""@echo off
echo Запуск Telegram Monitor Bot...
echo.

REM Перевіряємо чи існує файл .env
if not exist .env (
    echo Помилка: Файл .env не знайдено!
    echo Скопіюйте .env.example в .env та налаштуйте параметри
    pause
    exit /b 1
)

echo Запуск бота...
{exe_name}

pause
"""
        with open(dist_dir / "run.bat", 'w', encoding='utf-8') as f:
            f.write(run_script)
    else:
        run_script = f"""#!/bin/bash
echo "Запуск Telegram Monitor Bot..."
echo ""

# Перевіряємо чи існує файл .env
if [ ! -f .env ]; then
    echo "Помилка: Файл .env не знайдено!"
    echo "Скопіюйте .env.example в .env та налаштуйте параметри"
    exit 1
fi

echo "Запуск бота..."
./{exe_name}
"""
        with open(dist_dir / "run.sh", 'w', encoding='utf-8') as f:
            f.write(run_script)
        os.chmod(dist_dir / "run.sh", 0o755)
    
    print("✅ Створено скрипт запуску")
    
    return True

def create_readme():
    """Створити README для розповсюдження"""
    readme_content = """# Telegram Monitor Bot - Готовий до запуску

## Опис
Це готовий до запуску Telegram бот для моніторингу Discord каналів та Twitter/X акаунтів.

## Швидкий старт

### Windows
1. Скопіюйте `.env.example` в `.env`
2. Налаштуйте параметри в `.env` файлі
3. Запустіть `run.bat`

### Linux
1. Скопіюйте `.env.example` в `.env`
2. Налаштуйте параметри в `.env` файлі
3. Запустіть `./run.sh`

## Налаштування .env файлу

### Обов'язкові параметри:
- `BOT_TOKEN` - токен вашого Telegram бота (отримайте у @BotFather)
- `ADMIN_PASSWORD` - пароль для доступу до бота (за замовчуванням: 401483)

### Опціональні параметри:
- `AUTHORIZATION` - Discord authorization токен для моніторингу Discord
- `TWITTER_AUTH_TOKEN` - Twitter auth_token для моніторингу Twitter/X
- `TWITTER_CSRF_TOKEN` - Twitter csrf_token для моніторингу Twitter/X

## Функції бота
- Моніторинг Discord каналів
- Моніторинг Twitter/X акаунтів
- Пересилання повідомлень в Telegram
- Менеджер акаунтів
- Діагностика системи

## Архітектура проекту
Проект зберігає всю архітектуру:
- `data.json` - база даних проектів та користувачів
- `projects.json` - конфігурація проектів
- `browser_profile/` - профіль браузера для Selenium
- Документація в .md файлах

## Підтримка
При виникненні проблем перевірте:
1. Правильність налаштувань в .env файлі
2. Наявність інтернет-з'єднання
3. Права доступу до файлів

## Версія
Версія: 1.0
Дата збірки: {date}
Платформа: {platform}
""".format(
        date=subprocess.check_output(['date'], shell=True).decode().strip() if platform.system() != "Windows" else "Windows",
        platform=platform.system()
    )
    
    with open("dist_package/README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ Створено README.md")

def main():
    """Головна функція"""
    print("🚀 Запуск компіляції Telegram Monitor Bot")
    print("=" * 50)
    
    # Перевіряємо PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("❌ Неможливо встановити PyInstaller. Завершення.")
            return False
    
    # Створюємо .spec файл
    create_spec_file()
    
    # Компілюємо
    if not build_executable():
        print("❌ Помилка компіляції. Завершення.")
        return False
    
    # Створюємо папку розповсюдження
    if not create_distribution():
        print("❌ Помилка створення папки розповсюдження. Завершення.")
        return False
    
    # Створюємо README
    create_readme()
    
    print("\n" + "=" * 50)
    print("🎉 Компіляція завершена успішно!")
    print(f"📁 Готовий проект знаходиться в папці: dist_package/")
    print(f"💻 Платформа: {platform.system()}")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)