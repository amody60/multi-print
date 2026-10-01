"""Print Jobs API endpoints."""

import math
import os
import time
import fitz  # PyMuPDF
import win32print
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Optional

from backend.printers.print_queue import print_pdf_file
from backend.printers.groups import get_next_printer_in_group
from backend.compose.n_up import compose_n_up
from backend.config.history_store import add_history_item
from backend.config.settings_store import load_settings
from backend.config.logger import logger

router = APIRouter(prefix="/api/print", tags=["print"])

def wait_for_printer_ready(printer_name: str, max_jobs: int = 3):
    """
    تنتظر الطابعة حتى يقل الضغط عليها في طابور الويندوز
    عشان نتجنب رفض الطابعة للملفات الكبيرة صامتة.
    """
    try:
        handle = win32print.OpenPrinter(printer_name)
        while True:
            jobs = win32print.EnumJobs(handle, 0, -1, 1)
            if len(jobs) < max_jobs:
                break
            logger.info(f"Printer {printer_name} is busy ({len(jobs)} jobs). Waiting 2 seconds...")
            time.sleep(2)
        win32print.ClosePrinter(handle)
    except Exception as e:
        logger.warning(f"Couldn't check printer queue: {e}")

class PrintRequest(BaseModel):
    pdf_path: str
    original_name: str = "Unknown"
    printer_name: Optional[str] = None
    group_name: Optional[str] = None
    n_up: int = 1
    duplex: bool = False
    color: bool = True
    copies: int = 1
    orientation: str = "portrait"
    page_range: Optional[str] = None

def extract_pages_pdf(original_path: str, range_str: str) -> tuple[str, int]:
    try:
        doc = fitz.open(original_path)
        new_doc = fitz.open()
        parts = range_str.replace(' ', '').split(',')
        pages_extracted = 0
        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                for i in range(int(start)-1, int(end)):
                    if 0 <= i < len(doc):
                        new_doc.insert_pdf(doc, from_page=i, to_page=i)
                        pages_extracted += 1
            else:
                i = int(part) - 1
                if 0 <= i < len(doc):
                    new_doc.insert_pdf(doc, from_page=i, to_page=i)
                    pages_extracted += 1
        temp_path = original_path.replace(".pdf", f"_range_{hash(range_str)}.pdf")
        new_doc.save(temp_path)
        new_doc.close()
        doc.close()
        return temp_path, pages_extracted
    except Exception as e:
        logger.error(f"Page range extraction failed: {e}")
        return original_path, 0

@router.post("/job")
def start_print_job(req: PrintRequest) -> dict[str, Any]:
    target_printer = req.printer_name
    if req.group_name:
        target_printer = get_next_printer_in_group(req.group_name)
        if not target_printer:
            raise HTTPException(status_code=404, detail=f"المجموعة '{req.group_name}' غير موجودة.")
    if not target_printer:
        raise HTTPException(status_code=400, detail="يجب اختيار طابعة.")

    try:
        actual_pdf_to_print = req.pdf_path
        original_pages = 0
        files_to_clean = []

        if req.page_range:
            actual_pdf_to_print, original_pages = extract_pages_pdf(req.pdf_path, req.page_range)
            files_to_clean.append(actual_pdf_to_print)
            if original_pages == 0:
                raise HTTPException(status_code=400, detail="نطاق الصفحات خاطئ.")
        else:
            src_doc = fitz.open(req.pdf_path)
            original_pages = len(src_doc)
            src_doc.close()

        # 1. دمج الـ N-up واتجاه الورق في خطوة واحدة عشان مفيش هوامش بيضا
        if req.n_up > 1 or req.orientation == "landscape":
            nup_pdf_path = actual_pdf_to_print.replace(".pdf", f"_proc_{req.n_up}_{req.orientation}.pdf")
            compose_n_up(actual_pdf_to_print, nup_pdf_path, req.n_up, req.orientation)
            actual_pdf_to_print = nup_pdf_path
            files_to_clean.append(actual_pdf_to_print)

        sheets = math.ceil(original_pages / req.n_up)
        if req.duplex:
            sheets = math.ceil(sheets / 2)
        total_sheets = sheets * req.copies
        saved_sheets = (original_pages * req.copies) - total_sheets

        wait_for_printer_ready(target_printer)
        
        # 2. محاولة الطباعة على الطابعة الأساسية
        print_result = print_pdf_file(
            pdf_path=actual_pdf_to_print,
            printer_name=target_printer,
            duplex=req.duplex,
            color=req.color,
            copies=req.copies,
            orientation=req.orientation
        )
        
        # 3. لو الأساسية فشلت، نبحث عن الاحتياطية (Failover)
        if not print_result["success"]:
            settings = load_settings()
            fallback_printer = settings.get("fallback_printer")
            
            if fallback_printer and fallback_printer != target_printer:
                logger.warning(f"Primary printer '{target_printer}' failed. Failing over to '{fallback_printer}'.")
                wait_for_printer_ready(fallback_printer)
                
                print_result = print_pdf_file(
                    pdf_path=actual_pdf_to_print,
                    printer_name=fallback_printer,
                    duplex=req.duplex,
                    color=req.color,
                    copies=req.copies,
                    orientation=req.orientation
                )
                
                if print_result["success"]:
                    target_printer = fallback_printer  # تحديث اسم الطابعة للتقرير والسجل
                else:
                    raise HTTPException(status_code=500, detail=f"فشلت الطباعة على الطابعة الأساسية والاحتياطية. السبب: {print_result.get('error')}")
            else:
                # لو مفيش طابعة احتياطية أو هي نفسها اللي وقعت
                raise HTTPException(status_code=500, detail=print_result.get("error", "فشل الطباعة."))
        
        # 4. لو الطباعة نجحت (سواء على الأساسية أو الاحتياطية)
        add_history_item({
            "file_name": req.original_name,
            "printer": target_printer,
            "pages": original_pages,
            "sheets": total_sheets,
            "copies": req.copies,
            "duplex": req.duplex,
            "color": req.color
        })
        
        # ✅ تنظيف الملفات المؤقتة المشتقة (N-up, Landscape, Range) بعد الطباعة
        for f in files_to_clean:
            try:
                if os.path.exists(f): os.remove(f)
            except Exception: pass
            
        return {
            "status": "success", 
            "message": f"File sent to {target_printer}",
            "report": {
                "printer_used": target_printer,
                "original_pages": original_pages,
                "printed_sheets": total_sheets,
                "saved_sheets": saved_sheets
            }
        }
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Job Error: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في معالجة الملف. برجاء مراجعة log.txt")