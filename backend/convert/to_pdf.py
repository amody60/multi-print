"""Convert DOCX/PPTX files to PDF using LibreOffice headless."""
import subprocess
import sys
import os
from pathlib import Path
from backend.config.logger import logger

def get_data_dir():
    if getattr(sys, 'frozen', False):
        app_data = os.getenv('APPDATA')
        if app_data:
            data_dir = Path(app_data) / "MultiPrint"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir
    return Path(__file__).resolve().parent.parent.parent

def get_soffice_path():
    # 1. لو شغال كـ exe (بعد التسطيب)
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent / "libreoffice"
        possible_paths = [
            base_path / "program" / "soffice.exe",
            base_path / "App" / "libreoffice" / "program" / "soffice.exe",
            base_path / "LibreOfficePortable" / "App" / "libreoffice" / "program" / "soffice.exe"
        ]
        for p in possible_paths:
            if p.exists(): return str(p)
            
    # 2. لو شغال في بيئة التطوير (VS Code)
    project_root = Path(__file__).resolve().parent.parent.parent
    dev_paths = [
        # المسار زي ما إنت حاططه بالظبط في الصورة
        project_root / "libreoffice" / "LibreOfficePortable" / "App" / "libreoffice" / "program" / "soffice.exe",
        project_root / "libreoffice" / "App" / "libreoffice" / "program" / "soffice.exe",
        project_root / "libreoffice" / "program" / "soffice.exe"
    ]
    for p in dev_paths:
        if p.exists(): 
            logger.info(f"Found LibreOffice at: {p}")
            return str(p)

    # 3. لو متسطب عادي على الويندوز
    default_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    for p in default_paths:
        if Path(p).exists(): return p
            
    logger.error("LibreOffice (soffice.exe) not found in any path!")
    return "soffice"
def convert_document_to_pdf(input_path: str, output_dir: str) -> str:
    try:
        input_file = Path(input_path)
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        soffice_exe = get_soffice_path()
        
        lo_profile_dir = get_data_dir() / "lo_profile"
        lo_profile_dir.mkdir(parents=True, exist_ok=True)
        lo_profile_uri = lo_profile_dir.as_uri()
        
        cmd = [
            soffice_exe,
            f"-env:UserInstallation={lo_profile_uri}",
            "--headless", "--convert-to", "pdf",
            "--outdir", str(output_dir_path), str(input_file)
        ]
        
        logger.info(f"Attempting to convert with command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            logger.error(f"LibreOffice failed! Output: {result.stderr}")
            raise RuntimeError("LibreOffice failed to convert the file.")
            
        output_pdf = output_dir_path / f"{input_file.stem}.pdf"
        
        if output_pdf.exists():
            return str(output_pdf)
        else:
            raise RuntimeError("LibreOffice conversion failed. Output file not found.")
    except Exception as e:
        logger.error(f"LibreOffice error: {e}")
        raise RuntimeError(f"LibreOffice error: {e}")