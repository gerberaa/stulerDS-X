#!/usr/bin/env python3
"""
Швидкий скрипт для компіляції проекту
Автоматично визначає платформу та запускає відповідний скрипт
"""

import os
import sys
import platform
import subprocess

def main():
    """Головна функція"""
    print("🚀 Швидка компіляція Telegram Monitor Bot")
    print("=" * 50)
    print(f"💻 Платформа: {platform.system()}")
    print("=" * 50)
    
    system = platform.system().lower()
    
    if system == "windows":
        print("🪟 Запуск компіляції для Windows...")
        try:
            subprocess.run(["build.bat"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Помилка запуску build.bat")
            return False
        except FileNotFoundError:
            print("❌ Файл build.bat не знайдено")
            return False
    elif system == "linux":
        print("🐧 Запуск компіляції для Linux...")
        try:
            subprocess.run(["./build.sh"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Помилка запуску build.sh")
            return False
        except FileNotFoundError:
            print("❌ Файл build.sh не знайдено")
            return False
    else:
        print(f"❌ Непідтримувана платформа: {platform.system()}")
        print("Запустіть build.py вручну")
        return False
    
    print("\n🎉 Компіляція завершена!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)