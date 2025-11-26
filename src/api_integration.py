"""
Real-Time API Integration Module
Connects to API-Sports for live game data, odds, and team statistics
"""

import requests
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
import time


class APISportsIntegration:
    """
    Real-time sports data integration using API-Sports
    
    Supports: NHL, NFL, NBA, MLB
    Documentation: https://api-sports.io/documentation
    """
    
    BASE_URLS = {
        'NFL': 'https://v1.american-football.api-sports.io',
        'NBA': 'https://v1.basketball.api-sports.io',
        'MLB': 'https://v1.baseball.api-sports.io',
        'NHL': 'https://v1.hockey.api-sports.io'
    }
    
    LEAGUE_IDS = {
        'NFL': 1,   # NFL
        'NBA': 12,  # NBA
        'MLB': 1,   # MLB
        'NHL': 57   # NHL
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize API client
        
        Args:
            api_key: API-Sports API key (or set APISPORTS_KEY environment variable)
        """
        self.api_key = api_key or os.getenv('APISPORTS_KEY')
        
        if not self.api_key:
            # Try loading from .env file
            env_file = Path('.env')
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.startswith('APISPORTS_KEY='):
                            self.api_key = line.split('=', 1)[1].strip().strip('"\'')
                            break
        
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'api-sports.io'
        }
        
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, sport: str, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with error handling
        
        Args:
            sport: Sport name (NHL, NFL, NBA, MLB)
            endpoint: API endpoint (e.g., '/games')
            params: Query parameters
        
        Returns:
            API response as dictionary
        """
        if sport not in self.BASE_URLS:
            raise ValueError(f"Unsupported sport: {sport}")
        
        if not self.api_key:
            raise ValueError("API key not configured. Set APISPORTS_KEY environment variable or pass to constructor.")
        
        self._rate_limit()
        
        url = f"{self.BASE_URLS[sport]}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check API response status
            if 'errors' in data and data['errors']:
                raise Exception(f"API Error: {data['errors']}")
            
            return data
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Request failed: {str(e)}")
    
    def get_games(
        self,
        sport: str,
        date: str = None,
        season: str = None,
        team_id: int = None,
        status: str = None
    ) -> List[Dict]:
        """
        Get games for a sport
        
        Args:
            sport: Sport name (NHL, NFL, NBA, MLB)
            date: Date in YYYY-MM-DD format (default: today)
            season: Season year (e.g., '2024' for NFL/MLB, '2024-2025' for NBA/NHL)
            team_id: Filter by team ID
            status: Game status ('scheduled', 'live', 'finished')
        
        Returns:
            List of game dictionaries
        """
        params = {
            'league': self.LEAGUE_IDS[sport]
        }
        
        if date:
            params['date'] = date
        if season:
            params['season'] = season
        if team_id:
            params['team'] = team_id
        if status:
            params['status'] = status
        
        response = self._make_request(sport, '/games', params)
        return response.get('response', [])
    
    def get_today_games(self, sport: str) -> List[Dict]:
        """Get today's games for a sport"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_games(sport, date=today)
    
    def get_live_games(self, sport: str) -> List[Dict]:
        """Get currently live games"""
        return self.get_games(sport, status='live')
    
    def get_odds(self, sport: str, game_id: int) -> Dict:
        """
        Get betting odds for a specific game
        
        Args:
            sport: Sport name
            game_id: Game ID from API
        
        Returns:
            Odds dictionary
        """
        params = {
            'game': game_id
        }
        
        response = self._make_request(sport, '/odds', params)
        return response.get('response', [])
    
    def get_teams(self, sport: str, season: str = None) -> List[Dict]:
        """
        Get teams for a sport
        
        Args:
            sport: Sport name
            season: Season year
        
        Returns:
            List of team dictionaries
        """
        params = {
            'league': self.LEAGUE_IDS[sport]
        }
        
        if season:
            params['season'] = season
        
        response = self._make_request(sport, '/teams', params)
        return response.get('response', [])
    
    def get_standings(self, sport: str, season: str) -> List[Dict]:
        """
        Get league standings
        
        Args:
            sport: Sport name
            season: Season year
        
        Returns:
            Standings data
        """
        params = {
            'league': self.LEAGUE_IDS[sport],
            'season': season
        }
        
        response = self._make_request(sport, '/standings', params)
        return response.get('response', [])
    
    def get_team_statistics(self, sport: str, team_id: int, season: str) -> Dict:
        """
        Get team statistics
        
        Args:
            sport: Sport name
            team_id: Team ID
            season: Season year
        
        Returns:
            Team statistics dictionary
        """
        params = {
            'team': team_id,
            'season': season
        }
        
        response = self._make_request(sport, '/statistics', params)
        return response.get('response', {})
    
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    def test_connection(self, sport: str = 'NHL') -> bool:
        """
        Test API connection
        
        Args:
            sport: Sport to test (default: NHL)
        
        Returns:
            True if connection successful
        """
        try:
            teams = self.get_teams(sport)
            return len(teams) > 0
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


# Convenience functions
def get_api_client(api_key: str = None) -> APISportsIntegration:
    """Get configured API client"""
    return APISportsIntegration(api_key)


def setup_api_key(api_key: str):
    """
    Save API key to .env file
    
    Args:
        api_key: Your API-Sports key
    """
    env_file = Path('.env')
    
    # Read existing content
    lines = []
    if env_file.exists():
        with open(env_file) as f:
            lines = [line for line in f if not line.startswith('APISPORTS_KEY=')]
    
    # Add API key
    lines.append(f'APISPORTS_KEY={api_key}\n')
    
    # Write back
    with open(env_file, 'w') as f:
        f.writelines(lines)
    
    print(f"✓ API key saved to {env_file}")
    print("You can now use: api_client = get_api_client()")
