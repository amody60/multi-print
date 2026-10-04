import requests
import zipfile
import os
import subprocess
import ctypes
import sys
import shutil
from backend.config.logger import logger

# ✅ تم تعديل الرابط باسمك
GITHUB_REPO = "https://api.github.com/repos/amody60/multi-print/releases/latest"
CURRENT_VERSION = "1.0.3" # غيرها كل ما تعمل Build جديد

def check_for_updates():
    try:
        logger.info("Checking for updates...")
        response = requests.get(GITHUB_REPO)
        data = response.json()
        
        latest_version = data.get("tag_name", "v1.0.0").replace("v", "")
        download_url = data.get("assets", [{}])[0].get("browser_download_url")

        if not download_url:
            return

        # تحويل النصوص لأرقام للمقارنة الصح
        def v_tuple(v): return tuple(map(int, v.split(".")))
        if v_tuple(latest_version) > v_tuple(CURRENT_VERSION):
            # رسالة ويندوز تطلب من المستخدم الموافقة على التحديث
            result = ctypes.windll.user32.MessageBoxW(0, f"يتوفر إصدار جديد ({latest_version}).\nهل تريد تحديث البرنامج الآن؟", "تحديث Multi Print", 4 | 64)
            if result == 6: # 6 يعني المستخدم داس Yes
                download_and_install_update(download_url)
    except Exception as e:
        logger.error(f"Update check failed: {e}")

def download_and_install_update(url):
    try:
        logger.info("Downloading update...")
        zip_path = "update.zip"
        
        # تحميل ملف الـ zip
        with requests.get(url, stream=True) as r:
            with open(zip_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        # فك الضغط في فولدر مؤقت
        extract_folder = "new_update"
        if os.path.exists(extract_folder):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        # إنشاء سكريبت باتش عشان يغلق البرنامج وينسخ الملفات ويعيد التشغيل
        bat_content = f"""@echo off
timeout /t 2 /nobreak >nul
taskkill /f /im MultiPrint.exe
xcopy /s /y "{extract_folder}\\*" ".\\"
start "" "MultiPrint.exe"
del "update.bat"
"""
        with open("update.bat", "w") as f:
            f.write(bat_content)

        # تشغيل سكريبت الباتش في الخلفية
        subprocess.Popen(["cmd", "/c", "update.bat"], creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit(0) # إغلاق البرنامج الحالي عشان الباتش يقدر يكمل شغله

    except Exception as e:
        logger.error(f"Update installation failed: {e}")

if __name__ == "__main__":
    check_for_updates()