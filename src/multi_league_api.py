"""
Multi-League Real-Time API Integration
Unified interface for live data from all 4 leagues (NFL, NHL, NBA, MLB)
"""

import requests
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd


class MultiLeagueAPI:
    """
    Unified API client for all 4 sports leagues
    Manages rate limiting, caching, and parallel requests
    """
    
    # API Configuration for each league
    API_CONFIG = {
        'NFL': {
            'base_url': 'https://v1.american-football.api-sports.io',
            'league_id': 1,
            'host': 'api-sports.io',
            'season_format': 'YYYY'
        },
        'NHL': {
            'base_url': 'https://v1.hockey.api-sports.io',
            'league_id': 57,
            'host': 'api-sports.io',
            'season_format': 'YYYY'
        },
        'NBA': {
            'base_url': 'https://v1.basketball.api-sports.io',
            'league_id': 12,
            'host': 'api-sports.io',
            'season_format': 'YYYY-YYYY'
        },
        'MLB': {
            'base_url': 'https://v1.baseball.api-sports.io',
            'league_id': 1,
            'host': 'api-sports.io',
            'season_format': 'YYYY'
        }
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize API client
        
        API key priority:
        1. Passed as parameter
        2. Environment variable APISPORTS_KEY
        3. Config file .api_config.json
        """
        # Try multiple sources for API key
        self.api_key = api_key or os.getenv('APISPORTS_KEY')
        
        # Try loading from config file
        if not self.api_key:
            config_file = Path(__file__).parent.parent / ".api_config.json"
            if config_file.exists():
                try:
                    with open(config_file) as f:
                        config = json.load(f)
                        self.api_key = config.get('api_key')
                except:
                    pass
        
        # Try loading from .env file
        if not self.api_key:
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
        self.last_request_time = {}
        self.request_cache = {}
        self.cache_timeout = 300  # 5 minutes
        
        # Validation
        self.is_valid = self.validate_configuration()
    
    def validate_configuration(self) -> bool:
        """Validate API configuration"""
        if not self.api_key:
            print("⚠️  Warning: API key not configured. Set APISPORTS_KEY environment variable.")
            return False
        
        if len(self.api_key) < 10:
            print("⚠️  Warning: API key appears invalid (too short).")
            return False
        
        return True
    
    def _rate_limit(self, sport: str):
        """Enforce rate limiting per sport"""
        if sport not in self.last_request_time:
            self.last_request_time[sport] = 0
        
        elapsed = time.time() - self.last_request_time[sport]
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        
        self.last_request_time[sport] = time.time()
    
    def _get_cache_key(self, sport: str, endpoint: str, params: Dict) -> str:
        """Generate cache key for request"""
        params_str = json.dumps(params, sort_keys=True) if params else ""
        return f"{sport}:{endpoint}:{params_str}"
    
    def _make_request(self, sport: str, endpoint: str, params: Dict = None) -> Dict:
        """
        Make API request with caching and error handling
        
        Args:
            sport: Sport name (NFL, NHL, NBA, MLB)
            endpoint: API endpoint (e.g., '/games')
            params: Query parameters
        
        Returns:
            API response as dictionary
        """
        if sport not in self.API_CONFIG:
            raise ValueError(f"Unsupported sport: {sport}. Must be NFL, NHL, NBA, or MLB")
        
        if not self.is_valid:
            raise ValueError("API not properly configured. Set APISPORTS_KEY environment variable.")
        
        # Check cache
        cache_key = self._get_cache_key(sport, endpoint, params)
        if cache_key in self.request_cache:
            cached_data, cached_time = self.request_cache[cache_key]
            if time.time() - cached_time < self.cache_timeout:
                return cached_data
        
        # Rate limit
        self._rate_limit(sport)
        
        # Make request
        config = self.API_CONFIG[sport]
        url = f"{config['base_url']}{endpoint}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Check API response status
            if 'errors' in data and data['errors']:
                raise Exception(f"API Error: {data['errors']}")
            
            # Cache successful response
            self.request_cache[cache_key] = (data, time.time())
            
            return data
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Request failed for {sport}: {str(e)}")
    
    # ============================================================================
    # GAMES ENDPOINTS
    # ============================================================================
    
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
            sport: Sport name (NFL, NHL, NBA, MLB)
            date: Date in YYYY-MM-DD format
            season: Season year
            team_id: Filter by team ID
            status: Game status (scheduled, live, finished)
        
        Returns:
            List of game dictionaries
        """
        params = {
            'league': self.API_CONFIG[sport]['league_id']
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
    
    def get_all_live_games(self) -> Dict[str, List[Dict]]:
        """Get live games across ALL 4 leagues"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.get_live_games, sport): sport
                for sport in ['NFL', 'NHL', 'NBA', 'MLB']
            }
            
            for future in as_completed(futures):
                sport = futures[future]
                try:
                    results[sport] = future.result()
                except Exception as e:
                    print(f"Error fetching live games for {sport}: {e}")
                    results[sport] = []
        
        return results
    
    def get_all_today_games(self) -> Dict[str, List[Dict]]:
        """Get today's games across ALL 4 leagues"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.get_today_games, sport): sport
                for sport in ['NFL', 'NHL', 'NBA', 'MLB']
            }
            
            for future in as_completed(futures):
                sport = futures[future]
                try:
                    results[sport] = future.result()
                except Exception as e:
                    print(f"Error fetching today's games for {sport}: {e}")
                    results[sport] = []
        
        return results
    
    # ============================================================================
    # TEAMS ENDPOINTS
    # ============================================================================
    
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
            'league': self.API_CONFIG[sport]['league_id']
        }
        
        if season:
            params['season'] = season
        
        response = self._make_request(sport, '/teams', params)
        return response.get('response', [])
    
    def get_all_teams(self) -> Dict[str, List[Dict]]:
        """Get teams from ALL 4 leagues"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.get_teams, sport): sport
                for sport in ['NFL', 'NHL', 'NBA', 'MLB']
            }
            
            for future in as_completed(futures):
                sport = futures[future]
                try:
                    results[sport] = future.result()
                except Exception as e:
                    print(f"Error fetching teams for {sport}: {e}")
                    results[sport] = []
        
        return results
    
    # ============================================================================
    # STANDINGS ENDPOINTS
    # ============================================================================
    
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
            'league': self.API_CONFIG[sport]['league_id'],
            'season': season
        }
        
        response = self._make_request(sport, '/standings', params)
        return response.get('response', [])
    
    def get_all_standings(self, season: str = None) -> Dict[str, List[Dict]]:
        """Get standings from ALL 4 leagues"""
        if not season:
            season = str(datetime.now().year)
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.get_standings, sport, season): sport
                for sport in ['NFL', 'NHL', 'NBA', 'MLB']
            }
            
            for future in as_completed(futures):
                sport = futures[future]
                try:
                    results[sport] = future.result()
                except Exception as e:
                    print(f"Error fetching standings for {sport}: {e}")
                    results[sport] = []
        
        return results
    
    # ============================================================================
    # STATISTICS ENDPOINTS
    # ============================================================================
    
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
    
    # ============================================================================
    # ODDS ENDPOINTS
    # ============================================================================
    
    def get_odds(self, sport: str, game_id: int) -> List[Dict]:
        """
        Get betting odds for a specific game
        
        Args:
            sport: Sport name
            game_id: Game ID from API
        
        Returns:
            Odds list
        """
        params = {
            'game': game_id
        }
        
        response = self._make_request(sport, '/odds', params)
        return response.get('response', [])
    
    def get_game_odds(self, sport: str, games: List[Dict]) -> List[Dict]:
        """
        Get odds for multiple games
        
        Args:
            sport: Sport name
            games: List of game dictionaries
        
        Returns:
            Games with odds information
        """
        games_with_odds = []
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self.get_odds, sport, game['id']): game
                for game in games[:10]  # Limit to 10 to avoid rate limiting
            }
            
            for future in as_completed(futures):
                game = futures[future]
                try:
                    odds = future.result()
                    game['odds'] = odds
                    games_with_odds.append(game)
                except Exception as e:
                    game['odds'] = []
                    games_with_odds.append(game)
        
        return games_with_odds
    
    # ============================================================================
    # UTILITY & MONITORING
    # ============================================================================
    
    def get_league_summary(self) -> Dict:
        """Get comprehensive summary of all leagues"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'leagues': {}
        }
        
        # Get live games
        live_games = self.get_all_live_games()
        
        # Get teams
        all_teams = self.get_all_teams()
        
        for sport in ['NFL', 'NHL', 'NBA', 'MLB']:
            summary['leagues'][sport] = {
                'live_games': len(live_games.get(sport, [])),
                'total_teams': len(all_teams.get(sport, [])),
                'status': 'Online' if all_teams.get(sport) else 'Offline'
            }
        
        return summary
    
    def test_connection(self, sport: str = 'NHL') -> bool:
        """
        Test API connection for a specific sport
        
        Args:
            sport: Sport to test
        
        Returns:
            True if connection successful
        """
        try:
            teams = self.get_teams(sport)
            return len(teams) > 0
        except Exception as e:
            print(f"Connection test failed for {sport}: {e}")
            return False
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test API connections for all leagues"""
        results = {}
        
        for sport in ['NFL', 'NHL', 'NBA', 'MLB']:
            results[sport] = self.test_connection(sport)
        
        return results
    
    def export_games_to_csv(self, sport: str, date: str, filename: str = None):
        """
        Export games to CSV file
        
        Args:
            sport: Sport name
            date: Date in YYYY-MM-DD format
            filename: Output filename (default: {sport}_{date}.csv)
        """
        if not filename:
            filename = f"{sport}_{date}.csv"
        
        games = self.get_games(sport, date=date)
        
        if not games:
            print(f"No games found for {sport} on {date}")
            return
        
        df = pd.DataFrame(games)
        df.to_csv(filename, index=False)
        print(f"Exported {len(games)} games to {filename}")
    
    def get_cached_data_info(self) -> Dict:
        """Get information about cached data"""
        cache_info = {
            'total_cached_requests': len(self.request_cache),
            'cache_entries': []
        }
        
        for cache_key, (data, timestamp) in self.request_cache.items():
            age = time.time() - timestamp
            cache_info['cache_entries'].append({
                'key': cache_key,
                'age_seconds': round(age, 2),
                'expired': age > self.cache_timeout
            })
        
        return cache_info
    
    def clear_cache(self):
        """Clear all cached data"""
        self.request_cache.clear()
        print("Cache cleared")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_multi_league_api(api_key: str = None) -> MultiLeagueAPI:
    """Get configured multi-league API client"""
    return MultiLeagueAPI(api_key)


def setup_api_key(api_key: str):
    """
    Save API key to .env file
    
    Args:
        api_key: Your API-Sports key (get from https://api-sports.io)
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
    print("You can now use: api = get_multi_league_api()")


# Quick test
if __name__ == '__main__':
    api = get_multi_league_api()
    
    print("=" * 60)
    print("MULTI-LEAGUE API TEST")
    print("=" * 60)
    
    if api.is_valid:
        print("\n✅ API Configuration Valid")
        
        # Test connections
        print("\nTesting connections to all 4 leagues...")
        connections = api.test_all_connections()
        for sport, status in connections.items():
            symbol = "✓" if status else "✗"
            print(f"  {symbol} {sport}: {'Online' if status else 'Offline'}")
        
        # Get league summary
        print("\nFetching league summaries...")
        summary = api.get_league_summary()
        print(json.dumps(summary, indent=2))
    
    else:
        print("\n❌ API Configuration Missing")
        print("To enable API integration:")
        print("1. Get API key from https://api-sports.io")
        print("2. Run: setup_api_key('your-api-key')")
        print("3. Or set environment variable: APISPORTS_KEY=your-api-key")
