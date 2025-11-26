"""
Generate NBA game data from NFL template for testing/demo purposes
This creates realistic NBA game data with proper schema matching NFL/MLB format
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# NBA teams
NBA_TEAMS = [
    "Boston Celtics", "Brooklyn Nets", "New York Knicks", "Philadelphia 76ers",
    "Toronto Raptors", "Chicago Bulls", "Cleveland Cavaliers", "Detroit Pistons",
    "Indiana Pacers", "Milwaukee Bucks", "Atlanta Hawks", "Charlotte Hornets",
    "Miami Heat", "Orlando Magic", "Washington Wizards", "Denver Nuggets",
    "Minnesota Timberwolves", "Oklahoma City Thunder", "Portland Trail Blazers",
    "Utah Jazz", "Golden State Warriors", "LA Clippers", "Los Angeles Lakers",
    "Phoenix Suns", "Sacramento Kings"
]

def generate_nba_games(num_games=1230, season_start=2023):
    """Generate NBA game data"""
    np.random.seed(42)
    
    games = []
    game_id = 1
    
    # Generate games throughout the season
    season_start_date = datetime(season_start, 10, 1)  # NBA season starts in October
    
    for i in range(num_games):
        # Distribute games across the season (Oct-June is ~270 days)
        days_offset = int((i / num_games) * 270)
        game_date = season_start_date + timedelta(days=days_offset)
        
        # Random teams
        home_idx = np.random.randint(0, len(NBA_TEAMS))
        away_idx = np.random.randint(0, len(NBA_TEAMS))
        while away_idx == home_idx:
            away_idx = np.random.randint(0, len(NBA_TEAMS))
        
        home_team = NBA_TEAMS[home_idx]
        away_team = NBA_TEAMS[away_idx]
        
        # NBA scores are typically 95-115 (higher scoring than other sports)
        home_score = int(np.random.normal(105, 10))
        away_score = int(np.random.normal(100, 10))
        home_score = max(50, min(150, home_score))  # Realistic bounds
        away_score = max(50, min(150, away_score))
        
        # Add quarters (4 quarters in NBA)
        q_scores_home = np.random.multinomial(home_score, [0.25, 0.25, 0.25, 0.25])
        q_scores_away = np.random.multinomial(away_score, [0.25, 0.25, 0.25, 0.25])
        
        games.append({
            'league': 'NBA',
            'season': season_start,
            'game_id': game_id,
            'date': game_date.strftime('%Y-%m-%d'),
            'week': (days_offset // 7) + 1,
            'time': f"{np.random.randint(18, 21):02d}:{np.random.randint(0, 60):02d}",
            'timezone': 'EST',
            'stage': 'Regular Season',
            'referee': f"Referee {np.random.randint(1, 50)}",
            'status_short': 'FT',
            'status_long': 'Match Finished',
            'venue_name': f"{home_team} Arena",
            'venue_city': 'City',
            'venue_surface': 'Court',
            'home_team_id': home_idx,
            'home_team_name': home_team,
            'home_team_logo': f"logo_{home_idx}",
            'home_winner': 1 if home_score > away_score else 0,
            'away_team_id': away_idx,
            'away_team_name': away_team,
            'away_team_logo': f"logo_{away_idx}",
            'away_winner': 1 if away_score > home_score else 0,
            'home_score_total': home_score,
            'away_score_total': away_score,
            'home_score_q1': q_scores_home[0],
            'home_score_q2': q_scores_home[1],
            'home_score_q3': q_scores_home[2],
            'home_score_q4': q_scores_home[3],
            'away_score_q1': q_scores_away[0],
            'away_score_q2': q_scores_away[1],
            'away_score_q3': q_scores_away[2],
            'away_score_q4': q_scores_away[3],
            'total_points': home_score + away_score,
            'odds_home': round(np.random.uniform(1.5, 2.5), 2),
            'odds_away': round(np.random.uniform(1.5, 2.5), 2),
            'odds_draw': None,
            'over_under_line': round(np.random.normal(210, 15), 1)
        })
        
        game_id += 1
    
    return pd.DataFrame(games)

if __name__ == "__main__":
    print("Generating NBA game data...")
    df_nba = generate_nba_games(num_games=1230, season_start=2023)
    
    output_file = "nba_games.csv"
    df_nba.to_csv(output_file, index=False)
    
    print(f"✓ Generated {len(df_nba)} NBA games")
    print(f"✓ Saved to {output_file}")
    print(f"\nColumns: {df_nba.columns.tolist()}")
    print(f"\nSample data:\n{df_nba.head()}")
