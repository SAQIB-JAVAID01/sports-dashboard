"""
Generate synthetic MLB game data to match NFL/NBA schema
Creates realistic baseball games with proper team data, scores, and statistics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# MLB teams
MLB_TEAMS = [
    "Arizona Diamondbacks", "Atlanta Braves", "Baltimore Orioles", "Boston Red Sox",
    "Chicago Cubs", "Chicago White Sox", "Cincinnati Reds", "Cleveland Guardians",
    "Colorado Rockies", "Detroit Tigers", "Houston Astros", "Kansas City Royals",
    "Los Angeles Angels", "Los Angeles Dodgers", "Miami Marlins", "Milwaukee Brewers",
    "Minnesota Twins", "New York Mets", "New York Yankees", "Oakland Athletics",
    "Philadelphia Phillies", "Pittsburgh Pirates", "San Diego Padres", "San Francisco Giants",
    "Seattle Mariners", "St. Louis Cardinals", "Tampa Bay Rays", "Texas Rangers",
    "Toronto Blue Jays", "Washington Nationals"
]

# Generate games
num_games = 1230  # Match NFL/NBA
games = []

# MLB season runs roughly April-October (183 days), but generate across full range for variety
start_date = datetime(2015, 3, 28)  # Common MLB opening day
end_date = datetime(2025, 11, 1)

# Generate random dates
date_range = (end_date - start_date).days
dates = sorted([start_date + timedelta(days=random.randint(0, date_range)) for _ in range(num_games)])

for idx, game_date in enumerate(dates):
    # Select two different teams
    home_team = random.choice(MLB_TEAMS)
    away_team = random.choice([t for t in MLB_TEAMS if t != home_team])
    
    # MLB average scores: home ~4.5, away ~4.2 (slightly favors home)
    home_score = max(0, int(np.random.normal(4.5, 2.5)))
    away_score = max(0, int(np.random.normal(4.2, 2.5)))
    
    # Determine winner (can have ties in baseball stats but games have winners)
    if home_score > away_score:
        home_winner = 1
        away_winner = 0
    else:
        home_winner = 0
        away_winner = 1
    
    # Distribute score across 9 innings (baseball has 9 innings)
    home_q1 = random.randint(0, home_score)
    home_q2 = random.randint(0, home_score - home_q1)
    home_q3 = random.randint(0, home_score - home_q1 - home_q2)
    home_q4 = max(0, home_score - home_q1 - home_q2 - home_q3)
    
    away_q1 = random.randint(0, away_score)
    away_q2 = random.randint(0, away_score - away_q1)
    away_q3 = random.randint(0, away_score - away_q1 - away_q2)
    away_q4 = max(0, away_score - away_q1 - away_q2 - away_q3)
    
    # Create game record
    game = {
        'league': 'MLB',
        'season': game_date.year,
        'game_id': f"MLB_{game_date.strftime('%Y%m%d')}_{idx}",
        'date': game_date.strftime('%Y-%m-%d'),
        'week': game_date.isocalendar()[1],
        'time': f"{random.randint(18, 21):02d}:{random.randint(0, 59):02d}",
        'timezone': 'UTC',
        'stage': 'Regular Season',
        'referee': f"Umpire_{random.randint(1, 50):03d}",
        'status_short': 'FT',
        'status_long': 'Match Finished',
        'venue_name': f"{home_team} Stadium",
        'venue_city': 'City',
        'venue_surface': 'Grass',
        'home_team_id': f"MLB_{home_team.replace(' ', '_')}",
        'home_team_name': home_team,
        'home_team_logo': '',
        'home_winner': home_winner,
        'away_team_id': f"MLB_{away_team.replace(' ', '_')}",
        'away_team_name': away_team,
        'away_team_logo': '',
        'away_winner': away_winner,
        'home_score_total': home_score,
        'away_score_total': away_score,
        'home_score_q1': home_q1,
        'home_score_q2': home_q2,
        'home_score_q3': home_q3,
        'home_score_q4': home_q4,
        'away_score_q1': away_q1,
        'away_score_q2': away_q2,
        'away_score_q3': away_q3,
        'away_score_q4': away_q4,
        'total_points': home_score + away_score,
        'odds_home': round(1.85 + np.random.uniform(-0.2, 0.2), 2),
        'odds_away': round(1.95 + np.random.uniform(-0.2, 0.2), 2),
        'odds_draw': 26.0,  # Draw is rare in baseball
        'over_under_line': round(home_score + away_score + np.random.uniform(-0.5, 0.5), 1),
    }
    
    games.append(game)

# Create DataFrame
df = pd.DataFrame(games)

# Save to CSV
df.to_csv('mlb_games.csv', index=False)

print(f"Generated {len(df)} MLB games")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Unique teams: {len(df['home_team_name'].unique())}")
print(f"Sample teams: {df['home_team_name'].unique()[:5]}")
print(f"Avg home score: {df['home_score_total'].mean():.2f}")
print(f"Avg away score: {df['away_score_total'].mean():.2f}")
print(f"Home win rate: {df['home_winner'].mean():.1%}")
print(f"\nSaved to mlb_games.csv")
