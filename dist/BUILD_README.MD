# Build Fix - Initiative Viewer Executable

## Recent Updates ⭐

### Version 1.1 Features (February 2026)
1. **Automatic Versioning** - Prevents build failures when exe is running
   - First build creates: `InitiativeViewer_v1.0.exe`
   - Next build creates: `InitiativeViewer_v1.1.exe`
   - Keeps all versions in `dist/` folder
   
2. **Favicon Included** - No more startup errors
   - Application icon: `static/favicon.ico`
   - Windows Explorer shows proper icon
   - No missing favicon warnings in logs

---

## Problem Fixed

### Issue 1: Pandas Build Error ❌
**Error:** `Failed to build 'pandas' when getting requirements to build wheel`

**Root Cause:** 
- The spec file included pandas, numpy, scipy, matplotlib, and seaborn
- These libraries are NOT used by Initiative Viewer
- Pandas requires C++ build tools which may not be installed

**Solution:** ✅
- Removed all unused heavy dependencies from spec file
- Application only needs: Flask, requests, reportlab, Pillow

### Issue 2: Huge Executable Size 📦
**Problem:** Executable was 150-200+ MB

**Root Cause:**
- pandas (~50 MB)
- numpy (~30 MB)  
- scipy (~40 MB)
- matplotlib (~30 MB)
- seaborn (~20 MB)
- **Total unnecessary:** ~170 MB of unused libraries!

**Solution:** ✅
- Removed all unused dependencies
- **Expected new size:** 30-50 MB (60-70% reduction!)
- Enabled UPX compression for further size reduction

---

## What Was Changed

### 1. `initiative_viewer.spec` 
**Removed from hiddenimports:**
- ❌ pandas (and all pandas.\_libs.*)
- ❌ numpy
- ❌ scipy (and scipy.special.*)
- ❌ matplotlib (and matplotlib.*)
- ❌ seaborn
- ❌ dateutil, pytz (not used)

**Added to excludes:**
- All the above libraries
- Testing frameworks (pytest, nose, coverage)
- Development tools (jupyter, IPython)
- Unused stdlib modules (tkinter, turtle, asyncio, multiprocessing)

**Kept (actually needed):**
- ✅ Flask + dependencies
- ✅ requests
- ✅ reportlab (for PDF generation)
- ✅ Pillow (reportlab dependency)

### 2. `requirements_initiative_viewer.txt`
**Added:**
- Pillow>=10.0.0 (required by reportlab)

### 3. `build_initiative_viewer.py`
**Improved:**
- Added automatic dependency installation before build
- Better error messages
- Dependency verification
- **Automatic version increment** ⭐ NEW
- **Preserves previous executables** ⭐ NEW
- **Detects next available version** (1.0 → 1.1 → 1.2, etc.)

### 4. `build_initiative_viewer.bat`

## How to Build (Fixed Version)

### Option 1: Using Batch File (Recommended)
```batch
cd C:\Users\a788055\GITREPO\JiraObeya\PerseusLeadTime
build_initiative_viewer.bat
```

### Option 2: Using Python Directly
```batch
cd C:\Users\a788055\GITREPO\JiraObeya\PerseusLeadTime
python build_initiative_viewer.py
```

### B**Detects next version number** (1.0, 1.1, 1.2, etc.)
4. ✓ Asks if you want to clean previous builds
5. ✓ Builds executable using PyInstaller with favicon
6. ✓ **Renames to versioned name** (InitiativeViewer_v1.1.exe)
7. ✓ Installs/updates dependencies (Flask, requests, reportlab, Pillow)
3. ✓ Asks if you want to clean previous builds
4. ✓ Builds executable using PyInstaller
5. ✓ Shows result and file size

---

## Expected Results

### Before Fix:
- ❌ Build failed with pandas error
- 📦 Size: 150-200+ MB (if it worked)
- ⏱️ Build time: 10-15 minutes
- ⚠️ Many unnecessary dependencies

### After Fix:
- ✅ Build succeeds without errors
- 📦 Size: **30-50 MB** (60-70%
- 🎯 **Automatic versioning** - Build works even if app is running
- 🖼️ **Includes favicon** - No missing icon errors smaller!)
- ⏱️ Build time: **2-5 minutes** (much faster!)
- ✅ Only necessary dependencies

---

## What Your Application Actually Uses

Based on code analysis:

### `initiative_viewer.py`
- Flask (web framework)
- requests (Jira API)
- Standard library (logging, typing, collections, pickle, etc.)

### `initiative_viewer_pdf.py`
- reportlab (PDF generation)
- reportlab.graphics.charts (bar charts, pie charts)

### `jira_client.py`
- requests (HTTP client)
- Standard library

### `backward_check_analyzer.py`
- Standard library only

**Conclusion:** No pandas, numpy, scipy, matplotlib, or seaborn anywhere! 🎉

---

## Verification Steps

After building, verify the fix:

### 1. Check Build Succes*.exe
```
Should show the versioned exe file (e.g., InitiativeViewer_v1.0.exe).

### 2. Check File Size
The file should be **30-50 MB** instead of 150-200 MB.

### 3. Check Version
Each build increments: v1.0 → v1.1 → v1.2, etc.

### 4. Test the Application
```batch
cd dist
InitiativeViewer_v1.0
cd dist
InitiativeViewer.exe --help
```
Should show help message without errors.
_v1.0.exe --jira-url https://your-jira.com --email your@email.com --token YOUR_TOKEN --jql "project = TEST"
```
Should open browser and work as before. No favicon warnings in console!

---

## Versioning System

### How It Works:
1. **First build**: Creates `InitiativeViewer_v1.0.exe`
2. **Second build**: Creates `InitiativeViewer_v1.1.exe` (even if v1.0 is running!)
3. **Third build**: Creates `InitiativeViewer_v1.2.exe`
4. **And so on...**

### Benefits:
- ✅ **No conflicts** - Build works even when app is running
- ✅ **Version history** - Keep multiple versions for testing
- ✅ **Easy rollback** - Can use older version if needed
- ✅ **Clear identification** - Know which version you're using

### Example `dist/` folder after multiple builds:
```
dist/
├── InitiativeViewer_v1.0.exe  (45 MB)
├── InitiativeViewer_v1.1.exe  (43 MB) 
└── InitiativeViewer_v1.2.exe  (44 MB) ← Latest
InitiativeViewer.exe --jira-url https://your-jira.com --email your@email.com --token YOUR_TOKEN --jql "project = TEST"
```
Should open browser and work as before.

---

## Troubleshooting

### If build still fails:

**1. Upgrade pip and tools:**
```batch
python -m pip install --upgrade pip setuptools wheel
```

**2. Install dependencies manually:**
```batch
pip install Flask==3.0.0 requests==2.31.0 Werkzeug==3.0.1 reportlab==4.0.4 Pillow
```

**3. Install PyInstaller:**
```batch
✅ **Automatic versioning** - Build while app runs ⭐  
✅ **Favicon included** - No missing icon errors ⭐

**The application has the same functionality, just without the bloat!** 🚀

---

## Additional Notes

### Cleaning Old Versions
If you want to remove old versions from `dist/`:
```batch
cd dist
del InitiativeViewer_v1.0.exe
del InitiativeViewer_v1.1.exe
```
(Keep the latest version only)

### Distributing to Users
- Give them the **latest version** (highest number)
- Example: `InitiativeViewer_v1.2.exe`
- They can rename it to just `InitiativeViewer.exe` if preferred

### Version Naming
The version in the filename is **build version**, not application version.
- It's automatically incremented by the build script
- It prevents file conflicts during development
- For application version, see the app's internal version (if you add one later)

**4. Clean and rebuild:**
```batch
rmdir /s /q build dist
python build_initiative_viewer.py
```

### If executable is still large:

Check what's included:
```batch
python -m PyInstaller --log-level=DEBUG initiative_viewer.spec > build.log 2>&1
```
Then check `build.log` for what's being bundled.

---

## Summary

✅ **Removed 170+ MB of unused libraries**  
✅ **Fixed pandas build error**  
✅ **Build now works without C++ build tools**  
✅ **Faster build times**  
✅ **Smaller, cleaner executable**  

**The application has the same functionality, just without the bloat!** 🚀
