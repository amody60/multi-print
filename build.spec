# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_dynamic_libs

block_cipher = None
ROOT_DIR = os.path.abspath('.')

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
    'uvicorn.protocols.websockets.autoimpl',
    'uvicorn.lifespan.on',
    'uvicorn.lifespan.off',
]

hiddenimports += collect_submodules('webview')
hiddenimports += collect_submodules('backend')

# إجبار PyInstaller يجلب كل ملفات DLL بتاعة pywin32
pywin32_dlls = collect_dynamic_libs('pywin32')

a = Analysis(
    ['backend/main.py'],
    pathex=[ROOT_DIR],
    binaries=pywin32_dlls,
    datas=[
        ('frontend', 'frontend'),
        ('backend/resources/bin', 'backend/resources/bin')
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MultiPrint',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
      # يطلب صلاحيات المسؤول دائماً
)