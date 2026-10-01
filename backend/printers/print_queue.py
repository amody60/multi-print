"""Handle actual printing tasks via SumatraPDF subprocess."""
import sys
import subprocess
import os
import shutil
import tempfile
import uuid
from pathlib import Path
from backend.config.logger import logger

if getattr(sys, 'frozen', False):
    SUMATRA_PATH = Path(sys._MEIPASS) / "backend" / "resources" / "bin" / "SumatraPDF.exe"
else:
    SUMATRA_PATH = Path(__file__).resolve().parent.parent / "resources" / "bin" / "SumatraPDF.exe"

def print_pdf_file(pdf_path: str, printer_name: str, duplex: bool = False, color: bool = True, copies: int = 1, orientation: str = "portrait") -> dict:
    if not SUMATRA_PATH.exists():
        msg = "SumatraPDF.exe غير موجود."
        logger.error(msg)
        return {"success": False, "error": msg}

    settings = []
    if duplex:
        if orientation == "landscape":
            settings.append("DuplexShort")
        else:
            settings.append("DuplexLong") 
    else:
        settings.append("Simplex")
        
    if color:
        settings.append("Color")
    else:
        settings.append("Grayscale")
        
    settings.append(f"Copies={copies}")
    settings_str = ",".join(settings)

    temp_dir = tempfile.gettempdir()
    temp_pdf_name = f"print_job_{uuid.uuid4().hex}.pdf"
    temp_pdf_path = Path(temp_dir) / temp_pdf_name
    
    try:
        shutil.copy(str(Path(pdf_path).resolve()), str(temp_pdf_path))
        
        cmd = [
            str(SUMATRA_PATH),
            "-print-to", printer_name,
            "-print-settings", settings_str,
            "-silent",
            "-exit-when-done",
            str(temp_pdf_path)
        ]

        file_size_mb = os.path.getsize(str(temp_pdf_path)) / (1024 * 1024)
        dynamic_timeout = max(30, int(file_size_mb * 10))
        
        logger.info(f"Sending {temp_pdf_path} to {printer_name}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=dynamic_timeout)
        
        if result.returncode == 0:
            logger.info(f"Success printing on {printer_name}!")
        else:
            logger.warning(f"SumatraPDF returned code {result.returncode} for {printer_name}, but it may have printed.")
        
        return {"success": True}
        
    except subprocess.TimeoutExpired:
        msg = f"الملف كبير جداً (Timeout)."
        logger.error(f"Timeout for {printer_name}")
        return {"success": False, "error": msg}
    except Exception as e:
        msg = f"خطأ غير متوقع: {str(e)}"
        logger.error(msg)
        return {"success": False, "error": msg}
    finally:
        if temp_pdf_path.exists():
            try: temp_pdf_path.unlink()
            except: pass