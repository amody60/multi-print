"""Persistent application settings helpers."""

import json
from pathlib import Path
from typing import Any


SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"


def load_settings() -> dict[str, Any]:
    """Load saved settings, returning an empty dictionary when absent."""
    if not SETTINGS_FILE.exists():
        return {}

    with SETTINGS_FILE.open("r", encoding="utf-8") as settings_file:
        return json.load(settings_file)


def save_settings(data: dict[str, Any]) -> None:
    """Save application settings as UTF-8 JSON."""
    with SETTINGS_FILE.open("w", encoding="utf-8") as settings_file:
        json.dump(data, settings_file, ensure_ascii=False, indent=2)
