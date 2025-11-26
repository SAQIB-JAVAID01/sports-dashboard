"""
Example: How to Configure API Key for Sports Prediction Dashboard

This file shows all 3 methods to configure the API key.
"""

# ============================================================================
# METHOD 1: INTERACTIVE SETUP (RECOMMENDED - EASIEST)
# ============================================================================
"""
Run this in terminal:
    python setup_api_key.py

Then:
1. Select option 1 (Configure new API key)
2. Go to https://www.api-sports.io/ and sign up (free)
3. Copy your API key from dashboard
4. Paste it in the terminal prompt
5. Done! API key will be saved automatically
"""


# ============================================================================
# METHOD 2: COMMAND LINE SETUP (FASTEST)
# ============================================================================
"""
Replace YOUR-API-KEY with your actual key from api-sports.io:

    python setup_api_key.py YOUR-API-KEY

Example:
    python setup_api_key.py a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6

That's it! Your API key is now configured and saved.
"""


# ============================================================================
# METHOD 3: ENVIRONMENT VARIABLE (BEST FOR DEVELOPMENT)
# ============================================================================

# Windows PowerShell:
# $env:APISPORTS_KEY='your-api-key'

# Windows CMD:
# set APISPORTS_KEY=your-api-key

# Linux/Mac Bash:
# export APISPORTS_KEY='your-api-key'

# Then run dashboard normally:
# python -m streamlit run comprehensive_sports_dashboard.py --server.port 8505


# ============================================================================
# METHOD 4: .ENV FILE (GOOD FOR TEAMS)
# ============================================================================
"""
Create file .env in project root with:

APISPORTS_KEY=your-api-key

Example .env file content:
---
APISPORTS_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
---

Then no need to set anything - it loads automatically.
This file should NOT be committed to git (add to .gitignore)
"""


# ============================================================================
# VERIFY CONFIGURATION
# ============================================================================
"""
After configuring, verify it works:

    python setup_api_key.py

Then select option 2 (Check API key status)

Expected output:
    ✅ API Key Found: xxxxxxxxx***xxxxx
    ✅ API Connection: WORKING

If you see this, everything is set up correctly!
"""


# ============================================================================
# USING THE API IN YOUR CODE
# ============================================================================

from src.multi_league_api import MultiLeagueAPI

# Initialize API (automatically uses configured key)
api = MultiLeagueAPI()

# Get today's NFL games
nfl_games = api.get_games_by_date('2025-11-26', sport='NFL')

# Get live scores for NHL
nhl_scores = api.get_live_scores('NHL')

# Get team statistics
team_stats = api.get_team_stats('New England Patriots', sport='NFL')

# Get all games across all leagues
all_games = api.get_all_games_today()

print("Check API_SETUP_GUIDE.md for more detailed instructions!")
