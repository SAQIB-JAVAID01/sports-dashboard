@echo off
REM ============================================================================
REM STREAMLIT CLOUD DEPLOYMENT SCRIPT
REM Deploy your dashboard to Streamlit Cloud (works when Python is closed)
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo.   STREAMLIT CLOUD DEPLOYMENT SCRIPT
echo.   Sports Prediction Dashboard
echo.
echo ========================================================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [!] ERROR: Git is not installed
    echo [!] Please install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [!] Current directory:
cd

echo.
echo [1/5] Initializing Git Repository...
git init >nul 2>&1
git config user.email "sports-dashboard@local" >nul 2>&1
git config user.name "Sports Dashboard" >nul 2>&1
echo [✓] Git initialized

echo.
echo [2/5] Staging files for upload...
git add . >nul 2>&1
echo [✓] Files staged

echo.
echo [3/5] Creating commit...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a-%%b)
git commit -m "Sports Dashboard - Deployment %mydate% %mytime%" >nul 2>&1
echo [✓] Commit created

echo.
echo ========================================================================
echo.
echo [4/5] GITHUB SETUP REQUIRED
echo.
echo You need to:
echo   1. Go to https://github.com/new
echo   2. Create a NEW repository (any name)
echo   3. Copy the repository URL (e.g., https://github.com/YOUR-USERNAME/repo-name)
echo   4. Paste it below when prompted
echo.
echo ========================================================================
echo.

set /p repo_url="Enter your GitHub repository URL: "

if "!repo_url!"=="" (
    echo [!] ERROR: No repository URL provided
    pause
    exit /b 1
)

echo.
echo [!] Adding remote repository...
git remote remove origin >nul 2>&1
git remote add origin !repo_url! >nul 2>&1
git branch -M main >nul 2>&1
echo [✓] Remote configured

echo.
echo [5/5] Pushing code to GitHub...
git push -u origin main
if errorlevel 1 (
    echo.
    echo [!] Push failed. Make sure:
    echo     - Repository URL is correct
    echo     - You have internet connection
    echo     - Your GitHub credentials are saved
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================================================
echo.
echo [✓] SUCCESS! Code pushed to GitHub
echo.
echo NEXT STEP: Deploy to Streamlit Cloud
echo   1. Go to https://streamlit.io/cloud
echo   2. Sign in with GitHub
echo   3. Click "New app"
echo   4. Select your repository
echo   5. Main file: streamlit_app.py
echo   6. Click "Deploy"
echo.
echo Your app will be live in 2-3 minutes!
echo.
echo ========================================================================
echo.

pause
