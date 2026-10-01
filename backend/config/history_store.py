"""Store and retrieve print history."""
import json
from pathlib import Path
from datetime import datetime

HISTORY_FILE = Path(__file__).resolve().parent / "history.json"

def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []
    with HISTORY_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def add_history_item(item: dict) -> None:
    history = load_history()
    item["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append(item)
    # الاحتفاظ بآخر 100 عملية طباعة فقط
    if len(history) > 100:
        history = history[-100:]
    with HISTORY_FILE.open("w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)