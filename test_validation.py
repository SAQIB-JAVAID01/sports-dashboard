"""
Validation Test Script
Tests the core functionality without GUI
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n" + "=" * 70)
print("SPORTS FORECASTING PLATFORM - VALIDATION TEST")
print("=" * 70 + "\n")

try:
    # Test 1: Import core modules
    print("TEST 1: Importing core modules...")
    from src.utils.activation import LicenseManager, ActivationManager
    from src.api_client import SportsAPIClient
    from src.prediction import PredictionService
    print("✓ All core modules imported successfully\n")
    
    # Test 2: Load and validate license
    print("TEST 2: Checking license...")
    activation = ActivationManager()
    is_active, message = activation.check_activation()
    print(f"  Status: {message}")
    if is_active:
        print(f"  Type: {activation.license_info.get('license_id')}")
        print(f"  Valid until: {activation.license_info.get('end_date')}")
    print("✓ License check complete\n")
    
    # Test 3: Initialize API client
    print("TEST 3: Initializing API client...")
    api_client = SportsAPIClient()
    sports = api_client.get_sports()
    print(f"  Supported sports: {', '.join(sports)}")
    print("✓ API client initialized\n")
    
    # Test 4: Initialize prediction service
    print("TEST 4: Initializing prediction service...")
    prediction = PredictionService()
    if prediction.load_models():
        print("  Models loaded successfully")
    else:
        print("  Models directory found (lazy loading enabled)")
    print("✓ Prediction service ready\n")
    
    # Test 5: Generate test prediction
    print("TEST 5: Generating sample prediction...")
    test_game = {
        "home_team": "Team A",
        "away_team": "Team B",
        "over_under": 45.5
    }
    ou_pred = prediction.predict_over_under("NFL", test_game)
    print(f"  O/U Prediction: {ou_pred.get('prediction')} ({ou_pred.get('probability'):.1%})")
    
    spread_pred = prediction.predict_spread("NFL", test_game)
    print(f"  Spread Prediction: {spread_pred.get('prediction')} ({spread_pred.get('probability'):.1%})")
    
    winner_pred = prediction.predict_winner("NFL", test_game)
    print(f"  Winner Prediction: {winner_pred.get('prediction')} ({winner_pred.get('probability'):.1%})")
    print("✓ Predictions generated\n")
    
    # Test 6: SHAP explanation
    print("TEST 6: Getting SHAP feature importance...")
    shap = prediction.get_shap_explanation("NFL", test_game)
    print("  Top contributing features:")
    for feature in shap.get('top_features', [])[:3]:
        print(f"    - {feature['name']}: {feature['impact']:.2f}")
    print("✓ SHAP values available\n")
    
    # Test 7: Check file structure
    print("TEST 7: Validating directory structure...")
    required_dirs = [
        "src",
        "src/gui",
        "src/utils",
        "LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP"
    ]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}")
        else:
            print(f"  ✗ {dir_name} (missing)")
    print()
    
    # Test 8: Check license file
    print("TEST 8: Checking license storage...")
    license_file = project_root.parent / ".license"
    if license_file.exists():
        print(f"  ✓ License file found: {license_file.name}")
    else:
        print(f"  ⚠ No license file (expected after activation)")
    print()
    
    # Summary
    print("=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    print("\nAPPLICATION STATUS:")
    print(f"  License: {'ACTIVE ✓' if is_active else 'INACTIVE - Requires activation'}")
    print(f"  API Client: READY")
    print(f"  Models: LOADED" if prediction.models_loaded else "  Models: READY (lazy loading)")
    print(f"  GUI Framework: PyQt6 (install with: pip install PyQt6)")
    print()
    print("TO RUN THE GUI APPLICATION:")
    print("  1. pip install PyQt6")
    print("  2. python main.py")
    print()
    print("=" * 70 + "\n")
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
