"""Convert DOCX/PPTX files to PDF using LibreOffice headless."""

import subprocess
import sys
from pathlib import Path

def get_soffice_path():
    """البحث عن مسار LibreOffice (Portable أو على الويندوز)"""
    # 1. البحث في مجلد المشروع (Portable Version)
    if getattr(sys, 'frozen', False):
        # لو البرنامج اتعمله exe (PyInstaller)
        base_path = Path(sys.executable).parent / "libreoffice"
    else:
        # لو شغال كـ Python عادي وقت التطوير
        base_path = Path(__file__).resolve().parent.parent.parent / "resources" / "bin" / "libreoffice"
        
    local_soffice = base_path / "program" / "soffice.exe"
    if local_soffice.exists():
        return str(local_soffice)
        
    # 2. البحث في مسارات الويندوز الافتراضية لو مش لاقيناه Portable
    default_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    for p in default_paths:
        if Path(p).exists():
            return p
            
    return "soffice" # Fallback

def convert_document_to_pdf(input_path: str, output_dir: str) -> str:
    """Convert DOCX/PPTX to PDF using LibreOffice."""
    input_file = Path(input_path)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    # جلب مسار LibreOffice
    soffice_exe = get_soffice_path()
    
    # بناء أمر التحويل
    cmd = [
        soffice_exe, "--headless", "--convert-to", "pdf",
        "--outdir", str(output_dir_path), str(input_file)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    except Exception as e:
        raise RuntimeError(f"LibreOffice error: {e}")
        
    output_pdf = output_dir_path / f"{input_file.stem}.pdf"
    
    if output_pdf.exists():
        return str(output_pdf)
    else:
        raise RuntimeError("LibreOffice conversion failed. Output file not found.")