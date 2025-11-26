"""
Test API Integration
Tests real API connection for all 4 sports

Usage:
    python test_api.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def test_imports():
    """Test if required modules can be imported"""
    print("\n" + "="*60)
    print("TESTING IMPORTS")
    print("="*60)
    
    modules = ['requests', 'pandas', 'streamlit']
    missing = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - not installed")
            missing.append(module)
    
    if missing:
        print(f"\nInstall missing modules:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def test_api_sports():
    """Test API-Sports connection"""
    print("\n" + "="*60)
    print("TESTING API-SPORTS CONNECTION")
    print("="*60)
    
    api_key = os.getenv('APISPORTS_KEY')
    
    if not api_key:
        print("❌ APISPORTS_KEY not found in environment")
        print("\nSet API key:")
        print("  export APISPORTS_KEY=your_key_here")
        print("  OR add to .env file")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    try:
        from src.api_integration import APISportsIntegration
    except ImportError:
        print("❌ Cannot import APISportsIntegration")
        print("   Make sure you're in the correct directory")
        return False
    
    print("✅ APISportsIntegration imported")
    
    # Initialize client
    api = APISportsIntegration()
    
    if not api.is_configured():
        print("❌ API client not configured")
        return False
    
    print("✅ API client initialized")
    
    # Test each sport
    results = {}
    
    for sport in ['NFL', 'NBA', 'MLB', 'NHL']:
        print(f"\n📊 Testing {sport}...")
        print("-" * 40)
        
        try:
            # Test 1: Get teams
            print(f"  • Fetching {sport} teams...")
            teams = api.get_teams(sport)
            results[sport] = {
                'teams': len(teams),
                'status': 'OK'
            }
            
            print(f"    ✅ {len(teams)} teams available")
            
            # Show sample teams
            if teams:
                sample = teams[:3]
                print(f"    Sample teams:")
                for team in sample:
                    print(f"      - {team.get('name', 'N/A')} (ID: {team.get('id', 'N/A')})")
            
            # Test 2: Get today's games
            print(f"  • Fetching today's {sport} games...")
            games = api.get_today_games(sport)
            print(f"    ✅ {len(games)} games today")
            
            if games:
                game = games[0]
                home = game.get('teams', {}).get('home', {}).get('name', 'Home')
                away = game.get('teams', {}).get('away', {}).get('name', 'Away')
                print(f"    Sample: {home} vs {away}")
            
            # Test 3: Get live games
            print(f"  • Fetching live {sport} games...")
            live = api.get_live_games(sport)
            print(f"    ✅ {len(live)} games live")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:150]}")
            results[sport] = {
                'status': 'FAILED',
                'error': str(e)[:150]
            }
    
    return all(r.get('status') == 'OK' for r in results.values())

def test_data_files():
    """Test CSV data files"""
    print("\n" + "="*60)
    print("TESTING DATA FILES")
    print("="*60)
    
    files = {
        'nfl_games.csv': 'NFL games',
        'mlb_games.csv': 'MLB games',
        'nba_games.csv': 'NBA games',
        'NHL_Dataset/game_plays.csv': 'NHL games'
    }
    
    import pandas as pd
    
    for filepath, description in files.items():
        path = Path(filepath)
        
        if path.exists():
            try:
                df = pd.read_csv(path)
                print(f"✅ {description}: {len(df)} rows")
                
                # Check for team columns
                if 'home_team_name' in df.columns:
                    teams = df['home_team_name'].unique()
                    print(f"   Teams: {len(teams)}")
            except Exception as e:
                print(f"❌ {description}: Error reading file - {e}")
        else:
            print(f"⚠️  {description}: File not found")

def test_database():
    """Test SQLite database"""
    print("\n" + "="*60)
    print("TESTING DATABASE")
    print("="*60)
    
    import sqlite3
    
    db_path = Path('sports_data.db')
    
    if not db_path.exists():
        print("❌ Database not found: sports_data.db")
        print("   Run: python setup_api.py")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if tables:
            print(f"✅ Database has {len(tables)} tables:")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   • {table[0]}: {count} rows")
        else:
            print("❌ No tables found in database")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_cache_file():
    """Test team cache JSON"""
    print("\n" + "="*60)
    print("TESTING CACHE FILE")
    print("="*60)
    
    cache_path = Path('teams_cache.json')
    
    if not cache_path.exists():
        print("⚠️  Cache file not found: teams_cache.json")
        print("   Run: python setup_api.py")
        return False
    
    try:
        import json
        with open(cache_path) as f:
            data = json.load(f)
        
        print(f"✅ Cache file loaded")
        
        for sport, info in data.items():
            count = info.get('count', 0)
            print(f"   • {sport}: {count} teams")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache error: {e}")
        return False

def generate_report():
    """Generate test report"""
    print("\n" + "="*60)
    print("TEST REPORT")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("API Connection", test_api_sports),
        ("Data Files", test_data_files),
        ("Database", test_database),
        ("Cache File", test_cache_file)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            print(f"\n❌ Test {test_name} crashed: {e}")
            results[test_name] = "CRASH"
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, status in results.items():
        icon = "✅" if status == "PASS" else "❌"
        print(f"{icon} {test_name}: {status}")
    
    all_pass = all(status == "PASS" for status in results.values())
    
    if all_pass:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour API integration is ready!")
        print("Next step: python -m streamlit run comprehensive_sports_dashboard.py --server.port 8505")
    else:
        print("\n⚠️  Some tests failed")
        print("Check messages above for details")
    
    return all_pass

def main():
    """Run all tests"""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " API INTEGRATION TEST ".center(58) + "║")
    print("║" + " Verifying all systems are operational ".center(58) + "║")
    print("╚" + "="*58 + "╝")
    
    all_pass = generate_report()
    
    print("\n")
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
