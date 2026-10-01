"""Store and retrieve print history."""
import sys
import os
import json
from pathlib import Path
from datetime import datetime

def get_data_dir():
    if getattr(sys, 'frozen', False):
        app_data = os.getenv('APPDATA')
        if app_data:
            data_dir = Path(app_data) / "MultiPrint"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir
    return Path(__file__).resolve().parent

HISTORY_FILE = get_data_dir() / "history.json"

def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def add_history_item(item: dict) -> None:
    history = load_history()
    item["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(item)
    if len(history) > 100:
        history = history[-100:]
    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)