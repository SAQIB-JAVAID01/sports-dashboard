# Sports Prediction Dashboard - Installation Guide

## Quick Start (Easiest Method)

1. Double-click `START_DASHBOARD.bat`
2. The dashboard will open in your browser at http://localhost:8505

## Alternative Methods

### PowerShell
```powershell
.\Start-Dashboard.ps1
```

### Python Direct
```bash
python -m streamlit run comprehensive_sports_dashboard.py --server.port 8505
```

## Requirements

- Python 3.10 or higher
- Internet connection (for first-time package installation)

## Included Files

- `START_DASHBOARD.bat` - Windows batch launcher (easiest)
- `Start-Dashboard.ps1` - PowerShell launcher
- `launch_dashboard.py` - Python launcher script
- `comprehensive_sports_dashboard.py` - Main dashboard application
- `ml_prediction_integration.py` - ML prediction module
- `datasets/` - Sports data files
- `LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/` - Pre-trained models

## Troubleshooting

### "Python not found"
Install Python from https://www.python.org/downloads/
Make sure to check "Add Python to PATH" during installation.

### "Module not found"
Run this command to install dependencies:
```bash
pip install streamlit pandas numpy scikit-learn xgboost plotly joblib
```

### Dashboard won't start
1. Check if port 8505 is already in use
2. Try a different port: `python -m streamlit run comprehensive_sports_dashboard.py --server.port 8506`

## Support

For issues, check the documentation in `DASHBOARD_STATUS_REPORT.md`
