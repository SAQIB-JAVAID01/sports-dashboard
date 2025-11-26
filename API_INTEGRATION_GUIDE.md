# Multi-League API Integration Guide

## Overview

The Sports Prediction Dashboard now supports **real-time API integration** for all 4 leagues:
- 🏀 NBA
- 🏈 NFL  
- 🏒 NHL
- ⚾ MLB

## Quick Setup (2 minutes)

### Step 1: Get API Key
1. Visit https://api-sports.io
2. Create a free account
3. Copy your API key from the dashboard

### Step 2: Configure Dashboard
Run one of these commands:

**Option A: Python Script**
```bash
python -c "from src.multi_league_api import setup_api_key; setup_api_key('YOUR-API-KEY')"
```

**Option B: Environment Variable**
```bash
# Windows (PowerShell)
$env:APISPORTS_KEY='YOUR-API-KEY'

# Windows (CMD)
set APISPORTS_KEY=YOUR-API-KEY

# Mac/Linux
export APISPORTS_KEY='YOUR-API-KEY'
```

**Option C: Create .env file**
```
APISPORTS_KEY=YOUR-API-KEY
```

### Step 3: Restart Dashboard
```bash
python -m streamlit run comprehensive_sports_dashboard.py --server.port 8505
```

## Features Unlocked

✅ **Live Game Scores** - See real-time scores across all 4 leagues  
✅ **Today's Games** - View all games scheduled for today  
✅ **Team Statistics** - Access detailed team performance data  
✅ **League Standings** - View current standings and rankings  
✅ **Betting Odds** - Get real-time odds information  
✅ **Multi-League Summary** - Dashboard showing all leagues at once  

## API Usage Examples

### Get Live Games (All Leagues)
```python
from src.multi_league_api import get_multi_league_api

api = get_multi_league_api()

# Get live games across all 4 leagues
live_games = api.get_all_live_games()
print(f"Live NBA games: {len(live_games.get('NBA', []))}")
print(f"Live NFL games: {len(live_games.get('NFL', []))}")
print(f"Live NHL games: {len(live_games.get('NHL', []))}")
print(f"Live MLB games: {len(live_games.get('MLB', []))}")
```

### Get Today's Games
```python
# Get all games today across all leagues
today_games = api.get_all_today_games()

for sport, games in today_games.items():
    print(f"{sport}: {len(games)} games")
```

### Get Team Information
```python
# Get all NBA teams
nba_teams = api.get_teams('NBA')
for team in nba_teams:
    print(f"  {team['name']}")

# Get all NFL teams
nfl_teams = api.get_teams('NFL')

# Get all NHL teams
nhl_teams = api.get_teams('NHL')

# Get all MLB teams
mlb_teams = api.get_teams('MLB')
```

### Get League Standings
```python
# Get NBA standings for current season
nba_standings = api.get_standings('NBA', '2024-2025')

# Get NFL standings
nfl_standings = api.get_standings('NFL', '2024')

# Get NHL standings
nhl_standings = api.get_standings('NHL', '2024-2025')

# Get MLB standings
mlb_standings = api.get_standings('MLB', '2024')
```

### Test API Connection
```python
# Test connection for specific league
is_connected = api.test_connection('NHL')

# Test all leagues
connections = api.test_all_connections()
for sport, status in connections.items():
    print(f"{sport}: {'Online' if status else 'Offline'}")
```

### Get League Summary
```python
# Get comprehensive summary of all leagues
summary = api.get_league_summary()
print(summary)
# Output:
# {
#   'timestamp': '2025-11-26T20:30:00',
#   'leagues': {
#     'NBA': {'live_games': 3, 'total_teams': 30, 'status': 'Online'},
#     'NFL': {'live_games': 0, 'total_teams': 32, 'status': 'Online'},
#     'NHL': {'live_games': 5, 'total_teams': 32, 'status': 'Online'},
#     'MLB': {'live_games': 0, 'total_teams': 30, 'status': 'Online'}
#   }
# }
```

## API Rate Limiting

- **Free Tier**: 100 requests/day
- **Pro Tier**: 5,000 requests/day
- **Enterprise**: Unlimited

The dashboard includes:
- ✅ Automatic rate limiting (100ms between requests)
- ✅ Request caching (5 minute TTL)
- ✅ Parallel requests (max 4 concurrent)
- ✅ Error handling and graceful degradation

## Troubleshooting

### API Key Not Working
```
Error: API Error: Invalid API key
```
**Solution:**
1. Verify key from https://api-sports.io/dashboard
2. Check for leading/trailing spaces
3. Ensure key is for v1 (not older versions)

### Rate Limit Exceeded
```
Error: API Request failed: 429 Too Many Requests
```
**Solution:**
1. Wait a few minutes
2. Upgrade to Pro tier at api-sports.io
3. Reduce request frequency

### Connection Timeout
```
Error: API Request failed: Connection timeout
```
**Solution:**
1. Check internet connection
2. Verify firewall allows outbound HTTPS
3. Try again in a few moments

### Module Not Found
```
Error: No module named 'multi_league_api'
```
**Solution:**
```bash
# Reinstall dependencies
pip install requests pandas
```

## Dashboard Integration

The API is automatically integrated into the **Export tab**:

1. **Live Games Section**
   - Shows real-time scores
   - Displays live games from all 4 leagues
   - Updates when you visit the Export tab

2. **Today's Games Summary**
   - Game count for each league
   - Quick overview of daily schedule

3. **League Status**
   - Shows which leagues are online
   - Connection status for each API

## Performance Tips

1. **Use Caching**
   - API responses cached for 5 minutes
   - Reduces duplicate requests
   - Improves dashboard responsiveness

2. **Parallel Requests**
   - All 4 leagues fetched simultaneously
   - Complete league summary in ~1 second

3. **Selective Updates**
   - Only fetch what you need
   - Use date filters for specific games
   - Limit results to reduce bandwidth

## API Documentation

Full API-Sports documentation: https://api-sports.io/documentation

- Games: Get games, live scores, play-by-play
- Teams: Team info, rosters, logos
- Standings: League standings, records
- Statistics: Team and player statistics
- Odds: Betting lines and odds
- Injuries: Player injury reports

## Support

For API issues:
- API-Sports Support: https://api-sports.io/support
- GitHub Issues: Report bugs in dashboard

For Dashboard integration issues:
- Check configuration: `api.test_all_connections()`
- View cache: `api.get_cached_data_info()`
- Clear cache: `api.clear_cache()`

## Free vs Paid Plans

| Feature | Free | Pro | Enterprise |
|---------|------|-----|-----------|
| **Requests/Day** | 100 | 5,000 | Unlimited |
| **Concurrent Requests** | 1 | 10 | Unlimited |
| **API Support** | Email | Priority | Dedicated |
| **SLA** | - | 99.5% | 99.9% |
| **Price** | Free | $99/mo | Custom |

Start free and upgrade if needed!
