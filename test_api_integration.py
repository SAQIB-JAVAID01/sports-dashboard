#!/usr/bin/env python
"""
Quick test of Multi-League API Integration
Tests connection to all 4 leagues
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from multi_league_api import get_multi_league_api


def test_api():
    """Test Multi-League API"""
    
    print("\n" + "=" * 70)
    print("MULTI-LEAGUE API INTEGRATION TEST")
    print("=" * 70)
    
    # Initialize API
    api = get_multi_league_api()
    
    print("\n1. CHECKING API CONFIGURATION")
    print("-" * 70)
    if api.is_valid:
        print("✅ API Key Configured")
    else:
        print("❌ API Key NOT Configured")
        print("\nTo configure API key, run:")
        print("  python -c \"from src.multi_league_api import setup_api_key; setup_api_key('YOUR-API-KEY')\"")
        print("\nOr set environment variable:")
        print("  APISPORTS_KEY=your-api-key")
        return
    
    print("\n2. TESTING CONNECTIONS")
    print("-" * 70)
    connections = api.test_all_connections()
    for sport, status in connections.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {sport:4} - {'Online' if status else 'Offline'}")
    
    if not any(connections.values()):
        print("\n⚠️  All connections offline. Check API key and internet connection.")
        return
    
    print("\n3. FETCHING LEAGUE SUMMARY")
    print("-" * 70)
    try:
        summary = api.get_league_summary()
        for sport, data in summary['leagues'].items():
            print(f"\n{sport}:")
            print(f"  Live Games: {data['live_games']}")
            print(f"  Total Teams: {data['total_teams']}")
            print(f"  Status: {data['status']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n4. FETCHING TODAY'S GAMES")
    print("-" * 70)
    try:
        today_games = api.get_all_today_games()
        for sport, games in today_games.items():
            print(f"{sport}: {len(games)} games today")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n5. FETCHING LIVE GAMES")
    print("-" * 70)
    try:
        live_games = api.get_all_live_games()
        for sport, games in live_games.items():
            count = len(games)
            status = "🔴 LIVE" if count > 0 else "No live games"
            print(f"{sport}: {count} games - {status}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n6. FETCHING TEAMS")
    print("-" * 70)
    try:
        all_teams = api.get_all_teams()
        for sport, teams in all_teams.items():
            print(f"{sport}: {len(teams)} teams")
            if teams:
                print(f"  First 3: {', '.join([t['name'] for t in teams[:3]])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n7. CACHE STATISTICS")
    print("-" * 70)
    cache_info = api.get_cached_data_info()
    print(f"Cached Requests: {cache_info['total_cached_requests']}")
    
    print("\n" + "=" * 70)
    print("✅ API TEST COMPLETE")
    print("=" * 70)
    print("\nNext Steps:")
    print("1. Start dashboard: python -m streamlit run comprehensive_sports_dashboard.py")
    print("2. Go to Export tab to see live games")
    print("3. Check API_INTEGRATION_GUIDE.md for more details")
    print()


if __name__ == '__main__':
    test_api()
