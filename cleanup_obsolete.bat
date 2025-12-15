@echo off
echo ============================================================
echo EhkoForge Cleanup - Remove Obsolete Files
echo ============================================================
echo.
echo This will delete the following files:
echo.
echo APPLIED MIGRATION RUNNERS (6 files):
echo   - run_ingot_migration.py
echo   - run_reorientation_migration.py
echo   - run_mana_migration.py
echo   - run_memory_migration.py
echo   - run_ingestion_migration.py
echo   - run_tethers_migration.py
echo.
echo DEBUG SCRIPTS (2 files):
echo   - debug_extract.py
echo   - test_scheduler.py
echo.
echo ARCHIVED SPECS (3 files):
echo   - archive\1_5_Behaviour_Engine_v1_0.md
echo   - archive\1_4_Data_Model_v1_2_patch.md
echo   - archive\1_7_Ehko_Cultivation_^& Growth_Framework_v1_0.md
echo.
echo OBSOLETE BATCH FILES (1 file):
echo   - doc_delete.bat
echo.
echo EMPTY DIRECTORIES (2 folders):
echo   - 5.0 Scripts\_backups\
echo   - _ledger\
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
echo.

cd /d "G:\Other computers\Ehko\Obsidian\EhkoForge"

REM Applied migration runners
del "5.0 Scripts\run_ingot_migration.py" 2>nul
if %errorlevel%==0 (echo   [OK] run_ingot_migration.py) else (echo   [SKIP] run_ingot_migration.py - not found)

del "5.0 Scripts\run_reorientation_migration.py" 2>nul
if %errorlevel%==0 (echo   [OK] run_reorientation_migration.py) else (echo   [SKIP] run_reorientation_migration.py - not found)

del "5.0 Scripts\run_mana_migration.py" 2>nul
if %errorlevel%==0 (echo   [OK] run_mana_migration.py) else (echo   [SKIP] run_mana_migration.py - not found)

del "5.0 Scripts\run_memory_migration.py" 2>nul
if %errorlevel%==0 (echo   [OK] run_memory_migration.py) else (echo   [SKIP] run_memory_migration.py - not found)

del "5.0 Scripts\run_ingestion_migration.py" 2>nul
if %errorlevel%==0 (echo   [OK] run_ingestion_migration.py) else (echo   [SKIP] run_ingestion_migration.py - not found)

del "5.0 Scripts\run_tethers_migration.py" 2>nul
if %errorlevel%==0 (echo   [OK] run_tethers_migration.py) else (echo   [SKIP] run_tethers_migration.py - not found)

REM Debug scripts
del "5.0 Scripts\debug_extract.py" 2>nul
if %errorlevel%==0 (echo   [OK] debug_extract.py) else (echo   [SKIP] debug_extract.py - not found)

del "5.0 Scripts\test_scheduler.py" 2>nul
if %errorlevel%==0 (echo   [OK] test_scheduler.py) else (echo   [SKIP] test_scheduler.py - not found)

REM Archived specs
del "archive\1_5_Behaviour_Engine_v1_0.md" 2>nul
if %errorlevel%==0 (echo   [OK] 1_5_Behaviour_Engine_v1_0.md) else (echo   [SKIP] 1_5_Behaviour_Engine_v1_0.md - not found)

del "archive\1_4_Data_Model_v1_2_patch.md" 2>nul
if %errorlevel%==0 (echo   [OK] 1_4_Data_Model_v1_2_patch.md) else (echo   [SKIP] 1_4_Data_Model_v1_2_patch.md - not found)

del "archive\1_7_Ehko_Cultivation_& Growth_Framework_v1_0.md" 2>nul
if %errorlevel%==0 (echo   [OK] 1_7_Ehko_Cultivation...v1_0.md) else (echo   [SKIP] 1_7_Ehko_Cultivation...v1_0.md - not found)

REM Obsolete batch file
del "doc_delete.bat" 2>nul
if %errorlevel%==0 (echo   [OK] doc_delete.bat) else (echo   [SKIP] doc_delete.bat - not found)

REM Empty directories
rmdir "5.0 Scripts\_backups" 2>nul
if %errorlevel%==0 (echo   [OK] _backups folder) else (echo   [SKIP] _backups folder - not empty or not found)

rmdir "_ledger" 2>nul
if %errorlevel%==0 (echo   [OK] _ledger folder) else (echo   [SKIP] _ledger folder - not empty or not found)

REM Check if archive folder is now empty and remove if so
dir /b "archive" 2>nul | findstr . >nul
if %errorlevel%==1 (
    rmdir "archive" 2>nul
    if %errorlevel%==0 (echo   [OK] archive folder - was empty, removed) else (echo   [SKIP] archive folder)
)

echo.
echo ============================================================
echo Cleanup complete!
echo.
echo Run git_push.bat to commit these deletions.
echo ============================================================
pause
