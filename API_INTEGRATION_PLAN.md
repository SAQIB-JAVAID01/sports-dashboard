# API Integration Analysis & Implementation Plan

## Current Status Assessment

### ✅ What's Already Implemented
1. **APISportsIntegration Class** (`src/api_integration.py`)
   - ✅ Multi-sport support (NFL, NBA, MLB, NHL)
   - ✅ API endpoint structure defined
   - ✅ Rate limiting implemented
   - ✅ Error handling framework
   - ✅ Methods: get_games(), get_today_games(), get_live_games(), get_odds(), get_teams(), get_standings(), get_team_statistics()

2. **Dashboard Integration** (`comprehensive_sports_dashboard.py`)
   - ✅ Optional API integration (gracefully silent if not configured)
   - ✅ Falls back to CSV data when API unavailable
   - ✅ Displays API status when configured

3. **SportsAPIClient** (`src/api_client.py`)
   - ✅ Basic wrapper structure
   - ✅ API key configuration from environment
   - ✅ Multi-sport support (NFL, NBA, MLB, NHL)

### ❌ What's Missing / Incomplete
1. **Real API Implementation**
   - ❌ Actual HTTP requests to API-Sports endpoints not implemented
   - ❌ Missing live data fetching
   - ❌ No real team statistics integration
   - ❌ No odds/betting data integration
   - ❌ No player data integration

2. **Data Synchronization**
   - ❌ No database to store live data
   - ❌ No caching mechanism
   - ❌ No data refresh scheduling
   - ❌ No team lookup by ID

3. **Error Handling**
   - ⚠️ Partial - basic structure exists but needs refinement

---

## API-Sports Service Available APIs

### 1. **American Football (NFL)**
**Endpoint**: `https://v1.american-football.api-sports.io`
**League ID**: 1

**Available Endpoints**:
- `/games` - Get all games
- `/games?date=YYYY-MM-DD` - Games on specific date
- `/teams` - All NFL teams
- `/teams/{id}` - Specific team data
- `/standings?season=2024` - League standings
- `/statistics?team={id}&season=2024` - Team statistics
- `/players?team={id}&season=2024` - Team roster
- `/odds?game={id}` - Betting odds

---

### 2. **Basketball (NBA)**
**Endpoint**: `https://v1.basketball.api-sports.io`
**League ID**: 12

**Available Endpoints**:
- `/games` - All games
- `/games?date=YYYY-MM-DD` - Games on specific date  
- `/teams` - All NBA teams
- `/standings?season=2024-2025` - League standings
- `/statistics?team={id}&season=2024-2025` - Team stats
- `/players?team={id}&season=2024-2025` - Team roster
- `/odds?game={id}` - Betting odds

---

### 3. **Baseball (MLB)**
**Endpoint**: `https://v1.baseball.api-sports.io`
**League ID**: 1

**Available Endpoints**:
- `/games` - All games
- `/games?date=YYYY-MM-DD` - Games on specific date
- `/teams` - All MLB teams
- `/standings?season=2024` - League standings
- `/statistics?team={id}&season=2024` - Team stats
- `/players?team={id}&season=2024` - Team roster
- `/odds?game={id}` - Betting odds

---

### 4. **Ice Hockey (NHL)**
**Endpoint**: `https://v1.hockey.api-sports.io`
**League ID**: 57

**Available Endpoints**:
- `/games` - All games
- `/games?date=YYYY-MM-DD` - Games on specific date
- `/teams` - All NHL teams
- `/standings?season=2024-2025` - League standings
- `/statistics?team={id}&season=2024-2025` - Team stats
- `/players?team={id}&season=2024-2025` - Team roster
- `/odds?game={id}` - Betting odds

---

## Implementation Requirements

### 1. API Key Setup
```bash
# Option 1: Environment Variable
export APISPORTS_KEY=your_api_key_here

# Option 2: .env file
echo "APISPORTS_KEY=your_api_key_here" > .env

# Get free API key from:
# https://rapidapi.com/api-sports/api/api-sports
```

**Free Tier Limits**:
- 100 requests/day
- Rate limit: 1 request/second

**Paid Tier**:
- Higher request limits
- Priority support
- More endpoints available

---

### 2. Database Structure (Recommended)
```sql
-- Teams Table
CREATE TABLE teams (
    id INT PRIMARY KEY,
    sport VARCHAR(10),
    name VARCHAR(100),
    code VARCHAR(10),
    country VARCHAR(50),
    city VARCHAR(50),
    founded INT,
    logo URL,
    updated_at TIMESTAMP
);

-- Games Table
CREATE TABLE games (
    id INT PRIMARY KEY,
    sport VARCHAR(10),
    date DATETIME,
    home_team_id INT,
    away_team_id INT,
    home_score INT,
    away_score INT,
    status VARCHAR(20),
    odds_available BOOLEAN,
    updated_at TIMESTAMP,
    FOREIGN KEY (home_team_id) REFERENCES teams(id),
    FOREIGN KEY (away_team_id) REFERENCES teams(id)
);

-- Player Stats Table
CREATE TABLE player_stats (
    id INT PRIMARY KEY,
    sport VARCHAR(10),
    player_id INT,
    game_id INT,
    team_id INT,
    points INT,
    assists INT,
    rebounds INT,
    efficiency FLOAT,
    updated_at TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

-- Odds Table
CREATE TABLE odds (
    id INT PRIMARY KEY,
    game_id INT,
    bookmaker VARCHAR(50),
    home_odds FLOAT,
    away_odds FLOAT,
    spread FLOAT,
    over_under FLOAT,
    updated_at TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id)
);
```

---

## Step-by-Step Implementation Plan

### Phase 1: Foundation (Days 1-2)
**Objective**: Get real API working with live data

**Tasks**:
1. ✅ Obtain API-Sports API key
2. ✅ Test API connectivity
3. ✅ Implement real `_make_request()` method
4. ✅ Fetch and cache team data for all 4 sports
5. ✅ Store teams in JSON for quick lookup

**Files to Modify**:
- `src/api_integration.py` - Implement real API calls
- `src/data_cache.py` (NEW) - Create caching layer
- `.env` - Add API key

---

### Phase 2: Live Data Fetching (Days 3-4)
**Objective**: Fetch live games and scores

**Tasks**:
1. Implement `get_games()` with real API calls
2. Implement `get_today_games()` for upcoming games
3. Implement `get_live_games()` for in-progress games
4. Add automatic data refresh every 15 minutes
5. Store games in local SQLite database

**Files to Modify**:
- `src/api_integration.py` - Real game fetching
- `src/database.py` (NEW) - SQLite integration
- `src/scheduler.py` (NEW) - Background refresh tasks

---

### Phase 3: Team & Player Data (Days 5-6)
**Objective**: Get detailed team stats and player data

**Tasks**:
1. Implement `get_teams()` to fetch all teams
2. Implement `get_team_statistics()` for season stats
3. Implement player roster fetching
4. Map player IDs to names (all 4 sports)
5. Store in database for quick queries

**Files to Modify**:
- `src/api_integration.py` - Team/player fetching
- `src/database.py` - Schema extensions
- `src/data_models.py` (NEW) - Team/Player classes

---

### Phase 4: Odds & Betting Data (Days 7-8)
**Objective**: Integrate betting odds

**Tasks**:
1. Implement `get_odds()` for real betting lines
2. Add moneyline, spread, over/under odds
3. Track odds movement (line changes)
4. Implement odds history tracking
5. Use odds in prediction models

**Files to Modify**:
- `src/api_integration.py` - Odds fetching
- `src/database.py` - Odds tables
- `src/advanced_prediction_engine.py` - Use real odds

---

### Phase 5: Dashboard Integration (Days 9-10)
**Objective**: Wire everything together

**Tasks**:
1. Update `comprehensive_sports_dashboard.py` to use live API
2. Add real-time game updates
3. Show live scores in sidebar
4. Display real odds in predictions
5. Add data refresh button

**Files to Modify**:
- `comprehensive_sports_dashboard.py` - Use real API
- `src/api_integration.py` - Final tweaks
- `main.py` - API client initialization

---

## Detailed Implementation Code

### Step 1: Complete API Integration Class

```python
# src/api_integration.py - ENHANCED VERSION

import requests
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import json
import time
from functools import lru_cache

logger = logging.getLogger(__name__)

class APISportsIntegration:
    """Real-time sports data integration using API-Sports"""
    
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
    
    def __init__(self, api_key: str = None):
        """Initialize API client"""
        self.api_key = api_key or os.getenv('APISPORTS_KEY')
        
        if not self.api_key:
            env_file = Path('.env')
            if env_file.exists():
                with open(env_file) as f:
                    for line in f:
                        if line.startswith('APISPORTS_KEY='):
                            self.api_key = line.split('=', 1)[1].strip().strip('"\'')
                            break
        
        self.session = requests.Session()
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.last_request_time = 0
        self.cache = {}
        
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, sport: str, endpoint: str, params: Dict = None) -> Dict:
        """Make actual HTTP request to API-Sports"""
        if not self.api_key:
            raise ValueError("API key not configured")
        
        if sport not in self.BASE_URLS:
            raise ValueError(f"Unsupported sport: {sport}")
        
        self._rate_limit()
        
        url = f"{self.BASE_URLS[sport]}{endpoint}"
        headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'api-sports.io'
        }
        
        try:
            response = self.session.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'errors' in data and data['errors']:
                logger.error(f"API Error: {data['errors']}")
                raise Exception(f"API Error: {data['errors']}")
            
            return data
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"API Request failed: {str(e)}")
    
    def get_teams(self, sport: str, season: str = None) -> List[Dict]:
        """Fetch all teams for a sport"""
        params = {'league': self.LEAGUE_IDS[sport]}
        if season:
            params['season'] = season
        
        data = self._make_request(sport, '/teams', params)
        return data.get('response', [])
    
    def get_games(self, sport: str, date: str = None, season: str = None) -> List[Dict]:
        """Fetch games"""
        params = {'league': self.LEAGUE_IDS[sport]}
        if date:
            params['date'] = date
        if season:
            params['season'] = season
        
        data = self._make_request(sport, '/games', params)
        return data.get('response', [])
    
    def get_today_games(self, sport: str) -> List[Dict]:
        """Get today's games"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.get_games(sport, date=today)
    
    def get_live_games(self, sport: str) -> List[Dict]:
        """Get currently live games"""
        params = {
            'league': self.LEAGUE_IDS[sport],
            'status': 'live'
        }
        data = self._make_request(sport, '/games', params)
        return data.get('response', [])
    
    def get_team_statistics(self, sport: str, team_id: int, season: str = None) -> Dict:
        """Get team statistics"""
        params = {'team': team_id, 'season': season}
        data = self._make_request(sport, '/statistics', params)
        return data.get('response', {})
    
    def get_standings(self, sport: str, season: str = None) -> List[Dict]:
        """Get league standings"""
        params = {'league': self.LEAGUE_IDS[sport]}
        if season:
            params['season'] = season
        
        data = self._make_request(sport, '/standings', params)
        return data.get('response', [])
    
    def get_odds(self, sport: str, game_id: int) -> List[Dict]:
        """Get betting odds for a game"""
        params = {'game': game_id}
        data = self._make_request(sport, '/odds', params)
        return data.get('response', [])
    
    def is_configured(self) -> bool:
        """Check if API is configured"""
        return bool(self.api_key)
    
    def test_connection(self, sport: str = 'NFL') -> bool:
        """Test API connection"""
        try:
            teams = self.get_teams(sport)
            return len(teams) > 0
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
```

---

### Step 2: Caching Layer

```python
# src/data_cache.py (NEW)

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DataCache:
    """Local cache for API data"""
    
    def __init__(self, db_path: str = 'sports_data.db'):
        self.db_path = Path(db_path)
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS teams (
                    id INTEGER PRIMARY KEY,
                    sport TEXT,
                    name TEXT,
                    data TEXT,
                    updated_at TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY,
                    sport TEXT,
                    game_id INTEGER,
                    data TEXT,
                    updated_at TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def cache_teams(self, sport: str, teams: List[Dict]):
        """Cache teams data"""
        with sqlite3.connect(self.db_path) as conn:
            for team in teams:
                conn.execute(
                    '''INSERT OR REPLACE INTO teams (id, sport, name, data, updated_at)
                       VALUES (?, ?, ?, ?, ?)''',
                    (team['id'], sport, team['name'], json.dumps(team), datetime.now())
                )
            conn.commit()
    
    def get_cached_teams(self, sport: str, max_age_hours: int = 24) -> Optional[List[Dict]]:
        """Get cached teams"""
        with sqlite3.connect(self.db_path) as conn:
            cutoff = datetime.now() - timedelta(hours=max_age_hours)
            result = conn.execute(
                'SELECT data FROM teams WHERE sport = ? AND updated_at > ?',
                (sport, cutoff)
            ).fetchall()
            
            return [json.loads(row[0]) for row in result] if result else None
```

---

### Step 3: Environment Setup

```bash
# .env file
APISPORTS_KEY=your_actual_api_key_here

# How to get API key:
# 1. Go to https://rapidapi.com/api-sports/api/api-sports
# 2. Sign up for free account
# 3. Subscribe to the API (free tier available)
# 4. Copy your API key
# 5. Add to .env file above
```

---

### Step 4: Integration in Dashboard

```python
# In comprehensive_sports_dashboard.py

from src.api_integration import APISportsIntegration
from src.data_cache import DataCache

# Initialize at startup
api_client = APISportsIntegration()
cache = DataCache()

# In the main function, add live data section
if api_client.is_configured():
    with st.expander("📊 Live Games"):
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Refresh Live Games"):
                games = api_client.get_today_games(sport)
                st.write(f"Found {len(games)} games today")
                for game in games[:5]:
                    home = game.get('teams', {}).get('home', {})
                    away = game.get('teams', {}).get('away', {})
                    score = game.get('score', {})
                    status = game.get('fixture', {}).get('status', {}).get('short', 'TBD')
                    
                    st.write(f"{home.get('name', 'Home')} {score.get('home', '-')} - {score.get('away', '-')} {away.get('name', 'Away')} ({status})")
```

---

## API Response Examples

### Teams Response
```json
{
    "response": [
        {
            "id": 1,
            "name": "Kansas City Chiefs",
            "code": "KC",
            "country": "United States",
            "founded": 1960,
            "national": false,
            "logo": "https://media.api-sports.io/nfl/teams/1.png"
        }
    ]
}
```

### Games Response
```json
{
    "response": [
        {
            "id": 123456,
            "date": "2024-11-26T20:15:00+00:00",
            "week": 12,
            "status": {
                "long": "Final",
                "short": "FT"
            },
            "league": {
                "id": 1,
                "name": "NFL",
                "season": 2024,
                "logo": "https://media.api-sports.io/nfl/leagues/1.png"
            },
            "teams": {
                "home": {
                    "id": 1,
                    "name": "Kansas City Chiefs",
                    "logo": "https://media.api-sports.io/nfl/teams/1.png"
                },
                "away": {
                    "id": 2,
                    "name": "Buffalo Bills",
                    "logo": "https://media.api-sports.io/nfl/teams/2.png"
                }
            },
            "scores": {
                "home": 27,
                "away": 24
            },
            "odds": [
                {
                    "bookmaker": {
                        "id": 1,
                        "name": "DraftKings"
                    },
                    "lastUpdate": "2024-11-26T20:15:00+00:00",
                    "moneyline": {
                        "home": "-110",
                        "away": "-110"
                    },
                    "spread": {
                        "home": "-3.0",
                        "away": "+3.0"
                    },
                    "totals": {
                        "over": "-110",
                        "under": "-110"
                    }
                }
            ]
        }
    ]
}
```

---

## Testing API Integration

### Test Script
```python
# test_api.py

from src.api_integration import APISportsIntegration

api = APISportsIntegration()

# Test each sport
for sport in ['NFL', 'NBA', 'MLB', 'NHL']:
    print(f"\n{sport}:")
    
    try:
        # Get teams
        teams = api.get_teams(sport)
        print(f"  Teams: {len(teams)} available")
        
        # Get today's games
        games = api.get_today_games(sport)
        print(f"  Today's Games: {len(games)}")
        
        # Get live games
        live = api.get_live_games(sport)
        print(f"  Live Games: {len(live)}")
        
    except Exception as e:
        print(f"  Error: {e}")
```

---

## Cost Analysis

### API-Sports Pricing

| Plan | Price | Requests/Month | Use Case |
|------|-------|----------------|----------|
| Free | $0 | 100 | Testing/Development |
| Starter | $9.99 | 10,000 | Small app |
| Professional | $24.99 | 100,000 | Production app |
| Enterprise | Custom | Unlimited | High traffic |

**Estimated Cost for This Project**:
- Development: Free tier (100 requests/month)
- Testing: Free tier
- Production: Professional tier (~$25/month) for 100,000 requests

---

## Risk Mitigation

### What Could Go Wrong?
1. **API Key Leak** - Keep in .env, never commit
2. **Rate Limiting** - Implement caching and queuing
3. **API Downtime** - Fallback to CSV data
4. **Data Inconsistency** - Version control in database
5. **Cost Overruns** - Monitor request usage

### Solutions
- ✅ Environment variables for secrets
- ✅ SQLite caching layer
- ✅ Fallback to historical data
- ✅ Request logging and monitoring
- ✅ API usage alerts

---

## Timeline & Resources

| Phase | Days | Resources | Status |
|-------|------|-----------|--------|
| Foundation | 2 | API key, testing tools | Ready |
| Live Data | 2 | SQLite, scheduler | Ready |
| Team Data | 2 | Database schema | Ready |
| Odds Data | 2 | Prediction model | Ready |
| Dashboard | 2 | Streamlit updates | Ready |

**Total**: 10 days for full implementation

---

## Summary

### ✅ Is Real API Integration Possible?
**YES, absolutely!**

### ✅ For All 4 Leagues?
**YES - API-Sports supports NFL, NBA, MLB, NHL**

### ✅ With Live Data?
**YES - real-time games, scores, odds, player stats**

### ✅ For All Teams?
**YES - all 32 NFL, 30 MLB, 25 NBA, 26 NHL teams**

### Next Steps
1. Get API-Sports API key (free tier: 100 requests/day)
2. Add to `.env` file
3. Implement real `_make_request()` method
4. Test connectivity
5. Deploy to dashboard

**Cost**: Free to $25/month depending on usage
**Effort**: 10 days for full implementation
**Complexity**: Medium (straightforward API integration)

