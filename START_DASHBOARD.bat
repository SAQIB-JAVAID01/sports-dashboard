@echo off
title Sports Prediction Dashboard
echo ============================================================
echo            SPORTS PREDICTION DASHBOARD
echo ============================================================
echo.
echo Starting dashboard... Please wait...
echo.
echo The dashboard will open in your browser at:
echo    http://localhost:8505
echo.
echo Press Ctrl+C to stop the server.
echo ============================================================
echo.

cd /d "%~dp0"

REM Try to find Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install streamlit pandas numpy scikit-learn xgboost plotly joblib --quiet
)

REM Start the dashboard
start "" http://localhost:8505
python -m streamlit run comprehensive_sports_dashboard.py --server.port 8505

pause
