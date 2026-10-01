"""Multi Print application entry point."""

import sys
import os
from pathlib import Path

# --- تحديد مسارات البرنامج حسب وضع التشغيل ---
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
    FRONTEND_DIR = BASE_DIR / "frontend"
    ROOT_DIR = Path(sys.executable).parent
    UPLOAD_DIR = ROOT_DIR / "temp_uploads"
    try:
        UPLOAD_DIR.mkdir(exist_ok=True)
    except Exception:
        pass
else:
    ROOT_DIR = Path(__file__).resolve().parent.parent
    sys.path.append(str(ROOT_DIR))
    FRONTEND_DIR = ROOT_DIR / "frontend"
    UPLOAD_DIR = ROOT_DIR / "temp_uploads"
    UPLOAD_DIR.mkdir(exist_ok=True)

    site_packages = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'pywin32_system32')
    if os.path.exists(site_packages):
        sys.path.append(site_packages)
        try:
            os.add_dll_directory(site_packages)
        except Exception:
            pass

import threading
from updater import check_for_updates
import time
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import webview

from backend.api.printers import router as printers_router
from backend.api.files import router as files_router
from backend.api.print_jobs import router as print_router
from backend.api.history import router as history_router

app = FastAPI(title="Multi Print")
app.include_router(printers_router)
app.include_router(files_router)
app.include_router(print_router)
app.include_router(history_router)

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
app.mount("/files", StaticFiles(directory=UPLOAD_DIR), name="files")

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    # 1. فحص التحديثات في Thread منفصل عشان مايعلقش فتح البرنامج
    update_thread = threading.Thread(target=check_for_updates, daemon=True)
    update_thread.start()
    
    # 2. تشغيل السيرفر
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    
    # 3. فتح الواجهة
    webview.create_window("Multi Print", "http://127.0.0.1:8000", width=1000, height=700, min_size=(800, 600))
    webview.start()