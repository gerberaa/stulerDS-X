#!/bin/bash

echo "🚀 Компіляція Telegram Monitor Bot для Linux"
echo "================================================"
echo

# Перевіряємо чи існує Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не знайдено! Встановіть Python 3.8+"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "CentOS/RHEL: sudo yum install python3 python3-pip"
    exit 1
fi

echo "✅ Python3 знайдено: $(python3 --version)"
echo

# Перевіряємо pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 не знайдено! Встановіть pip3"
    echo "Ubuntu/Debian: sudo apt install python3-pip"
    echo "CentOS/RHEL: sudo yum install python3-pip"
    exit 1
fi

echo "✅ pip3 знайдено"
echo

# Встановлюємо PyInstaller якщо потрібно
echo "📦 Перевірка PyInstaller..."
if ! python3 -c "import PyInstaller" &> /dev/null; then
    echo "📦 Встановлення PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "❌ Помилка встановлення PyInstaller"
        exit 1
    fi
else
    echo "✅ PyInstaller вже встановлений"
fi

echo
echo "🔨 Запуск компіляції..."
python3 build.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ Помилка компіляції!"
    exit 1
fi

echo
echo "🎉 Компіляція завершена успішно!"
echo "📁 Готовий проект знаходиться в папці: dist_package/"
echo
echo "Для запуску:"
echo "1. Перейдіть в папку dist_package/"
echo "2. Скопіюйте .env.example в .env"
echo "3. Налаштуйте параметри в .env файлі"
echo "4. Запустіть ./run.sh"
echo
echo "Натисніть Enter для завершення..."
read