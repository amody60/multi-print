# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs

block_cipher = None
ROOT_DIR = os.path.abspath('.')

# ✅ رقم النسخة (غيره كل مرة تعمل ابديت)
APP_VERSION = "1.0.3"

hiddenimports = [
    'win32print',
    'win32api',
    'win32con',
    'pywintypes',
    'pythoncom',
    'fitz',
    'PIL',
    'uvicorn.logging',
    'uvicorn.loops.auto',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets.auto', # ✅ تم إصلاح اسم المكتبة هنا
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
]

hiddenimports += collect_submodules('webview')
hiddenimports += collect_submodules('backend')

pywin32_dlls = collect_dynamic_libs('pywin32')

a = Analysis(
    ['backend/main.py'],
    pathex=[ROOT_DIR],
    binaries=pywin32_dlls,
    datas=[
        # بنضم مجلد الواجهة (HTML, CSS, JS)
        ('frontend', 'frontend'),
        # ✅ بنضم أداة الطباعة SumatraPDF.exe فقط (مش محتاجين LibreOffice هنا)
        ('backend/resources/bin/SumatraPDF.exe', 'backend/resources/bin'),
        ('backend/resources/bin/SumatraPDF-settings.txt', 'backend/resources/bin')
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ✅ وضع البرنامج في فولدر باسم النسخة (dist/1.0.3)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MultiPrint',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='app_icon.ico'  # تأكد إنك حاطط أيقونة في المسار ده
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=APP_VERSION,
    upx=True,
    upx_exclude=[],
    strip=False
)