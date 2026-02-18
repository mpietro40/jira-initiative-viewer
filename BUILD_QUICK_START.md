# Quick Start - Build Initiative Viewer

## 🚀 Build the Executable (New Features!)

### Just run:
```batch
build_initiative_viewer.bat
```

Or:
```batch
python build_initiative_viewer.py
```

### What Happens:
1. ✓ Installs dependencies automatically
2. ✓ Detects next version (v1.0, v1.1, v1.2, etc.)
3. ✓ Builds with **favicon.ico** included
4. ✓ Creates versioned executable: `InitiativeViewer_v1.X.exe`

---

## ✨ New Features

### 1. Production WSGI Server (Waitress) 🚀
**Why:** Flask's development server isn't suitable for sharing with others

**Solution:** Switched to Waitress production server!
- ✅ Production-ready and thread-safe
- ✅ Handles multiple concurrent users
- ✅ Better performance and stability
- ✅ Up to 100 concurrent connections
- ✅ No "development server" warnings

### 2. Automatic Versioning
**Problem:** Build failed when app was running (file locked)

**Solution:** Each build creates a new version!
- First run: `InitiativeViewer_v1.0.exe`
- Second run: `InitiativeViewer_v1.1.exe` ✅ works even if v1.0 is running!
- Third run: `InitiativeViewer_v1.2.exe`

### 3. Favicon Included
**Problem:** Missing favicon.ico caused errors at startup

**Solution:** Now included from `static/favicon.ico`
- ✅ No more "favicon not found" errors
- ✅ Windows Explorer shows proper icon
- ✅ Professional appearance

---

## 📦 What You'll Get

### File: `dist/InitiativeViewer_v1.0.exe`
- **Size:** 30-50 MB (not 150-200 MB!)
- **Version:** Automatically numbered
- **Icon:** Included favicon
- **Server:** Waitress production WSGI server ⭐
- **Standalone:** No Python needed

---

## 🎯 Quick Commands

### Build New Version
```batch
cd C:\Users\a788055\GITREPO\JiraObeya\PerseusLeadTime
build_initiative_viewer.bat
```
Answer prompts:
- Clean build directories? → Type `y` or `n`

### View All Versions
```batch
dir dist\InitiativeViewer*.exe
```

### Run Latest Version
```batch
cd dist
InitiativeViewer_v1.2.exe
```
(Double-click in Windows Explorer or run from command line)

---

## 📋 Build Output Example

```
Initiative Viewer - Build Script
============================================================
✓ PyInstaller 6.19.0 is installed

------------------------------------------------------------
✓ Dependencies installed successfully

------------------------------------------------------------
Previous version found: 1.1
New version will be: 1.2

✓ Building version: 1.2

------------------------------------------------------------
Clean previous build directories? (y/n): y
✓ Cleaned build
✓ Cleaned __pycache__

============================================================
Building Initiative Viewer Executable v1.2
============================================================

💗 Found spec file: initiative_viewer.spec
✅ Found favicon: static/favicon.ico

Running PyInstaller...
[PyInstaller output...]

✅ Build completed successfully!
✅ Renamed to: InitiativeViewer_v1.2.exe

============================================================
Build Results - Version 1.2
============================================================
✅ Executable created: C:\...\dist\InitiativeViewer_v1.2.exe
  Version: 1.2
  Size: 42.3 MB
  Includes: favicon.ico
  Server: Waitress (production-ready) ⭐

To run the application:
  InitiativeViewer_v1.2.exe
  (Double-click or run from command line)
============================================================
```

---

## 🔄 Workflow Examples

### Scenario 1: App is Running, Need to Rebuild
```batch
# App v1.0 is running (can't overwrite)
python build_initiative_viewer.py

# → Creates v1.1 (no conflict!)
# → Both versions can coexist
```

### Scenario 2: Multiple Versions for Testing
```bash
dist/
├── InitiativeViewer_v1.0.exe  # Old stable version
├── InitiativeViewer_v1.1.exe  # Testing new features
└── InitiativeViewer_v1.2.exe  # Latest with bug fix
```
Keep multiple versions for A/B testing or rollback!

### Scenario 3: Clean Slate
```batch
# Remove old versions
rmdir /s /q dist

# Build fresh v1.0
python build_initiative_viewer.py
```

---

## 🐛 Troubleshooting

### Issue: "PyInstaller not found"
```batch
pip install pyinstaller
```

### Issue: "Favicon not found"
Check that `static/favicon.ico` exists:
```batch
dir static\favicon.ico
```

### Issue: Build errors
1. Upgrade tools:
```batch
python -m pip install --upgrade pip setuptools wheel
```

2. Install dependencies:
```batch
pip install -r requirements_initiative_viewer.txt
```

3. Try again:
```batch
build_initiative_viewer.bat
```

### Issue: Exe too large
The fixes already applied should make it 30-50 MB.
If still large, check [BUILD_FIX_README.md](BUILD_FIX_README.md).

---

## ✅ Verification

After building, verify:

### 1. File exists
```batch
dir dist\InitiativeViewer_v1.*.exe
```

### 2. Size is reasonable
Should be 30-50 MB (not 150+ MB)

### 3. Icon shows
Right-click exe → Properties → Should show your favicon

### 4. App runs
```batch
cd dist
InitiativeViewer_v1.0.exe --help
```
Should show help without errors

### 5. No favicon errors
When app starts, check console - no "favicon not found" messages

---

## 📝 Summary

**Before:**
- ❌ Build failed if app was running
- ❌ Missing favicon caused errors
- ❌ 150-200 MB exe size
- ❌ Included unused libraries
- ❌ Flask development server (not production-ready)

**After:**
- ✅ Automatic versioning (v1.0, v1.1, etc.)
- ✅ Favicon included (static/favicon.ico)
- ✅ 30-50 MB exe size (60-70% smaller!)
- ✅ Only necessary dependencies
- ✅ Build works even when app runs
- ✅ Professional appearance with icon
- ✅ **Waitress production server** - ready to share! 🚀

---

## 🎉 You're Ready!

Just run:
```batch
build_initiative_viewer.bat
```

The first build creates `v1.0`, next creates `v1.1`, and so on!

You can now build anytime without worrying about file conflicts! 🚀
