import sys
import os
import io
import pytest
from fastapi.testclient import TestClient

# إضافة مسار المشروع للـ Python Path عشان pytest يلاقي الباك-إند
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.printers.groups import get_next_printer_in_group
from backend.api.print_jobs import extract_pages_pdf
from backend.config.settings_store import load_settings, save_settings
import fitz

# 1. تهيئة عميل الاختبار (Test Client)
client = TestClient(app)

# ==========================================
# دوال مساعدة للاختبار
# ==========================================

def create_dummy_pdf_bytes():
    """إنشاء ملف PDF وهمي في الذاكرة لاستخدامه في الاختبارات"""
    doc = fitz.open()
    doc.new_page()
    byte_stream = io.BytesIO()
    doc.save(byte_stream)
    doc.close()
    byte_stream.seek(0)
    return byte_stream.getvalue()

# ==========================================
# اختبارات الـ API (Endpoints)
# ==========================================

def test_read_main():
    """اختبار إن الواجهة الأمامية بترجع 200 OK"""
    response = client.get("/")
    assert response.status_code == 200

def test_get_printers():
    """اختبار إن الـ API بيرجع الطابعات"""
    response = client.get("/api/printers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_groups():
    """اختبار إن الـ API بيرجع المجموعات"""
    response = client.get("/api/groups")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

# ==========================================
# اختبارات الأخطاء والاستثناءات (Edge Cases) 🚀
# ==========================================

def test_invalid_print_job_requests():
    """اختبار إن /api/print/job بيرجع أخطاء صح لما الطابعة أو المجموعة غلط"""
    
    # 1. لو مفيش printer_name ولا group_name (المفروض 400)
    payload_no_target = {"pdf_path": "dummy.pdf"}
    res_no_target = client.post("/api/print/job", json=payload_no_target)
    assert res_no_target.status_code == 400
    
    # 2. لو group_name مش موجود (المفروض 404)
    payload_fake_group = {
        "pdf_path": "dummy.pdf",
        "group_name": "Fake_Group_12345"
    }
    res_fake_group = client.post("/api/print/job", json=payload_fake_group)
    assert res_fake_group.status_code == 404

def test_file_name_collision_prevention():
    """اختبار إن رفع نفس الملف مرتين بيولّد اسمين مختلفين على الديسك (UUID)"""
    dummy_pdf_bytes = create_dummy_pdf_bytes()
    
    # رفع الملف أول مرة
    res1 = client.post(
        "/api/files/upload",
        files={"file": ("test_dup.pdf", dummy_pdf_bytes, "application/pdf")}
    )
    assert res1.status_code == 200
    data1 = res1.json()
    
    # رفع نفس الملف تاني مرة
    res2 = client.post(
        "/api/files/upload",
        files={"file": ("test_dup.pdf", dummy_pdf_bytes, "application/pdf")}
    )
    assert res2.status_code == 200
    data2 = res2.json()
    
    # التأكد إن الأسماء الأصلية زي بعض (test_dup.pdf)
    assert data1["original_name"] == data2["original_name"]
    
    # التأكد إن المسارات على الديسك مختلفة تماماً (بفضل UUID)
    assert data1["saved_path"] != data2["saved_path"]
    assert data1["pdf_path"] != data2["pdf_path"]
    
    # تنظيف الملفات اللي اتعملت في مجلد temp_uploads
    from backend.api.files import UPLOAD_DIR
    try:
        if os.path.exists(data1["saved_path"]): os.remove(data1["saved_path"])
        if os.path.exists(data1["pdf_path"]): os.remove(data1["pdf_path"])
        if os.path.exists(data2["saved_path"]): os.remove(data2["saved_path"])
        if os.path.exists(data2["pdf_path"]): os.remove(data2["pdf_path"])
    except Exception:
        pass

# ==========================================
# اختبارات المنطق الأساسي (Business Logic)
# ==========================================

def test_round_robin_logic():
    """اختبار خوارزمية توزيع الأعباء (Round-Robin)"""
    original_settings = load_settings()
    
    test_group_name = "Test_Group_Temp"
    save_settings({"printer_groups": {test_group_name: {"printers": ["Printer1", "Printer2"], "last_used_index": 0}}})
    
    p1 = get_next_printer_in_group(test_group_name)
    assert p1 == "Printer1"
    
    p2 = get_next_printer_in_group(test_group_name)
    assert p2 == "Printer2"
    
    p3 = get_next_printer_in_group(test_group_name)
    assert p3 == "Printer1"
    
    save_settings(original_settings)

def test_extract_pages_pdf():
    """اختبار دالة استخراج الصفحات (Page Range)"""
    import tempfile
    temp_dir = tempfile.gettempdir()
    dummy_pdf = os.path.join(temp_dir, "dummy_test.pdf")
    doc = fitz.open()
    for _ in range(5):
        doc.new_page()
    doc.save(dummy_pdf)
    doc.close()
    
    extracted_path, count = extract_pages_pdf(dummy_pdf, "2-3")
    assert count == 2
    
    extracted_path2, count2 = extract_pages_pdf(dummy_pdf, "5")
    assert count2 == 1
    
    extracted_path3, count3 = extract_pages_pdf(dummy_pdf, "10-20")
    assert count3 == 0
    
    os.remove(dummy_pdf)
    if os.path.exists(extracted_path): os.remove(extracted_path)
    if os.path.exists(extracted_path2): os.remove(extracted_path2)