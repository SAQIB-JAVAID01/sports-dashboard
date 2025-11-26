"""
Auto-generate and save license key
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils.activation import LicenseManager

print("\n" + "=" * 60)
print("LICENSE KEY GENERATOR - AUTO SAVE")
print("=" * 60)
print("Generating 90-day TRIAL license...")
print()

# Generate key
key = LicenseManager.generate_key(days_valid=90, license_id="TRIAL")

# Display key
print("[OK] LICENSE KEY GENERATED SUCCESSFULLY")
print()
print("KEY:")
print("-" * 60)
print(key)
print("-" * 60)
print()

# Validate key
is_valid, message = LicenseManager.validate_key(key)
print(f"Validation: {message}")
print()

# Get key info
info = LicenseManager.get_license_info(key)
if info:
    print("License Details:")
    print(f"  Type: {info.get('license_id')}")
    print(f"  Start Date: {info.get('start_date')}")
    print(f"  End Date: {info.get('end_date')}")
    print()

# Auto-save
if LicenseManager.save_license(key):
    print("[OK] Key saved to .license file")
else:
    print("[FAIL] Could not save key")

print()
print("=" * 60)
print("Ready to run: python main.py")
print("=" * 60)
print()
