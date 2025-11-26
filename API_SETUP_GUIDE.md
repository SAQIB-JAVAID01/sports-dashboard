# API Configuration Guide

## Quick Start (5 Minutes)

### Step 1: Get Free API Key
1. Visit: https://www.api-sports.io/
2. Click "Sign Up" (free tier available)
3. Create account and verify email
4. Go to Dashboard → Copy your API Key

### Step 2: Configure API Key

**Option A: Interactive Setup (Easiest)**
```bash
python setup_api_key.py
```
Then follow the prompts and paste your API key.

**Option B: Command Line**
```bash
python setup_api_key.py YOUR-API-KEY-HERE
```

**Option C: Environment Variable**

Windows PowerShell:
```powershell
$env:APISPORTS_KEY='your-api-key'
```

Windows CMD:
```cmd
set APISPORTS_KEY=your-api-key
```

Linux/Mac:
```bash
export APISPORTS_KEY='your-api-key'
```

**Option D: .env File**
Create file `.env` in project root:
```
APISPORTS_KEY=your-api-key
```

### Step 3: Verify Configuration
```bash
python setup_api_key.py
# Select option 2 to check status
```

Expected output:
```
✅ API Key Found: xxxxxxxxx***xxxxx
✅ API Connection: WORKING
```

### Step 4: Run Dashboard
```bash
python -m streamlit run comprehensive_sports_dashboard.py --server.port 8505
```

Then use "Export" tab → "Fetch Live Games" to load today's games!

---

## What This Enables

### Live Game Data (All 4 Leagues)
- **NFL**: Real-time game scores, play-by-play
- **NHL**: Live game data, statistics
- **NBA**: Real-time updates, player stats
- **MLB**: Live scores, game events

### Real-Time Features
- ✅ Today's scheduled games
- ✅ Live score updates
- ✅ Team statistics
- ✅ Player performance data
- ✅ Injury reports (NFL/NBA)

### Prediction Integration
- ✅ Use live data in ML predictions
- ✅ Real-time accuracy validation
- ✅ Live probability updates

---

## API Limits

| Tier | Requests/Day | Leagues | Cost |
|------|-------------|---------|------|
| **Free** | 100 | All 4 | Free |
| **Starter** | 1,000 | All 4 | €9.99/mo |
| **Professional** | 100,000+ | All 4 | €99.99/mo |

Free tier is sufficient for:
- Daily predictions (1-2 requests)
- Weekly dashboard checks
- Development/testing

---

## Troubleshooting

### "API Key NOT Configured"
```bash
# Run setup
python setup_api_key.py

# Or set environment variable
set APISPORTS_KEY=your-key
```

### "401 Unauthorized"
Your API key is invalid or expired. Get a new one from api-sports.io

### "403 Forbidden"
You've exceeded your daily request limit. Wait until tomorrow or upgrade plan.

### "Connection timeout"
- Check internet connection
- API might be down (rare)
- Try again in a few seconds

---

## Using API in Dashboard

### Export Tab → Live Games Section
1. Select sport (NFL, NHL, NBA, MLB)
2. Click "Fetch Today's Games"
3. Games load with live data
4. Run ML predictions on live data

### Programmatic Usage
```python
from src.multi_league_api import MultiLeagueAPI

# Initialize with your key
api = MultiLeagueAPI(api_key='YOUR-KEY')

# Get today's games
games = api.get_games_by_date('2025-11-26', sport='NFL')

# Get live scores
scores = api.get_live_scores('NFL')

# Get team stats
stats = api.get_team_stats('New England Patriots', sport='NFL')
```

---

## Features by League

### NFL
- Teams: 32
- Live games, scores, statistics
- Injury reports, player stats
- Playoff/Super Bowl coverage

### NHL
- Teams: 33
- Real-time game updates
- Player statistics
- Stanley Cup tracking

### NBA
- Teams: 30
- Live scores and play-by-play
- Player performance
- Standings and stats

### MLB
- Teams: 30
- Live game feeds
- Player statistics
- Season standings

---

## Support

- API Docs: https://www.api-sports.io/documentation
- Dashboard: https://www.api-sports.io/dashboard
- Email: support@api-sports.io

For dashboard issues, check: `setup_api_key.py` (option 2 for status check)
