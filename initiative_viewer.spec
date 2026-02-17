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
        
        # HTTP and API
        'requests',
        'urllib3',
        
        # Data processing
        'pandas',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.skiplist',
        'numpy',
        'scipy',
        'scipy.special',
        'scipy.special._ufuncs_cxx',
        
        # Date/time
        'datetime',
        'dateutil',
        'pytz',
        
        # PDF generation
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'reportlab.lib.colors',
        'reportlab.lib.pagesizes',
        'reportlab.platypus',
        'reportlab.graphics',
        'reportlab.graphics.shapes',
        'reportlab.graphics.charts',
        'reportlab.graphics.charts.barcharts',
        
        # Visualization
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends',
        'matplotlib.backends.backend_agg',
        'seaborn',
        
        # Standard library
        'logging',
        'typing',
        'collections',
        'pickle',
        'tempfile',
        'uuid',
        'argparse',
        'io',
        're',
        'json',
        'csv',
        'threading',
        'time',
        'html',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytest',
        'pytest-flask',
        'unittest',
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
    icon=None,  # Add icon path if you have one: 'static/favicon.ico'
)
