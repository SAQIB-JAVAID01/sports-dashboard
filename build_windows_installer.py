"""
Windows Installer Builder for Sports Prediction Dashboard
Creates a standalone executable using PyInstaller
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil


def check_dependencies():
    """Check if required packages are installed"""
    try:
        import PyInstaller
        print("[OK] PyInstaller is installed")
        return True
    except ImportError:
        print("[!] PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"])
        print("[OK] PyInstaller installed successfully")
        return True


def create_spec_file():
    """Create PyInstaller spec file for the dashboard"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all data files
datas = [
    ('datasets/', 'datasets/'),
    ('LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/', 'LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/'),
    ('src/', 'src/'),
    ('*.csv', '.'),
]

# Hidden imports for ML libraries
hiddenimports = [
    'streamlit',
    'pandas',
    'numpy',
    'sklearn',
    'sklearn.ensemble',
    'sklearn.linear_model',
    'xgboost',
    'joblib',
    'plotly',
    'plotly.express',
    'plotly.graph_objects',
]

a = Analysis(
    ['comprehensive_sports_dashboard.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SportsPredictionDashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set to False for no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SportsPredictionDashboard',
)
'''
    
    spec_path = Path(__file__).parent / 'SportsPredictionDashboard.spec'
    spec_path.write_text(spec_content, encoding='utf-8')
    print(f"[OK] Created spec file: {spec_path}")
    return spec_path


def create_launcher_script():
    """Create a simple launcher script that starts Streamlit"""
    
    launcher_content = '''"""
Sports Prediction Dashboard Launcher
Double-click this file to start the dashboard
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def main():
    """Launch the Streamlit dashboard"""
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    dashboard_path = script_dir / 'comprehensive_sports_dashboard.py'
    
    if not dashboard_path.exists():
        print("[ERROR] Dashboard file not found!")
        print(f"   Expected: {dashboard_path}")
        input("Press Enter to exit...")
        return
    
    print("=" * 60)
    print("SPORTS PREDICTION DASHBOARD")
    print("=" * 60)
    print()
    print("Starting dashboard server...")
    print("This may take a few seconds...")
    print()
    
    # Start Streamlit
    port = 8505
    url = f"http://localhost:{port}"
    
    # Open browser after a delay
    def open_browser():
        time.sleep(3)
        webbrowser.open(url)
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.start()
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            str(dashboard_path),
            '--server.port', str(port),
            '--server.headless', 'true',
            '--theme.primaryColor', '#1e40af',
            '--theme.backgroundColor', '#ffffff',
            '--theme.secondaryBackgroundColor', '#f0f2f6',
        ], cwd=str(script_dir))
    except KeyboardInterrupt:
        print("\\n\\nDashboard stopped.")
    except Exception as e:
        print(f"\\n[ERROR] {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
'''
    
    launcher_path = Path(__file__).parent / 'launch_dashboard.py'
    launcher_path.write_text(launcher_content, encoding='utf-8')
    print(f"[OK] Created launcher: {launcher_path}")
    return launcher_path


def create_batch_launcher():
    """Create Windows batch file launcher"""
    
    batch_content = '''@echo off
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
'''
    
    batch_path = Path(__file__).parent / 'START_DASHBOARD.bat'
    batch_path.write_text(batch_content, encoding='utf-8')
    print(f"[OK] Created batch launcher: {batch_path}")
    return batch_path


def create_powershell_launcher():
    """Create PowerShell launcher script"""
    
    ps_content = '''# Sports Prediction Dashboard Launcher
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
'''
    
    ps_path = Path(__file__).parent / 'Start-Dashboard.ps1'
    ps_path.write_text(ps_content, encoding='utf-8')
    print(f"[OK] Created PowerShell launcher: {ps_path}")
    return ps_path


def build_standalone():
    """Build standalone executable with PyInstaller"""
    
    print("\n" + "=" * 60)
    print("Building Standalone Executable")
    print("=" * 60 + "\n")
    
    # Build directory
    build_dir = Path(__file__).parent / 'dist'
    
    # Create a simple entry point for PyInstaller
    entry_point = '''"""
Sports Prediction Dashboard Entry Point
"""
import subprocess
import sys
import os

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    subprocess.call([sys.executable, '-m', 'streamlit', 'run', 
                    'comprehensive_sports_dashboard.py', 
                    '--server.port', '8505'])

if __name__ == '__main__':
    main()
'''
    
    entry_path = Path(__file__).parent / '_entry_point.py'
    entry_path.write_text(entry_point)
    
    # Run PyInstaller
    try:
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--name', 'SportsPredictionDashboard',
            '--onedir',  # Create directory with exe
            '--console',  # Keep console for server output
            '--clean',
            '--noconfirm',
            str(entry_path)
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n[OK] Build successful!")
            print(f"   Output: {build_dir / 'SportsPredictionDashboard'}")
        else:
            print(f"\n[ERROR] Build failed:")
            print(result.stderr)
            
    except Exception as e:
        print(f"\n[ERROR] Build error: {e}")
    
    # Cleanup
    if entry_path.exists():
        entry_path.unlink()


def create_readme():
    """Create README for the installer package"""
    
    readme_content = '''# Sports Prediction Dashboard - Installation Guide

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
'''
    
    readme_path = Path(__file__).parent / 'INSTALLER_README.md'
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"[OK] Created installer README: {readme_path}")
    return readme_path


def main():
    """Main build process"""
    
    print("\n" + "=" * 60)
    print("Sports Prediction Dashboard - Windows Installer Builder")
    print("=" * 60 + "\n")
    
    # Check dependencies
    print("1. Checking dependencies...")
    check_dependencies()
    
    # Create launcher files
    print("\n2. Creating launcher files...")
    create_batch_launcher()
    create_powershell_launcher()
    create_launcher_script()
    create_readme()
    
    print("\n" + "=" * 60)
    print("[OK] BUILD COMPLETE!")
    print("=" * 60)
    print("\nCreated files:")
    print("  - START_DASHBOARD.bat     (Double-click to run)")
    print("  - Start-Dashboard.ps1     (PowerShell script)")
    print("  - launch_dashboard.py     (Python launcher)")
    print("  - INSTALLER_README.md     (Installation guide)")
    print("\nTo distribute:")
    print("  1. Copy the entire Sports-Project-main folder")
    print("  2. Users can double-click START_DASHBOARD.bat")
    print("\nTo build standalone .exe (advanced):")
    print("  Run: python build_windows_installer.py --standalone")


if __name__ == '__main__':
    if '--standalone' in sys.argv:
        check_dependencies()
        build_standalone()
    else:
        main()
