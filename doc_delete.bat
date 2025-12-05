@echo off
echo ============================================================
echo EhkoForge Cleanup - Delete Redundant Files
echo ============================================================
echo.
echo This will delete the following files:
echo.
echo SUPERSEDED SPECS:
echo   - 2.0 Modules\ReCog\ReCog_Engine_Spec_v0_2.md (replaced by v1.0)
echo   - 2.0 Modules\UI_Redesign_Spec_v0_1.md (pre-Reorientation design)
echo.
echo LEGACY FRONTEND:
echo   - 6.0 Frontend\static\index.html (replaced by templates\index.html)
echo   - 6.0 Frontend\static\app.js (replaced by js\main.js)
echo   - 6.0 Frontend\static\styles.css (replaced by css\main.css)
echo   - 6.0 Frontend\static\js\journal.js (unused since Reorientation)
echo.
echo APPLIED PATCHES:
echo   - 5.0 Scripts\_archive\fix_regex.py
echo   - 5.0 Scripts\_archive\fix_theme_headers.py
echo   - 5.0 Scripts\_archive\fix_transcription_extraction.py
echo   - 5.0 Scripts\_archive\cleanup_unused_ui.py
echo.
echo ============================================================
echo.
set /p confirm="Type YES to proceed with deletion: "

if /I not "%confirm%"=="YES" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Deleting files...

REM Superseded specs
del "G:\Other computers\Ehko\Obsidian\EhkoForge\2.0 Modules\ReCog\ReCog_Engine_Spec_v0_2.md"
if %errorlevel%==0 (echo   [OK] ReCog_Engine_Spec_v0_2.md) else (echo   [FAIL] ReCog_Engine_Spec_v0_2.md)

del "G:\Other computers\Ehko\Obsidian\EhkoForge\2.0 Modules\UI_Redesign_Spec_v0_1.md"
if %errorlevel%==0 (echo   [OK] UI_Redesign_Spec_v0_1.md) else (echo   [FAIL] UI_Redesign_Spec_v0_1.md)

REM Legacy frontend
del "G:\Other computers\Ehko\Obsidian\EhkoForge\6.0 Frontend\static\index.html"
if %errorlevel%==0 (echo   [OK] static\index.html) else (echo   [FAIL] static\index.html)

del "G:\Other computers\Ehko\Obsidian\EhkoForge\6.0 Frontend\static\app.js"
if %errorlevel%==0 (echo   [OK] static\app.js) else (echo   [FAIL] static\app.js)

del "G:\Other computers\Ehko\Obsidian\EhkoForge\6.0 Frontend\static\styles.css"
if %errorlevel%==0 (echo   [OK] static\styles.css) else (echo   [FAIL] static\styles.css)

del "G:\Other computers\Ehko\Obsidian\EhkoForge\6.0 Frontend\static\js\journal.js"
if %errorlevel%==0 (echo   [OK] js\journal.js) else (echo   [FAIL] js\journal.js)

REM Applied patches - delete entire _archive folder
rmdir /S /Q "G:\Other computers\Ehko\Obsidian\EhkoForge\5.0 Scripts\_archive"
if %errorlevel%==0 (echo   [OK] _archive folder removed) else (echo   [FAIL] _archive folder)

echo.
echo ============================================================
echo Cleanup complete!
echo.
echo Don't forget to run git_push.bat to commit these deletions.
echo ============================================================
pause
