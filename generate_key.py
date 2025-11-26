"""
License Key Generator Utility
Generates activation keys for the Sports Forecasting Platform

Usage:
    python generate_key.py --days 90 --type TRIAL
    python generate_key.py --days 365 --type PROFESSIONAL
    python generate_key.py --days 30 --type DEMO
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.activation import LicenseManager


def generate_key(days_valid: int = 90, license_type: str = "TRIAL"):
    """Generate a new license key"""
    
    print("\n" + "=" * 60)
    print("LICENSE KEY GENERATOR")
    print("=" * 60)
    print(f"Generating {license_type} license ({days_valid} days)...")
    print()
    
    # Generate key
    key = LicenseManager.generate_key(days_valid=days_valid, license_id=license_type)
    
    # Display key
    print("✓ LICENSE KEY GENERATED SUCCESSFULLY")
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
        print(f"  Created: {info.get('created_at')}")
    print()
    
    # Save option
    save_option = input("Save this key to file? (y/n): ").strip().lower()
    if save_option == 'y':
        if LicenseManager.save_license(key):
            print("✓ Key saved successfully")
        else:
            print("❌ Failed to save key")
    
    print()
    print("=" * 60)
    print()
    
    return key


def main():
    """CLI interface for key generation"""
    
    parser = argparse.ArgumentParser(
        description="Generate license keys for Sports Forecasting Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_key.py
  python generate_key.py --days 365 --type PROFESSIONAL
  python generate_key.py --days 30 --type DEMO
        """
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Number of days the license is valid (default: 90)"
    )
    
    parser.add_argument(
        "--type",
        default="TRIAL",
        choices=["DEMO", "TRIAL", "BASIC", "PROFESSIONAL", "ENTERPRISE"],
        help="License type (default: TRIAL)"
    )
    
    parser.add_argument(
        "--validate",
        help="Validate an existing license key"
    )
    
    parser.add_argument(
        "--info",
        help="Get information about a license key"
    )
    
    args = parser.parse_args()
    
    # Handle validation
    if args.validate:
        print("\nValidating license key...")
        is_valid, message = LicenseManager.validate_key(args.validate)
        print(f"Result: {message}")
        info = LicenseManager.get_license_info(args.validate)
        if info:
            print(f"Type: {info.get('license_id')}")
            print(f"Valid until: {info.get('end_date')}")
        return
    
    # Handle info request
    if args.info:
        print("\nExtracting license information...")
        info = LicenseManager.get_license_info(args.info)
        if info:
            print(f"License Type: {info.get('license_id')}")
            print(f"Start Date: {info.get('start_date')}")
            print(f"End Date: {info.get('end_date')}")
            print(f"Created: {info.get('created_at')}")
        else:
            print("Invalid license key format")
        return
    
    # Generate new key
    generate_key(days_valid=args.days, license_type=args.type)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
