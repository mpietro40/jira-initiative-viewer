# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Initiative Viewer
Creates a standalone Windows executable with all dependencies
"""
import sys
import os

block_cipher = None

# Get the path to the script directory
script_dir = os.path.dirname(os.path.abspath('initiative_viewer.py'))

a = Analysis(
    ['initiative_viewer.py'],
    pathex=[script_dir],
    binaries=[],
    datas=[
        # Include templates
        ('templates', 'templates'),
        # Include static files
        ('static', 'static'),
    ],
    hiddenimports=[
        # Flask and web framework
        'flask',
        'werkzeug.security',
        'werkzeug.serving',
        'jinja2',
        'markupsafe',
        'itsdangerous',
        'click',
        'blinker',
        
        # Waitress WSGI server
        'waitress',
        'waitress.server',
        'waitress.task',
        'waitress.adjustments',
        'waitress.channel',
        'waitress.utilities',
        
        # HTTP and API
        'requests',
        'urllib3',
        'charset_normalizer',
        'certifi',
        'idna',
        
        # PDF generation
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.colors',
        'reportlab.lib.pagesizes',
        'reportlab.lib.styles',
        'reportlab.lib.units',
        'reportlab.lib.enums',
        'reportlab.platypus',
        'reportlab.graphics',
        'reportlab.graphics.shapes',
        'reportlab.graphics.charts',
        'reportlab.graphics.charts.barcharts',
        'reportlab.graphics.charts.piecharts',
        
        # Pillow (reportlab dependency)
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Testing frameworks
        'pytest',
        'pytest-flask',
        'unittest',
        'nose',
        'coverage',
        
        # Heavy libraries not used
        'pandas',
        'numpy',
        'scipy',
        'matplotlib',
        'seaborn',
        'bokeh',
        'plotly',
        
        # Development tools
        'IPython',
        'jupyter',
        'notebook',
        
        # Other unused
        'tkinter',
        'turtle',
        'test',
        'asyncio',
        'multiprocessing',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
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
    name='InitiativeViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console for logs and output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/favicon.ico',  # Application icon
)
