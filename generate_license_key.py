"""
LICENSE KEY GENERATOR - COMMERCIAL SPORTS PREDICTION PLATFORM
Generates activation keys for the application using HMAC-based signatures.

Usage:
    python generate_license_key.py
    
Then use the generated key with:
    python main.py --activate <YOUR_KEY>
"""

import hashlib
import hmac
import secrets
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys


# Secret key for HMAC (should be kept secure in production)
# This must match the key in src/utils/activation.py
SECRET_KEY = b"sports_prediction_platform_2024_secret_key_v1"


def generate_license_key(
    customer_name: str = "Commercial User",
    expiry_days: int = 365,
    max_predictions: int = 10000,
    features: list = None
) -> str:
    """
    Generate a cryptographically secure license key.
    
    Args:
        customer_name: Name of the customer/organization
        expiry_days: Number of days until license expires
        max_predictions: Maximum predictions allowed
        features: List of enabled features (e.g., ['NHL', 'NFL', 'NBA', 'MLB'])
    
    Returns:
        Base64-encoded license key
    """
    if features is None:
        features = ['NHL', 'NFL', 'NBA', 'MLB']
    
    # Generate unique license ID
    license_id = secrets.token_hex(8)
    
    # Calculate expiry date
    issue_date = datetime.now()
    expiry_date = issue_date + timedelta(days=expiry_days)
    
    # Create license payload
    payload = {
        'license_id': license_id,
        'customer_name': customer_name,
        'issue_date': issue_date.isoformat(),
        'expiry_date': expiry_date.isoformat(),
        'max_predictions': max_predictions,
        'features': features,
        'version': '1.0'
    }
    
    # Convert to JSON
    payload_json = json.dumps(payload, sort_keys=True)
    payload_bytes = payload_json.encode('utf-8')
    
    # Create HMAC signature
    signature = hmac.new(
        SECRET_KEY,
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    
    # Combine payload and signature
    license_data = {
        'payload': payload,
        'signature': signature
    }
    
    # Encode as base64
    import base64
    license_json = json.dumps(license_data)
    license_key = base64.b64encode(license_json.encode('utf-8')).decode('utf-8')
    
    return license_key


def verify_license_key(license_key: str) -> dict:
    """
    Verify a license key's authenticity.
    
    Args:
        license_key: Base64-encoded license key
    
    Returns:
        Dictionary with verification result and payload
    """
    import base64
    
    try:
        # Decode from base64
        license_json = base64.b64decode(license_key.encode('utf-8')).decode('utf-8')
        license_data = json.loads(license_json)
        
        payload = license_data['payload']
        signature = license_data['signature']
        
        # Recreate signature
        payload_json = json.dumps(payload, sort_keys=True)
        payload_bytes = payload_json.encode('utf-8')
        expected_signature = hmac.new(
            SECRET_KEY,
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Verify signature
        if signature != expected_signature:
            return {
                'valid': False,
                'reason': 'Invalid signature - key has been tampered with'
            }
        
        # Check expiry
        expiry_date = datetime.fromisoformat(payload['expiry_date'])
        if datetime.now() > expiry_date:
            return {
                'valid': False,
                'reason': f"License expired on {expiry_date.strftime('%Y-%m-%d')}"
            }
        
        return {
            'valid': True,
            'payload': payload
        }
    
    except Exception as e:
        return {
            'valid': False,
            'reason': f'Invalid key format: {str(e)}'
        }


def generate_trial_key() -> str:
    """Generate a 30-day trial license."""
    return generate_license_key(
        customer_name="Trial User",
        expiry_days=30,
        max_predictions=1000,
        features=['NHL', 'NFL']
    )


def generate_commercial_key() -> str:
    """Generate a full commercial license (1 year)."""
    return generate_license_key(
        customer_name="Commercial License",
        expiry_days=365,
        max_predictions=100000,
        features=['NHL', 'NFL', 'NBA', 'MLB']
    )


def generate_developer_key() -> str:
    """Generate a developer license (unlimited)."""
    return generate_license_key(
        customer_name="Developer",
        expiry_days=3650,  # 10 years
        max_predictions=999999,
        features=['NHL', 'NFL', 'NBA', 'MLB']
    )


def save_license_key(license_key: str, filename: str = "license.key"):
    """Save license key to file."""
    project_root = Path(__file__).parent
    license_file = project_root / filename
    
    with open(license_file, 'w') as f:
        f.write(license_key)
    
    print(f"License key saved to: {license_file}")


def main():
    """Interactive license key generator."""
    print("=" * 70)
    print("LICENSE KEY GENERATOR - Sports Prediction Platform")
    print("=" * 70)
    print()
    
    print("Select license type:")
    print("  1. Trial License (30 days, 1,000 predictions, NHL/NFL only)")
    print("  2. Commercial License (1 year, 100,000 predictions, all sports)")
    print("  3. Developer License (10 years, unlimited, all sports)")
    print("  4. Custom License (specify parameters)")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        license_key = generate_trial_key()
        license_type = "Trial"
    
    elif choice == '2':
        license_key = generate_commercial_key()
        license_type = "Commercial"
    
    elif choice == '3':
        license_key = generate_developer_key()
        license_type = "Developer"
    
    elif choice == '4':
        print("\nCustom License Parameters:")
        customer_name = input("  Customer Name: ").strip() or "Custom User"
        expiry_days = int(input("  Expiry Days (e.g., 365): ").strip() or "365")
        max_predictions = int(input("  Max Predictions (e.g., 10000): ").strip() or "10000")
        
        print("  Features (comma-separated, e.g., NHL,NFL,NBA,MLB):")
        features_input = input("  ").strip() or "NHL,NFL,NBA,MLB"
        features = [f.strip().upper() for f in features_input.split(',')]
        
        license_key = generate_license_key(
            customer_name=customer_name,
            expiry_days=expiry_days,
            max_predictions=max_predictions,
            features=features
        )
        license_type = "Custom"
    
    else:
        print("Invalid choice. Exiting.")
        return
    
    print()
    print("=" * 70)
    print(f"{license_type} License Generated Successfully!")
    print("=" * 70)
    print()
    
    # Verify the key
    verification = verify_license_key(license_key)
    
    if verification['valid']:
        payload = verification['payload']
        print("License Details:")
        print(f"  License ID:      {payload['license_id']}")
        print(f"  Customer:        {payload['customer_name']}")
        print(f"  Issue Date:      {payload['issue_date'][:10]}")
        print(f"  Expiry Date:     {payload['expiry_date'][:10]}")
        print(f"  Max Predictions: {payload['max_predictions']:,}")
        print(f"  Features:        {', '.join(payload['features'])}")
        print()
    
    print("Your License Key:")
    print("-" * 70)
    print(license_key)
    print("-" * 70)
    print()
    
    # Save option
    save_choice = input("Save to file? (y/n): ").strip().lower()
    if save_choice == 'y':
        save_license_key(license_key)
        print()
    
    print("To activate the application, run:")
    print(f"  python main.py --activate {license_key[:50]}...")
    print()
    print("Or copy the key to the activation prompt when running:")
    print("  python main.py")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
