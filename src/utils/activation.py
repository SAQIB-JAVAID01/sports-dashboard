"""
License Activation System using HMAC-SHA256
Generates and validates activation keys with date-based expiration
"""

import hmac
import hashlib
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger("activation")

# Developer's private key - KEEP THIS SECRET
PRIVATE_KEY = "sports_forecast_dev_key_2024_nov_secure"

# License storage location
LICENSE_FILE = Path(__file__).resolve().parent.parent.parent / ".license"


class LicenseManager:
    """Manages license key generation and validation"""
    
    @staticmethod
    def generate_key(days_valid: int = 90, license_id: str = "TRIAL") -> str:
        """
        Generates an HMAC-SHA256 based license key
        
        Args:
            days_valid: Number of days the license is valid
            license_id: License identifier (e.g., "TRIAL", "BASIC", "PROFESSIONAL")
            
        Returns:
            License key string
        """
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_valid)
        
        # Create license payload
        payload = {
            "license_id": license_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        # Convert to JSON and encode
        payload_json = json.dumps(payload, sort_keys=True)
        payload_b64 = base64.b64encode(payload_json.encode()).decode()
        
        # Generate HMAC signature
        signature = hmac.new(
            PRIVATE_KEY.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload and signature
        license_key = f"{payload_b64}.{signature}"
        
        logger.info(f"Generated license key: {license_id} (valid until {end_date})")
        return license_key
    
    @staticmethod
    def validate_key(license_key: str) -> Tuple[bool, str]:
        """
        Validates a license key and checks expiration
        
        Args:
            license_key: License key to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            if "." not in license_key:
                return False, "Invalid license format"
            
            payload_b64, signature = license_key.rsplit(".", 1)
            
            # Decode payload
            try:
                payload_json = base64.b64decode(payload_b64).decode()
                payload = json.loads(payload_json)
            except Exception as e:
                return False, f"Failed to decode license: {str(e)}"
            
            # Verify signature
            expected_signature = hmac.new(
                PRIVATE_KEY.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                return False, "License signature invalid - tampering detected"
            
            # Check expiration
            end_date = datetime.fromisoformat(payload["end_date"]).date()
            if datetime.now().date() > end_date:
                return False, f"License expired on {end_date}"
            
            # Check start date
            start_date = datetime.fromisoformat(payload["start_date"]).date()
            if datetime.now().date() < start_date:
                return False, f"License not yet valid (starts {start_date})"
            
            days_remaining = (end_date - datetime.now().date()).days
            return True, f" License valid - {days_remaining} days remaining"
            
        except Exception as e:
            return False, f"License validation error: {str(e)}"
    
    @staticmethod
    def save_license(license_key: str, file_path: Optional[Path] = None) -> bool:
        """Save license key to file"""
        try:
            path = file_path or LICENSE_FILE
            path.write_text(license_key)
            logger.info(f"License saved to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save license: {e}")
            return False
    
    @staticmethod
    def load_license(file_path: Optional[Path] = None) -> Optional[str]:
        """Load license key from file"""
        try:
            path = file_path or LICENSE_FILE
            if path.exists():
                return path.read_text().strip()
        except Exception as e:
            logger.error(f"Failed to load license: {e}")
        return None
    
    @staticmethod
    def get_license_info(license_key: str) -> Optional[Dict]:
        """Extract license information without validation"""
        try:
            if "." not in license_key:
                return None
            
            payload_b64, _ = license_key.rsplit(".", 1)
            payload_json = base64.b64decode(payload_b64).decode()
            return json.loads(payload_json)
        except:
            return None


class ActivationManager:
    """Manages application activation status"""
    
    def __init__(self):
        self.is_activated = False
        self.license_info = None
        self.license_key = None
    
    def activate(self, license_key: str) -> Tuple[bool, str]:
        """
        Activate application with license key
        
        Returns:
            Tuple of (success, message)
        """
        is_valid, message = LicenseManager.validate_key(license_key)
        
        if not is_valid:
            logger.warning(f"Activation failed: {message}")
            return False, message
        
        # Save license
        if LicenseManager.save_license(license_key):
            self.is_activated = True
            self.license_key = license_key
            self.license_info = LicenseManager.get_license_info(license_key)
            logger.info(" Application activated successfully")
            return True, f" {message}"
        else:
            return False, "Failed to save license"
    
    def check_activation(self) -> Tuple[bool, str]:
        """Check if application is currently activated"""
        # Try to load stored license
        stored_key = LicenseManager.load_license()
        
        if not stored_key:
            return False, "No license found - please activate"
        
        # Validate stored license
        is_valid, message = LicenseManager.validate_key(stored_key)
        
        if is_valid:
            self.is_activated = True
            self.license_key = stored_key
            self.license_info = LicenseManager.get_license_info(stored_key)
            return True, message
        else:
            return False, message
    
    def get_status(self) -> Dict:
        """Get detailed activation status"""
        is_active, message = self.check_activation()
        
        return {
            "is_activated": is_active,
            "message": message,
            "license_info": self.license_info,
            "license_type": self.license_info.get("license_id", "UNKNOWN") if self.license_info else "NONE"
        }
