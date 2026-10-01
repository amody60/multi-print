"""Convert image files (JPG/PNG) to a single-page PDF."""

from PIL import Image
from pathlib import Path

def convert_image_to_pdf(image_path: str, output_pdf_path: str) -> None:
    """Convert an image to a PDF file, preserving aspect ratio."""
    img = Image.open(image_path)
    
    # تحويل الصورة لـ RGB عشان نتجنب مشاكل الـ PNG الشفاف (RGBA) مع الـ PDF
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
        
    img.save(output_pdf_path, "PDF", resolution=100.0)