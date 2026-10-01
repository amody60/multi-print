"""Compose N-up PDF layouts (2, 4, 6, 8, 10 pages per sheet)."""
import fitz  # PyMuPDF

A4_W = 595.27
A4_H = 841.89

LAYOUTS = {
    2: (2, 1),
    4: (2, 2),
    6: (3, 2),
    8: (4, 2),
    10: (5, 2)
}

def compose_n_up(input_pdf_path: str, output_pdf_path: str, n_up: int = 1, orientation: str = "portrait") -> None:
    # لو مفيش تركيب والورق طولي، انسخ الملف زي ما هو
    if n_up == 1 and orientation == "portrait":
        src_doc = fitz.open(input_pdf_path)
        src_doc.save(output_pdf_path)
        src_doc.close()
        return

    cols, rows = LAYOUTS.get(n_up, (1, 1))
    
    src_doc = fitz.open(input_pdf_path)
    dst_doc = fitz.open()
    
    # تحديد مقاس الورقة بناءً على الاتجاه
    if orientation == "landscape":
        page_width, page_height = A4_H, A4_W
    else:
        page_width, page_height = A4_W, A4_H

    MARGIN = 20
    cell_w = (page_width - MARGIN * (cols + 1)) / cols
    cell_h = (page_height - MARGIN * (rows + 1)) / rows

    for i in range(0, len(src_doc), n_up):
        new_page = dst_doc.new_page(width=page_width, height=page_height)
        for j in range(n_up):
            if i + j < len(src_doc):
                src_page = src_doc[i + j]
                row_idx = j // cols
                col_idx = j % cols
                x0 = MARGIN + col_idx * (cell_w + MARGIN)
                y0 = MARGIN + row_idx * (cell_h + MARGIN)
                target_rect = fitz.Rect(x0, y0, x0 + cell_w, y0 + cell_h)
                new_page.show_pdf_page(target_rect, src_doc, i + j, keep_proportion=True)
                
    dst_doc.save(output_pdf_path)
    dst_doc.close()
    src_doc.close()