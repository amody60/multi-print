import requests
import zipfile
import os
import subprocess
import ctypes
import sys
import shutil
from backend.config.logger import logger

# ✅ ضع اسم المستخدم بتاعك واسم الريبو بتاعك هنا
GITHUB_REPO = "https://api.github.com/repos/amody60/multi-print/releases/latest"
CURRENT_VERSION = "1.0.4" # كل ما تعمل ابديت، غير الرقم ده

def check_for_updates():
    try:
        logger.info("Checking for updates...")
        response = requests.get(GITHUB_REPO)
        data = response.json()
        
        latest_version = data.get("tag_name", "v1.0.0").replace("v", "")
        download_url = data.get("assets", [{}])[0].get("browser_download_url")

        if not download_url:
            return

        # ✅ تحويل النصوص لأرقام للمقارنة الصح
        def v_tuple(v): return tuple(map(int, v.split(".")))
        if v_tuple(latest_version) > v_tuple(CURRENT_VERSION):
            logger.info(f"New version found: {latest_version}")
            # رسالة ويندوز تطلب من المستخدم الموافقة على التحديث
        # ✅ جلب الأيقونة من البرنامج نفسه لعرضها في رسالة التحديث
        if getattr(sys, 'frozen', False):
            hwnd = 0
            hicon = ctypes.windll.shell32.ExtractIconW(0, sys.executable, 0)
            if hicon:
                ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)

        result = ctypes.windll.user32.MessageBoxW(0, f"يتوفر إصدار جديد ({latest_version}).\nهل تريد تحديث البرنامج الآن؟ سيتم إغلاق البرنامج وإعادة تشغيله تلقائياً.", "تحديث Multi Print", 4 | 64)            if result == 6: # 6 يعني المستخدم داس Yes
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

        # ✅ البحث عن ملف Setup.exe (بأي اسم) داخل الملفات اللي اتنزلت
        setup_exe = None
        for root, dirs, files in os.walk(extract_folder):
            for file in files:
                if file.lower().endswith("setup.exe"):
                    setup_exe = os.path.join(root, file)
                    break
            if setup_exe:
                break

        if not setup_exe:
            raise RuntimeError("Setup.exe not found in update package.")

        # ✅ تشغيل ملف الـ Setup في الوضع الصامت (Silent Mode)
        # /VERYSILENT بيخليه يتسطب من غير واجهة، /NORESTART يمنع الويندوز يعمل ريستارت
        # /CLOSEAPPLICATIONS بيقفل أي نسخة قديمة شغالة، /NOCANCEL يمنع الإلغاء
        subprocess.Popen([setup_exe, "/VERYSILENT", "/NORESTART", "/CLOSEAPPLICATIONS", "/NOCANCEL"])
        
        # ✅ إغلاق البرنامج الحالي فوراً عشان الـ Setup يقدر يكمل ويفتح النسخة الجديدة
        sys.exit(0)

    except Exception as e:
        logger.error(f"Update installation failed: {e}")

if __name__ == "__main__":
    check_for_updates()