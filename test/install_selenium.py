#!/usr/bin/env python3
"""
Скрипт для встановлення Selenium та ChromeDriver
"""

import subprocess
import sys
import os
import zipfile
import requests
from pathlib import Path

def install_selenium():
    """Встановити Selenium"""
    print("📦 Встановлення Selenium...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium==4.15.0"])
        print("✅ Selenium встановлено успішно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Помилка встановлення Selenium: {e}")
        return False

def download_chromedriver():
    """Завантажити ChromeDriver"""
    print("🌐 Завантаження ChromeDriver...")
    
    # Визначаємо версію Chrome
    try:
        import subprocess
        result = subprocess.run(['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.strip().split('\n')[-1]
            chrome_version = version_line.split()[-1]
            major_version = chrome_version.split('.')[0]
            print(f"🔍 Знайдено Chrome версії: {chrome_version}")
        else:
            print("⚠️ Не вдалося визначити версію Chrome, використовуємо останню")
            major_version = "119"  # Остання стабільна версія
    except Exception as e:
        print(f"⚠️ Помилка визначення версії Chrome: {e}")
        major_version = "119"
    
    # URL для завантаження ChromeDriver
    chromedriver_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
    
    try:
        # Отримуємо останню версію
        response = requests.get(chromedriver_url, timeout=10)
        if response.status_code == 200:
            driver_version = response.text.strip()
            print(f"📥 Завантаження ChromeDriver версії: {driver_version}")
            
            # URL для завантаження
            download_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_win32.zip"
            
            # Завантажуємо файл
            response = requests.get(download_url, timeout=30)
            if response.status_code == 200:
                # Зберігаємо zip файл
                zip_path = "chromedriver.zip"
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                # Розпаковуємо
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall('.')
                
                # Видаляємо zip файл
                os.remove(zip_path)
                
                print("✅ ChromeDriver завантажено та розпаковано")
                return True
            else:
                print(f"❌ Помилка завантаження ChromeDriver: {response.status_code}")
                return False
        else:
            print(f"❌ Помилка отримання версії ChromeDriver: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка завантаження ChromeDriver: {e}")
        return False

def check_chrome_installed():
    """Перевірити чи встановлений Chrome"""
    print("🔍 Перевірка встановлення Chrome...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome знайдено: {path}")
            return True
    
    print("❌ Chrome не знайдено. Будь ласка, встановіть Google Chrome")
    print("🌐 Завантажити можна тут: https://www.google.com/chrome/")
    return False

def main():
    """Головна функція"""
    print("🚀 Встановлення залежностей для Selenium моніторингу")
    print("=" * 60)
    
    # Перевіряємо Chrome
    if not check_chrome_installed():
        return
    
    # Встановлюємо Selenium
    if not install_selenium():
        return
    
    # Завантажуємо ChromeDriver
    if not download_chromedriver():
        print("⚠️ ChromeDriver не завантажено, але можна спробувати запустити скрипт")
        print("💡 Якщо виникнуть помилки, встановіть ChromeDriver вручну")
    
    print("\n🎉 Встановлення завершено!")
    print("💡 Тепер можна запустити: python monitor_pilk_xz_selenium.py")

if __name__ == "__main__":
    main()