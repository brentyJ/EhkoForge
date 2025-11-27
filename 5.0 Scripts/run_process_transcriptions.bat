@echo off
echo ================================================
echo EHKO REFRESH - Fix and Process Transcriptions
echo ================================================
echo.

cd "%~dp0"

echo Step 1: Fixing regex bug...
python fix_regex.py
echo.

echo Step 2: Fixing theme header detection...
python fix_theme_headers.py
echo.

echo Step 3: Fixing transcription extraction...
python fix_transcription_extraction.py
echo.

echo Step 4: Running ehko_refresh.py...
python ehko_refresh.py
echo.

echo ================================================
echo Script completed
echo ================================================
echo.
pause
