"""
API Key Setup Script for Sports Prediction Platform
Configure API-Sports key for all 4 leagues (NHL, NFL, NBA, MLB)
"""

import os
import sys
import json
from pathlib import Path


def setup_api_key(api_key=None):
    """
    Set up API key for sports data integration
    Supports 3 methods:
    1. Command line argument
    2. User input prompt
    3. Environment variable
    """
    
    config_file = Path(__file__).parent / ".api_config.json"
    
    # Method 1: API key provided as argument
    if api_key:
        print(f"✅ Using provided API key: {api_key[:10]}...")
        
        config = {
            "api_key": api_key,
            "provider": "api-sports.io",
            "configured": True,
            "timestamp": str(Path.cwd())
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set environment variable
        os.environ['APISPORTS_KEY'] = api_key
        
        print(f"✅ API Key saved to: {config_file}")
        print(f"✅ Environment variable APISPORTS_KEY set")
        return True
    
    # Method 2: User input
    print("\n" + "=" * 70)
    print("SPORTS PREDICTION PLATFORM - API KEY SETUP")
    print("=" * 70)
    print("\nTo get your FREE API key:")
    print("1. Visit: https://www.api-sports.io/")
    print("2. Sign up (free tier available)")
    print("3. Go to your dashboard and copy your API key")
    print("4. Paste it below\n")
    
    api_key = input("Enter your API-Sports.io API key: ").strip()
    
    if not api_key:
        print("❌ No API key entered. Setup cancelled.")
        return False
    
    if len(api_key) < 10:
        print("❌ Invalid API key (too short)")
        return False
    
    # Save configuration
    config = {
        "api_key": api_key,
        "provider": "api-sports.io",
        "configured": True,
        "leagues": ["NHL", "NFL", "NBA", "MLB"]
    }
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set environment variable
        os.environ['APISPORTS_KEY'] = api_key
        
        print("\n" + "=" * 70)
        print("✅ API KEY CONFIGURATION SUCCESSFUL")
        print("=" * 70)
        print(f"✅ API Key saved to: {config_file}")
        print(f"✅ Environment variable APISPORTS_KEY set")
        print("\nYou can now use the dashboard with live game data!")
        print("=" * 70 + "\n")
        
        return True
    
    except Exception as e:
        print(f"❌ Error saving API key: {e}")
        return False


def load_api_key():
    """Load API key from config file or environment"""
    
    config_file = Path(__file__).parent / ".api_config.json"
    
    # Try config file first
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                return config.get('api_key')
        except:
            pass
    
    # Try environment variable
    return os.environ.get('APISPORTS_KEY')


def check_api_status():
    """Check if API is configured and test connection"""
    
    api_key = load_api_key()
    
    if not api_key:
        print("❌ API Key NOT Configured")
        print("\nTo configure API key, run:")
        print("  python setup_api_key.py")
        print("\nOr set environment variable:")
        print("  set APISPORTS_KEY=your-api-key")
        return False
    
    print("✅ API Key Found:", api_key[:10] + "***" + api_key[-5:])
    
    # Test connection
    try:
        import requests
        
        headers = {"x-apisports-key": api_key}
        
        # Test with simple request
        response = requests.get(
            "https://v1.american-football.api-sports.io/games",
            headers=headers,
            params={"season": 2025},
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ API Connection: WORKING")
            return True
        else:
            print(f"⚠️ API Response Code: {response.status_code}")
            if response.status_code == 401:
                print("❌ Invalid API key (401 Unauthorized)")
            elif response.status_code == 403:
                print("❌ Access forbidden (403)")
            else:
                print(f"⚠️ API returned: {response.text[:100]}")
            return False
    
    except Exception as e:
        print(f"⚠️ API Connection Test: {str(e)}")
        print("(This is OK if you're offline - API will work when online)")
        return True


def show_setup_options():
    """Display setup menu"""
    
    print("\n" + "=" * 70)
    print("SETUP OPTIONS")
    print("=" * 70)
    print("1. Configure new API key (interactive)")
    print("2. Check API key status")
    print("3. Show environment variable (Linux/Mac)")
    print("4. Show environment variable (Windows PowerShell)")
    print("5. Exit")
    print("=" * 70)
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        setup_api_key()
    elif choice == "2":
        check_api_status()
    elif choice == "3":
        print("\nLinux/Mac/Git Bash:")
        print("  export APISPORTS_KEY=your-api-key")
    elif choice == "4":
        print("\nWindows PowerShell:")
        print("  $env:APISPORTS_KEY='your-api-key'")
        print("\nWindows CMD:")
        print("  set APISPORTS_KEY=your-api-key")
    elif choice == "5":
        print("Exiting...")
        return False
    
    return True


if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        # Command line API key provided
        api_key = sys.argv[1]
        setup_api_key(api_key)
    else:
        # Interactive mode
        while True:
            if not show_setup_options():
                break
            
            again = input("\nContinue? (y/n): ").strip().lower()
            if again != 'y':
                break
