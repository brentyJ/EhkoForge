@echo off
REM EhkoForge Quick Commit v1.0
REM Usage: quick_commit.bat "Your commit message here"
REM Or double-click for interactive mode

echo.
echo ========================================
echo   EHKOFORGE QUICK COMMIT v1.0
echo ========================================
echo.

REM Check if message was provided as argument
if "%~1"=="" (
    REM Interactive mode
    echo No message provided. Entering interactive mode.
    echo.
    set /p MESSAGE="Enter commit message: "
) else (
    REM Command-line mode
    set MESSAGE=%~1
)

REM Validate message
if "%MESSAGE%"=="" (
    echo Error: No commit message provided.
    echo.
    pause
    exit /b 1
)

echo.
echo Commit message: %MESSAGE%
echo.

REM Git operations
echo Adding all changes...
git add .
if errorlevel 1 (
    echo Error: git add failed
    pause
    exit /b 1
)

echo Committing...
git commit -m "%MESSAGE%"
if errorlevel 1 (
    echo Error: git commit failed
    pause
    exit /b 1
)

echo Pushing to remote...
git push
if errorlevel 1 (
    echo Error: git push failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SUCCESS - Changes pushed to remote
echo ========================================
echo.
pause
