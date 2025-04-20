# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mainmodule.py'],
    pathex=[],
    binaries=[],
    datas=[
        # ('data/icon.ico', 'data/modules/infomodule.py', 'data/modules/keymodule.py', 'data/windows/mainwindow.py', 'data/windows/workspace.py')
    ],
    hiddenimports=[
        'Crypto',
        'Crypto.Hash',
        'Crypto.Cipher',
        'psutil',
        'uuid',
        'platform',
        'subprocess'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='FileEncryptor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='data/icon.ico',
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
