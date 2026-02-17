# Initiative Viewer - Windows Executable Deployment Guide

## Overview
This guide explains how to build and deploy the Initiative Viewer as a standalone Windows executable that includes Python and all dependencies.

## Prerequisites

### For Building the Executable:
- **Python 3.8 or higher** installed on the build machine
- **Virtual environment** (recommended): `Obeya` folder with activated environment
- **Internet connection** for downloading dependencies

## Building the Executable

### Option 1: Quick Build (Recommended)
Simply double-click or run from command prompt:
```batch
build_initiative_viewer.bat
```

This will:
1. Activate the virtual environment (if available)
2. Install/check all dependencies
3. Build the executable using PyInstaller
4. Show the location of the generated executable

### Option 2: Manual Build
```batch
# 1. Activate virtual environment (if using one)
..\Obeya\Scripts\activate.bat

# 2. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# 3. Run the build script
python build_initiative_viewer.py

# Or build directly with PyInstaller
pyinstaller initiative_viewer.spec --noconfirm --clean
```

## Build Output

After successful build, you'll find:
- **Executable**: `dist\InitiativeViewer.exe` (~150-200 MB)
- **Build artifacts**: `build\` folder (can be deleted)

The executable is **completely standalone** and includes:
- Python interpreter
- Flask web framework
- All required libraries (pandas, numpy, matplotlib, reportlab, etc.)
- Templates and static files
- All application code

## Distributing the Executable

### What to Include:
1. **InitiativeViewer.exe** - The main executable
2. **Usage instructions** - See below

### What Users Need:
- **Nothing!** The executable is completely self-contained
- No Python installation required
- No dependencies to install
- Just a Windows machine (Windows 10/11 recommended)

## Running the Executable

### Simple Usage (Recommended):
Just **double-click** `InitiativeViewer.exe`!

That's it! The application will:
1. ✓ Start the web server
2. ✓ Automatically open your web browser
3. ✓ Show you a form to enter your Jira details

### Alternative: Command Line:
```batch
InitiativeViewer.exe
```

Or specify a different port:
```batch
InitiativeViewer.exe --port 8080
```

### Optional Command Line Arguments:
- `--port` (optional): Port to run the web server (default: 5001)
- `--cached` (optional): Use cached data from previous analysis
- `--no-browser` (optional): Don't automatically open the browser

### Getting a Jira API Token:
1. Log in to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name (e.g., "Initiative Viewer")
4. Copy and save the token securely

## Using the Application

1. **Start the application** by double-clicking `InitiativeViewer.exe`
2. **Your browser opens automatically** showing the configuration form
3. **Fill in the form:**
   - Jira URL (e.g., https://jira.company.com)
   - API Token (get from https://id.atlassian.com/manage-profile/security/api-tokens)
   - JQL Query (e.g., `project = PROJ AND type = "Business Initiative"`)
   - Fix Version
4. **Click "Analyze"** to fetch and analyze the initiatives
5. **View the hierarchy** - explore Business Initiatives → Features → Sub-Features → Epics
6. **Generate PDF** - click the PDF button to create a report
7. **Stop the application** - Close the console window or press Ctrl+C

## Features Included in the Executable

### ✓ Full Initiative Hierarchy Analysis
- Business Initiative → Feature → Sub-Feature → Epic structure
- Risk probability color coding
- Area-based organization
- Status tracking

### ✓ PDF Report Generation
- Complete hierarchy documentation
- Export for stakeholder review
- Professional formatting

### ✓ Backward Check Analysis
- Dependency validation
- Epic-to-initiative mapping verification

### ✓ Caching Support
- Fast re-analysis of previously fetched data
- Reduces Jira API calls

## Troubleshooting

### Build Issues

**Problem**: `ModuleNotFoundError` during build
**Solution**: Install missing dependencies:
```batch
pip install -r requirements.txt
```

**Problem**: Build takes too long or fails with memory error
**Solution**: Close other applications and try again. Building can use 2-4 GB of RAM.

**Problem**: PyInstaller not found
**Solution**: Install PyInstaller:
```batch
pip install pyinstaller
```

### Runtime Issues

**Problem**: Executable won't start or crashes immediately
**Solution**: 
- Run from command prompt to see error messages
- Check if antivirus is blocking the executable
- Try running as administrator

**Problem**: "Cannot connect to Jira"
**Solution**:
- Verify Jira URL is correct (include https://)
- Check API token is valid
- Ensure you have network connectivity
- Check if firewall is blocking the connection

**Problem**: "Port already in use"
**Solution**: Either:
- Close the application using that port
- Or use a different port: `--port 5200`

**Problem**: Web page won't load
**Solution**:
- Wait 10-15 seconds after starting for the server to fully initialize
- Check the console for "Running on http://..." message
- Try accessing http://127.0.0.1:5100 instead of localhost

### Performance Issues

**Problem**: Analysis is slow
**Solution**:
- Reduce `--max-results` to analyze fewer initiatives
- Use more specific JQL to target specific initiatives
- Cached results will be faster on subsequent runs

**Problem**: Executable is very large (>300 MB)
**Solution**: This is normal. The executable includes:
- Python runtime (~50 MB)
- NumPy/Pandas (~80 MB)
- Matplotlib (~40 MB)
- Other libraries and dependencies

## Advanced Configuration

### Using a Different Port:
```batch
InitiativeViewer.exe --port 8080
```

### Using Cached Data (faster re-analysis):
```batch
InitiativeViewer.exe --cached
```

### Running Without Auto-Opening Browser:
```batch
InitiativeViewer.exe --no-browser
```
Then manually navigate to `http://localhost:5001`

### Combining Options:
```batch
InitiativeViewer.exe --port 8080 --cached --no-browser
```

### Security Considerations

⚠️ **Important Security Notes:**

1. **API Token**: Never share your Jira API token or commit it to version control
2. **Web Interface**: API tokens are entered via the secure web form, not exposed in command line
3. **Session Data**: Tokens are stored temporarily in session and not persisted to disk
4. **Logs**: Check logs for sensitive information before sharing
5. **Distribution**: Only distribute the executable to trusted users
6. **Local Network**: The server binds to 0.0.0.0, meaning it's accessible on your local network. For security, only run on trusted networks.

## File Structure

```
PerseusLeadTime/
├── initiative_viewer.py          # Main application code
├── initiative_viewer.spec        # PyInstaller configuration
├── build_initiative_viewer.py    # Build script
├── build_initiative_viewer.bat   # Windows build wrapper
├── requirements.txt              # Python dependencies
├── templates/                    # HTML templates (bundled)
│   └── initiative_hierarchy.html
├── static/                       # Static assets (bundled)
│   ├── logo.png
│   └── favicon.ico
├── build/                        # Build artifacts (generated)
└── dist/                         # Output directory (generated)
    └── InitiativeViewer.exe      # Final executable
```

## Support and Updates

### Rebuilding After Code Changes:
1. Make your changes to `initiative_viewer.py` or related files
2. Run `build_initiative_viewer.bat` again
3. Distribute the new `InitiativeViewer.exe`

### Version Control:
- **Include in Git**: `.py`, `.spec`, `.bat`, `.txt` files
- **Exclude from Git**: `build/`, `dist/`, `__pycache__/`, `*.pyc`

### Adding Dependencies:
1. Add to `requirements.txt`
2. Add to `hiddenimports` in `initiative_viewer.spec` (if needed)
3. Rebuild the executable

## FAQ

**Q: Can users run this without admin rights?**
A: Yes, the executable doesn't require administrator privileges.

**Q: Do I need to memorize complex command line arguments?**
A: No! Just double-click the executable. All settings are entered via the web form.

**Q: Does it work on older Windows versions?**
A: Tested on Windows 10/11. May work on Windows 8.1 with updates.

**Q: Can I create a desktop shortcut?**
A: Yes! Right-click `InitiativeViewer.exe` → Send to → Desktop (create shortcut).
   Then just double-click the shortcut to start.

**Q: How do I update the application?**
A: Simply rebuild with the new code and replace the old executable.

**Q: Can I customize the appearance?**
A: Yes, modify the HTML templates and rebuild. Templates are bundled into the executable.

**Q: How much disk space is needed?**
A: ~200 MB for the executable, plus temporary space for cache and PDFs (~100 MB).

**Q: Can multiple users run it simultaneously?**
A: Yes, but each needs their own copy running on a different port (use `--port` argument).

**Q: My browser didn't open automatically. What should I do?**
A: Just open your browser manually and go to `http://localhost:5001`

## Contact

For issues or questions about the Initiative Viewer:
- Check the main application logs for error messages
- Review this guide for troubleshooting steps
- Check Jira connectivity and API token validity

---

**Last Updated**: February 2026
**Application Version**: Initiative Viewer with PyInstaller
**Author**: Pietro Maffi
