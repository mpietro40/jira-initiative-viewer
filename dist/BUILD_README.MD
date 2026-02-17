=============================================================================
        INITIATIVE VIEWER - EXECUTABLE BUILD & DEPLOYMENT
                    Documentation Index
=============================================================================

This folder contains everything you need to build and distribute the
Initiative Viewer as a standalone Windows executable.

=============================================================================
📖 DOCUMENTATION FILES (READ THESE)
=============================================================================

1. 📘 HOW_TO_BUILD_EXECUTABLE.txt
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   READ THIS FIRST!
   
   Step-by-step instructions to BUILD the executable
   • Prerequisites checklist
   • Easiest method: Double-click build_initiative_viewer.bat
   • Manual build method
   • Troubleshooting build problems
   
   👉 Start here if you need to CREATE InitiativeViewer.exe


2. 📗 QUICK_START_EXECUTABLE.txt
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FOR END USERS
   
   Simple instructions for USING the executable
   • How to run: Just double-click InitiativeViewer.exe
   • How to get Jira API token
   • Example JQL queries
   • Troubleshooting runtime issues
   
   👉 Give this file to users who will RUN the application


3. 📕 DEPLOYMENT_GUIDE.md
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   COMPLETE REFERENCE
   
   Comprehensive documentation covering everything:
   • Building the executable
   • Distributing to users
   • Security considerations
   • Advanced configuration
   • FAQ
   
   👉 Read this for complete details and advanced topics

=============================================================================
🔧 BUILD FILES (USE THESE)
=============================================================================

1. ⚡ build_initiative_viewer.bat
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   QUICKEST WAY TO BUILD!
   
   Just double-click this file to build the executable
   It handles everything automatically
   
   👉 This is the easiest build method


2. 🐍 build_initiative_viewer.py
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Python build script
   
   Automated build script with progress messages
   Can be run directly: python build_initiative_viewer.py
   
   👉 Alternative to the .bat file


3. ⚙️ initiative_viewer.spec
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PyInstaller configuration
   
   Defines what gets bundled into the executable
   • All Python dependencies
   • Templates and static files
   • Hidden imports
   
   👉 Advanced users can customize this file

=============================================================================
📦 WHAT YOU'LL GET
=============================================================================

After running the build, you'll find:

📁 dist/
  └─ 📄 InitiativeViewer.exe  ← THE EXECUTABLE (distribute this!)
  
📁 build/
  └─ (temporary build files - can be deleted)

=============================================================================
🚀 QUICK START
=============================================================================

FOR BUILDERS (Creating the executable):
────────────────────────────────────────
1. Read: HOW_TO_BUILD_EXECUTABLE.txt
2. Double-click: build_initiative_viewer.bat
3. Wait 2-5 minutes for the build to complete
4. Find executable in: dist\InitiativeViewer.exe
5. Test it!


FOR END USERS (Using the executable):
──────────────────────────────────────
1. Read: QUICK_START_EXECUTABLE.txt
2. Double-click: InitiativeViewer.exe
3. Fill in the web form that opens in your browser
4. Click "Analyze"
5. View your results!

=============================================================================
💡 TYPICAL WORKFLOW
=============================================================================

As a Developer/Builder:
───────────────────────
1. Make code changes to initiative_viewer.py
2. Test locally: python initiative_viewer.py
3. When ready to distribute:
   • Double-click build_initiative_viewer.bat
   • Wait for build to complete
   • Test the executable in dist/InitiativeViewer.exe
4. Distribute:
   • Copy dist/InitiativeViewer.exe to users
   • Include QUICK_START_EXECUTABLE.txt for instructions


As an End User:
────────────────
1. Receive InitiativeViewer.exe (and QUICK_START_EXECUTABLE.txt)
2. Place it in any folder
3. Double-click to run
4. Browser opens automatically with a form
5. Enter your Jira details and click Analyze
6. Done! View your initiative hierarchy

=============================================================================
❓ WHICH FILE DO I NEED?
=============================================================================

Question: "How do I build the executable?"
Answer: → Read HOW_TO_BUILD_EXECUTABLE.txt
        → Then run build_initiative_viewer.bat

Question: "How do I use the executable?"
Answer: → Read QUICK_START_EXECUTABLE.txt
        → Then double-click InitiativeViewer.exe

Question: "I need detailed information about everything"
Answer: → Read DEPLOYMENT_GUIDE.md

Question: "The build isn't working"
Answer: → Check troubleshooting in HOW_TO_BUILD_EXECUTABLE.txt

Question: "The executable won't run"
Answer: → Check troubleshooting in QUICK_START_EXECUTABLE.txt

Question: "I want to customize the build"
Answer: → Edit initiative_viewer.spec
        → Read advanced section in DEPLOYMENT_GUIDE.md

=============================================================================
📋 CHECKLIST FOR FIRST-TIME BUILD
=============================================================================

Before building for the first time:

☐ Python 3.8+ is installed
☐ Virtual environment is activated (if using one)
☐ Run: pip install -r requirements.txt
☐ All files exist: initiative_viewer.py, templates/, static/
☐ You have 2-4 GB free RAM
☐ You have 500 MB free disk space

Then:

☐ Double-click build_initiative_viewer.bat
☐ Wait for "Build completed successfully!" message
☐ Check that dist/InitiativeViewer.exe exists
☐ Test the executable
☐ Distribute to users with QUICK_START_EXECUTABLE.txt

=============================================================================
🎯 FILE SUMMARY
=============================================================================

📖 Documentation:
   • HOW_TO_BUILD_EXECUTABLE.txt    - Building the exe
   • QUICK_START_EXECUTABLE.txt     - Using the exe
   • DEPLOYMENT_GUIDE.md            - Complete reference

🔧 Build Tools:
   • build_initiative_viewer.bat    - Easy build (double-click this!)
   • build_initiative_viewer.py     - Build script
   • initiative_viewer.spec         - PyInstaller config

📦 Output:
   • dist/InitiativeViewer.exe      - The final executable

🐍 Source:
   • initiative_viewer.py           - Main application
   • templates/                     - HTML templates
   • static/                        - CSS, images, etc.

=============================================================================

Version: February 2026
Author: Pietro Maffi

=============================================================================
