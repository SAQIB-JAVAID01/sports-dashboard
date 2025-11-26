"""
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
        print("\n\nDashboard stopped.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        input("Press Enter to exit...")

if __name__ == '__main__':
    main()
