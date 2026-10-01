"""File upload, conversion, and preview API endpoints."""

import sys
import os
import time
import uuid
import base64
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
from typing import List
import fitz  # PyMuPDF

from backend.convert.to_pdf import convert_document_to_pdf
from backend.convert.image_to_pdf import convert_image_to_pdf
from backend.config.logger import logger

router = APIRouter(prefix="/api/files", tags=["files"])

def get_data_dir():
    if getattr(sys, 'frozen', False):
        app_data = os.getenv('APPDATA')
        if app_data:
            data_dir = Path(app_data) / "MultiPrint"
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir
    return Path(__file__).resolve().parent.parent.parent

# ✅ حفظ الملفات المؤقتة في AppData عشان الويندوز ميرفضش الكتابة
UPLOAD_DIR = get_data_dir() / "temp_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    original_name = file.filename
    original_path = Path(original_name)

    unique_id = uuid.uuid4().hex[:8]
    disk_stem = f"{original_path.stem}_{unique_id}"
    disk_filename = f"{disk_stem}{original_path.suffix}"
    saved_path = UPLOAD_DIR / disk_filename

    with saved_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    pdf_path = ""

    try:
        if ext == "pdf":
            pdf_path = str(saved_path)
        elif ext in ["docx", "pptx", "doc", "ppt"]:
            pdf_path = convert_document_to_pdf(str(saved_path), str(UPLOAD_DIR))
        elif ext in ["jpg", "jpeg", "png"]:
            pdf_path = str(UPLOAD_DIR / f"{disk_stem}.pdf")
            convert_image_to_pdf(str(saved_path), pdf_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")
            
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()
        
    except Exception as e:
        logger.error(f"Upload/Convert error: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

    return {
        "original_name": original_name, 
        "saved_path": str(saved_path), 
        "pdf_path": pdf_path,
        "page_count": page_count
    }

class PreviewRequest(BaseModel):
    files: List[str]

@router.post("/preview_all")
def preview_all_files(req: PreviewRequest):
    try:
        merged_doc = fitz.open()
        for pdf_path in req.files:
            if Path(pdf_path).exists():
                doc = fitz.open(pdf_path)
                merged_doc.insert_pdf(doc)
                doc.close()
                
        images = []
        for i in range(len(merged_doc)):
            page = merged_doc[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img_bytes = pix.tobytes("png")
            base64_str = base64.b64encode(img_bytes).decode("utf-8")
            images.append(f"data:image/png;base64,{base64_str}")
            
        merged_doc.close()
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_files(files: List[str] = Body(...)):
    deleted = 0
    for file_path in files:
        try:
            target = Path(file_path).resolve()
            if UPLOAD_DIR in target.parents:
                if target.exists():
                    target.unlink()
                    deleted += 1
        except Exception:
            pass
    return {"status": "success", "deleted_count": deleted}