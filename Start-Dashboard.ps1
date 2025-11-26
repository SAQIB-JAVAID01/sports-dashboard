# Sports Prediction Dashboard Launcher
# Run this script to start the dashboard

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "           SPORTS PREDICTION DASHBOARD" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting dashboard... Please wait..." -ForegroundColor Green
Write-Host ""
Write-Host "The dashboard will open in your browser at:" -ForegroundColor White
Write-Host "   http://localhost:8505" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Check Python
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from https://www.python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check streamlit
try {
    python -c "import streamlit" 2>$null
} catch {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install streamlit pandas numpy scikit-learn xgboost plotly joblib --quiet
}

# Open browser
Start-Process "http://localhost:8505"

# Start dashboard
python -m streamlit run comprehensive_sports_dashboard.py --server.port 8505
