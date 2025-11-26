"""
Quick Setup Script
Automated setup for Sports Prediction Platform with minimal user interaction
"""

import subprocess
import sys
from pathlib import Path
import os

def run_command(cmd, description):
    """Run command with user feedback"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"   ✅ {description} - Success")
            return True
        else:
            print(f"   ⚠️ {description} - Warning")
            if result.stderr:
                print(f"   {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ {description} - Failed: {e}")
        return False

def main():
    print("=" * 70)
    print("SPORTS PREDICTION PLATFORM - AUTOMATED SETUP")
    print("=" * 70)
    print()
    print("This script will:")
    print("  1. Install required Python packages")
    print("  2. Verify model files")
    print("  3. Generate trial license")
    print("  4. Test system")
    print("  5. Launch dashboard")
    print()
    input("Press Enter to continue...")
    
    # Check Python version
    print(f"\n✓ Python version: {sys.version.split()[0]}")
    
    # Install packages
    packages = [
        "pandas numpy scipy scikit-learn",
        "catboost lightgbm xgboost",
        "streamlit plotly",
        "reportlab requests python-dotenv"
    ]
    
    for pkg_group in packages:
        run_command(
            f"pip install {pkg_group} --quiet --disable-pip-version-check",
            f"Installing {pkg_group.split()[0]} and dependencies"
        )
    
    # Check model files
    print("\n🔍 Checking model files...")
    models_dir = Path("LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP")
    if models_dir.exists():
        model_dirs = [d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith(("NHL_", "NFL_", "NBA_", "MLB_"))]
        print(f"   ✅ Found {len(model_dirs)} trained models")
        for md in model_dirs:
            print(f"      • {md.name}")
    else:
        print("   ⚠️ No models found - will use demo mode")
    
    # Generate trial license
    print("\n🔑 Generating trial license...")
    if Path("generate_license_key.py").exists():
        try:
            # Auto-generate trial key
            result = subprocess.run(
                [sys.executable, "generate_license_key.py"],
                input="1\ny\n",  # Select trial, save to file
                capture_output=True,
                text=True,
                timeout=10
            )
            if "license.key" in result.stdout.lower() or Path("license.key").exists():
                print("   ✅ Trial license generated (30 days)")
            else:
                print("   ⚠️ License generation skipped - will run in demo mode")
        except:
            print("   ⚠️ Auto-generation failed - run manually: python generate_license_key.py")
    
    # Test system
    print("\n🧪 Testing system...")
    test_results = {
        "Data files": Path("nfl_games.csv").exists() or Path("mlb_games.csv").exists(),
        "Source code": Path("src").exists() and Path("main.py").exists(),
        "License system": Path("src/utils/activation.py").exists(),
        "Dashboard": Path("comprehensive_sports_dashboard.py").exists()
    }
    
    for test, passed in test_results.items():
        status = "✅" if passed else "⚠️"
        print(f"   {status} {test}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("📚 Quick Start Commands:")
    print()
    print("  1. Launch Dashboard (Recommended):")
    print("     streamlit run comprehensive_sports_dashboard.py")
    print()
    print("  2. Train Models:")
    print("     python train_single_sport.py NHL")
    print("     python train_single_sport.py NFL")
    print()
    print("  3. Generate License:")
    print("     python generate_license_key.py")
    print()
    print("  4. Build Installer:")
    print("     python build_installer.py")
    print()
    print("  5. Test Predictions:")
    print("     python demo_nhl_prediction.py")
    print()
    
    # Auto-launch option
    print("=" * 70)
    launch = input("\n🚀 Launch dashboard now? (y/n): ").strip().lower()
    
    if launch == 'y':
        print("\n🌐 Starting dashboard on http://localhost:8501...")
        print("   Press Ctrl+C to stop")
        print()
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                "comprehensive_sports_dashboard.py",
                "--server.port", "8501"
            ])
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard stopped")
    else:
        print("\n👋 Setup complete! Run commands above to get started.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Setup error: {e}")
        print("Please run commands manually - see README.md")
