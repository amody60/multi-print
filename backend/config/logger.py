import sys
import logging
from pathlib import Path

if getattr(sys, 'frozen', False):
    LOG_FILE = Path(sys.executable).parent / "log.txt"
else:
    LOG_FILE = Path(__file__).resolve().parent.parent.parent / "log.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("MultiPrint")