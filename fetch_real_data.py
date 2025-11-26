"""
Real Data Fetcher - Fetch Live Game Data from API-Sports
Uses real API key to get current game data for all 4 leagues
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class RealDataFetcher:
    """Fetch real live game data from API-Sports"""
    
    def __init__(self, api_key: str = None):
        """Initialize with API key"""
        self.api_key = api_key or os.getenv('APISPORTS_KEY')
        
        if not self.api_key:
            raise ValueError("API key not found. Set APISPORTS_KEY in .env or environment")
        
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'api-sports.io'
        }
        
        self.base_urls = {
            'NFL': 'https://v1.american-football.api-sports.io',
            'NHL': 'https://v1.hockey.api-sports.io',
            'NBA': 'https://v1.basketball.api-sports.io',
            'MLB': 'https://v1.baseball.api-sports.io'
        }
        
        print(f"✓ Real Data Fetcher initialized with API key: {self.api_key[:10]}...")
    
    def fetch_today_games(self, sport: str) -> List[Dict]:
        """Fetch games for today"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.fetch_games(sport, date=today)
    
    def fetch_games(self, sport: str, date: str = None) -> List[Dict]:
        """
        Fetch games for a specific date
        
        Args:
            sport: 'NFL', 'NHL', 'NBA', or 'MLB'
            date: Date string 'YYYY-MM-DD' or None for today
        
        Returns:
            List of game dictionaries
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        base_url = self.base_urls.get(sport)
        if not base_url:
            raise ValueError(f"Unknown sport: {sport}")
        
        url = f"{base_url}/games"
        params = {'date': date}
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            games = data.get('response', [])
            
            print(f"✓ {sport}: {len(games)} games on {date}")
            return games
        
        except requests.exceptions.RequestException as e:
            print(f"✗ {sport}: Failed to fetch - {str(e)}")
            return []
    
    def fetch_live_games(self, sport: str) -> List[Dict]:
        """Fetch currently live games"""
        base_url = self.base_urls.get(sport)
        if not base_url:
            raise ValueError(f"Unknown sport: {sport}")
        
        url = f"{base_url}/games"
        params = {'live': 'all'}  # Get all live games
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            games = data.get('response', [])
            
            print(f"✓ {sport}: {len(games)} live games")
            return games
        
        except requests.exceptions.RequestException as e:
            print(f"✗ {sport}: Failed to fetch live games - {str(e)}")
            return []
    
    def fetch_team_standings(self, sport: str, season: int = None) -> Dict:
        """Fetch team standings"""
        if not season:
            season = datetime.now().year
        
        base_url = self.base_urls.get(sport)
        if not base_url:
            raise ValueError(f"Unknown sport: {sport}")
        
        url = f"{base_url}/standings"
        params = {'season': season}
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            standings = data.get('response', {})
            
            print(f"✓ {sport}: Standings fetched for season {season}")
            return standings
        
        except requests.exceptions.RequestException as e:
            print(f"✗ {sport}: Failed to fetch standings - {str(e)}")
            return {}
    
    def fetch_all_today(self) -> Dict[str, List[Dict]]:
        """Fetch today's games for all 4 leagues"""
        print("\n" + "="*70)
        print("FETCHING TODAY'S LIVE GAMES - ALL 4 LEAGUES")
        print("="*70 + "\n")
        
        all_games = {}
        
        for sport in ['NFL', 'NHL', 'NBA', 'MLB']:
            games = self.fetch_today_games(sport)
            all_games[sport] = games
        
        return all_games
    
    def format_game_display(self, game: Dict, sport: str) -> str:
        """Format game data for display"""
        try:
            if sport == 'NFL':
                home = game.get('teams', {}).get('home', {}).get('name', 'Home')
                away = game.get('teams', {}).get('away', {}).get('name', 'Away')
                status = game.get('status', {}).get('long', 'Scheduled')
                home_score = game.get('scores', {}).get('home', '-')
                away_score = game.get('scores', {}).get('away', '-')
            elif sport == 'NHL':
                home = game.get('teams', {}).get('home', {}).get('name', 'Home')
                away = game.get('teams', {}).get('away', {}).get('name', 'Away')
                status = game.get('status', 'Scheduled')
                home_score = game.get('goals', {}).get('home', '-')
                away_score = game.get('goals', {}).get('away', '-')
            elif sport == 'NBA':
                home = game.get('teams', {}).get('home', {}).get('name', 'Home')
                away = game.get('teams', {}).get('away', {}).get('name', 'Away')
                status = game.get('status', 'Scheduled')
                home_score = game.get('scores', {}).get('home', {}).get('points', '-')
                away_score = game.get('scores', {}).get('away', {}).get('points', '-')
            elif sport == 'MLB':
                home = game.get('teams', {}).get('home', {}).get('name', 'Home')
                away = game.get('teams', {}).get('away', {}).get('name', 'Away')
                status = game.get('status', 'Scheduled')
                home_score = game.get('scores', {}).get('home', '-')
                away_score = game.get('scores', {}).get('away', '-')
            else:
                return "Unknown sport"
            
            return f"{away} @ {home} | {away_score}-{home_score} | {status}"
        
        except Exception as e:
            return f"Error formatting: {str(e)}"


def main():
    """Main execution"""
    try:
        # Initialize fetcher with real API key
        fetcher = RealDataFetcher()
        
        # Fetch today's games
        all_games = fetcher.fetch_all_today()
        
        # Display results
        print("\n" + "="*70)
        print("TODAY'S GAMES SUMMARY")
        print("="*70 + "\n")
        
        for sport, games in all_games.items():
            print(f"\n{sport} ({len(games)} games):")
            print("-" * 70)
            
            if games:
                for i, game in enumerate(games[:5], 1):  # Show first 5
                    display = fetcher.format_game_display(game, sport)
                    print(f"  {i}. {display}")
                
                if len(games) > 5:
                    print(f"  ... and {len(games) - 5} more games")
            else:
                print("  No games today")
        
        # Save to JSON for dashboard use
        output_file = Path('live_games_today.json')
        with open(output_file, 'w') as f:
            json.dump(all_games, f, indent=2, default=str)
        
        print("\n" + "="*70)
        print(f"✓ Data saved to {output_file}")
        print("="*70 + "\n")
        
        return True
    
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nSetup Instructions:")
        print("1. Get API key from: https://www.api-sports.io/")
        print("2. Add to .env file: APISPORTS_KEY=your-key")
        print("3. Or set environment: export APISPORTS_KEY=your-key")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
