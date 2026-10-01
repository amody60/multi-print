"""Persistent application settings helpers."""
import sys
import os
import json
from pathlib import Path
from typing import Any

def get_data_dir():
    """تحديد مسار حفظ البيانات (AppData لو البرنامج exe، أو مسار المشروع لو تطوير)"""
    if getattr(sys, 'frozen', False):
        # وضع الـ EXE: نحفظ في AppData/Roaming/MultiPrint
        app_data = os.getenv('APPDATA')
        if app_data:
            data_dir = Path(app_data) / "MultiPrint"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir
    # وضع التطوير
    return Path(__file__).resolve().parent

SETTINGS_FILE = get_data_dir() / "settings.json"

def load_settings() -> dict[str, Any]:
    if not SETTINGS_FILE.exists():
        return {}
    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as settings_file:
            return json.load(settings_file)
    except Exception:
        return {}

def save_settings(data: dict[str, Any]) -> None:
    with SETTINGS_FILE.open("w", encoding="utf-8") as settings_file:
        json.dump(data, settings_file, ensure_ascii=False, indent=2)