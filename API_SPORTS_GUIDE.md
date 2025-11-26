# API-Sports Integration Guide
## Complete API Endpoints for NFL, NBA, MLB, NHL

---

## 🔗 API Base URLs

```python
API_SPORTS_ENDPOINTS = {
    'NFL': 'https://v1.american-football.api-sports.io',
    'NBA': 'https://v1.basketball.api-sports.io',
    'MLB': 'https://v1.baseball.api-sports.io',
    'NHL': 'https://v1.hockey.api-sports.io'
}
```

## 🏈 League IDs

```python
LEAGUE_IDS = {
    'NFL': 1,      # National Football League
    'NBA': 12,     # National Basketball Association
    'MLB': 1,      # Major League Baseball
    'NHL': 57      # National Hockey League
}
```

---

## 📡 Common Endpoints (All Sports)

### 1. Get Games
```
GET /{sport}/games
Parameters:
  - league: League ID (required)
  - season: Year (e.g., 2025)
  - date: YYYY-MM-DD format
  - timezone: Timezone (default: America/New_York)

Example NFL:
https://v1.american-football.api-sports.io/games?league=1&season=2025

Example NBA:
https://v1.basketball.api-sports.io/games?league=12&season=2024-2025

Example MLB:
https://v1.baseball.api-sports.io/games?league=1&season=2025

Example NHL:
https://v1.hockey.api-sports.io/games?league=57&season=2024-2025
```

### 2. Get Leagues
```
GET /{sport}/leagues
Parameters:
  - id: League ID
  - name: League name
  - country: Country code
  - season: Year

Example:
https://v1.american-football.api-sports.io/leagues?id=1
```

### 3. Get Odds
```
GET /{sport}/odds
Parameters:
  - game: Game ID (required)
  - bookmaker: Bookmaker ID (optional)
  - bet: Bet type (optional)

Example:
https://v1.american-football.api-sports.io/odds?game=12345
```

### 4. Get Teams
```
GET /{sport}/teams
Parameters:
  - league: League ID
  - season: Year
  - name: Team name (search)

Example:
https://v1.basketball.api-sports.io/teams?league=12&season=2024-2025
```

### 5. Get Standings
```
GET /{sport}/standings
Parameters:
  - league: League ID (required)
  - season: Year (required)

Example:
https://v1.hockey.api-sports.io/standings?league=57&season=2024-2025
```

---

## 🔑 Authentication

All requests require API key in headers:

```python
headers = {
    'x-rapidapi-key': 'YOUR_API_KEY_HERE',
    'x-rapidapi-host': 'v1.american-football.api-sports.io'  # Change per sport
}
```

---

## 💻 Python Implementation

```python
import requests
from typing import Dict, List, Optional

class APISportsClient:
    """
    Unified client for API-Sports (all 4 leagues)
    """
    
    BASE_URLS = {
        'NFL': 'https://v1.american-football.api-sports.io',
        'NBA': 'https://v1.basketball.api-sports.io',
        'MLB': 'https://v1.baseball.api-sports.io',
        'NHL': 'https://v1.hockey.api-sports.io'
    }
    
    LEAGUE_IDS = {
        'NFL': 1,
        'NBA': 12,
        'MLB': 1,
        'NHL': 57
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def _get_headers(self, sport: str) -> Dict:
        """Get headers for API request"""
        host = self.BASE_URLS[sport].replace('https://', '')
        return {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': host
        }
    
    def get_games(self, sport: str, date: str = None, season: str = None) -> List[Dict]:
        """
        Fetch games for a sport
        
        Args:
            sport: 'NFL', 'NBA', 'MLB', or 'NHL'
            date: Date in YYYY-MM-DD format (optional)
            season: Season year (optional)
        
        Returns:
            List of game dictionaries
        """
        url = f"{self.BASE_URLS[sport]}/games"
        params = {'league': self.LEAGUE_IDS[sport]}
        
        if date:
            params['date'] = date
        if season:
            params['season'] = season
        
        try:
            response = requests.get(
                url, 
                headers=self._get_headers(sport),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except Exception as e:
            print(f"Error fetching games: {e}")
            return []
    
    def get_odds(self, sport: str, game_id: int) -> List[Dict]:
        """Get betting odds for a game"""
        url = f"{self.BASE_URLS[sport]}/odds"
        params = {'game': game_id}
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(sport),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except Exception as e:
            print(f"Error fetching odds: {e}")
            return []
    
    def get_teams(self, sport: str, season: str = None) -> List[Dict]:
        """Get teams for a league"""
        url = f"{self.BASE_URLS[sport]}/teams"
        params = {'league': self.LEAGUE_IDS[sport]}
        
        if season:
            params['season'] = season
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(sport),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except Exception as e:
            print(f"Error fetching teams: {e}")
            return []
    
    def get_standings(self, sport: str, season: str) -> List[Dict]:
        """Get league standings"""
        url = f"{self.BASE_URLS[sport]}/standings"
        params = {
            'league': self.LEAGUE_IDS[sport],
            'season': season
        }
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(sport),
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
        except Exception as e:
            print(f"Error fetching standings: {e}")
            return []


# Usage Example
if __name__ == "__main__":
    # Initialize client
    client = APISportsClient(api_key="YOUR_API_KEY_HERE")
    
    # Get today's NFL games
    nfl_games = client.get_games('NFL', date='2025-11-26')
    print(f"Found {len(nfl_games)} NFL games")
    
    # Get NHL season 2024-2025
    nhl_games = client.get_games('NHL', season='2024-2025')
    print(f"Found {len(nhl_games)} NHL games this season")
    
    # Get odds for a specific game
    if nfl_games:
        game_id = nfl_games[0]['game']['id']
        odds = client.get_odds('NFL', game_id)
        print(f"Found {len(odds)} bookmakers for game {game_id}")
    
    # Get NBA teams
    nba_teams = client.get_teams('NBA', season='2024-2025')
    print(f"Found {len(nba_teams)} NBA teams")
```

---

## 📊 Response Formats

### Game Response (Example)
```json
{
  "game": {
    "id": 12345,
    "date": "2025-11-26T20:00:00+00:00",
    "time": "20:00",
    "timestamp": 1732651200,
    "week": "Week 12",
    "status": {
      "short": "FT",
      "long": "Finished"
    }
  },
  "league": {
    "id": 1,
    "name": "NFL",
    "season": "2025"
  },
  "teams": {
    "home": {
      "id": 1,
      "name": "Dallas Cowboys",
      "logo": "https://..."
    },
    "away": {
      "id": 2,
      "name": "New York Giants",
      "logo": "https://..."
    }
  },
  "scores": {
    "home": {
      "total": 27
    },
    "away": {
      "total": 20
    }
  }
}
```

### Odds Response (Example)
```json
{
  "bookmaker": {
    "id": 5,
    "name": "DraftKings"
  },
  "bets": [
    {
      "id": 1,
      "name": "Spread",
      "values": [
        {
          "value": "-3.5",
          "odd": "1.91"
        },
        {
          "value": "+3.5",
          "odd": "1.91"
        }
      ]
    },
    {
      "id": 3,
      "name": "Totals",
      "values": [
        {
          "value": "Over 47.5",
          "odd": "1.87"
        },
        {
          "value": "Under 47.5",
          "odd": "1.95"
        }
      ]
    }
  ]
}
```

---

## 🎯 Integration with Your Platform

### Step 1: Add API Key to .env
```bash
# Create .env file in project root
API_SPORTS_KEY=your_api_key_here
```

### Step 2: Update src/api_client.py
Replace the placeholder implementation with the full APISportsClient code above.

### Step 3: Fetch Real-Time Data
```python
from src.api_client import SportsAPIClient
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv('API_SPORTS_KEY')

# Initialize client
client = SportsAPIClient(api_key)

# Get today's games
nfl_games = client.fetch_games('NFL', date='2025-11-26')

# Make predictions
for game in nfl_games:
    game_data = {
        'home_team': game['teams']['home']['name'],
        'away_team': game['teams']['away']['name'],
        'game_date': game['game']['date']
    }
    
    # Use trained model to predict
    prediction = predictor.predict_winner('NFL', game_data)
    print(f"{game_data['home_team']} vs {game_data['away_team']}: {prediction['prediction']} ({prediction['probability']:.1%})")
```

---

## 🔗 API-Sports URLs

- **Main Website:** https://www.api-sports.io/
- **Documentation:** https://www.api-sports.io/documentation/
- **Dashboard:** https://dashboard.api-sports.io/
- **Pricing:** https://www.api-sports.io/pricing/

### Free Tier Limits:
- 100 requests/day
- Limited historical data
- Rate limit: 10 requests/minute

### Pro Tier:
- 10,000+ requests/day
- Full historical data
- Higher rate limits
- Premium support

---

## 📝 Notes

1. **Season Formats:**
   - NFL/MLB: Single year (e.g., "2025")
   - NBA/NHL: Range format (e.g., "2024-2025")

2. **Game Status Codes:**
   - NS: Not Started
   - LIVE: In Progress
   - FT: Finished
   - CANC: Cancelled
   - POST: Postponed

3. **Rate Limiting:**
   - Implement exponential backoff
   - Cache responses when possible
   - Use webhooks for real-time updates (Pro tier)

4. **Betting Odds:**
   - Not all games have odds data
   - Odds updated in real-time during live games
   - Multiple bookmakers available

---

**Created:** November 26, 2025  
**For:** Sports Prediction Platform  
**Status:** Ready for Integration
