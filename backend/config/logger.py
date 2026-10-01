import sys
import os
import logging
from pathlib import Path

def get_data_dir():
    if getattr(sys, 'frozen', False):
        app_data = os.getenv('APPDATA')
        if app_data:
            data_dir = Path(app_data) / "MultiPrint"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir
    return Path(__file__).resolve().parent.parent.parent

LOG_FILE = get_data_dir() / "log.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MultiPrint")