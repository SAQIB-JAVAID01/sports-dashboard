"""
Multi-Sport Data Loaders
Unified interface for loading and normalizing NHL, NFL, NBA, MLB data

Key Design Decisions:
- Each sport has different raw data schema
- NHL: Simple 7-column format (season, game_id, date, teams, scores)
- NFL/MLB: Complex 35+ column format (venue, odds, quarters, etc.)
- NBA: Requires API integration for full features

Normalization Strategy:
- All sports converted to common format for ML pipeline
- Common columns: game_date, team_id, opponent_id, team_won, points_scored, points_allowed, is_home
- Sport-specific columns preserved in metadata for advanced features

Usage:
    loader = MultiSportDataLoader()
    df = loader.load_sport_data('NHL', 'nhl_finished_games.csv')
    df = loader.load_sport_data('NFL', 'nfl_games.csv')
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger("data_loaders")


class MultiSportDataLoader:
    """
    Unified data loader for all 4 sports with schema normalization
    """
    
    COMMON_SCHEMA = [
        'game_date',         # datetime: When game occurred
        'game_id',           # str: Unique game identifier
        'season',            # int: Season year
        'team_id',           # str: Team identifier (normalized)
        'opponent_id',       # str: Opponent identifier
        'team_won',          # int: 1 if team won, 0 if lost
        'points_scored',     # int: Points scored by team
        'points_allowed',    # int: Points allowed to opponent
        'is_home',           # int: 1 if home game, 0 if away
        'sport'              # str: Sport identifier (NHL, NFL, NBA, MLB)
    ]
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize data loader
        
        Args:
            data_dir: Directory containing sport data files (defaults to project root)
        """
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent
        self.logger = logger
        
        # Sport-specific loaders
        self.loaders = {
            'NHL': self._load_nhl_data,
            'NFL': self._load_nfl_data,
            'NBA': self._load_nba_data,
            'MLB': self._load_mlb_data
        }
    
    def load_sport_data(self, sport: str, filename: str = None) -> pd.DataFrame:
        """
        Load data for specified sport
        
        Args:
            sport: One of 'NHL', 'NFL', 'NBA', 'MLB'
            filename: Optional custom filename (defaults to standard names)
        
        Returns:
            DataFrame with normalized common schema
        """
        sport = sport.upper()
        
        if sport not in self.loaders:
            raise ValueError(f"Unknown sport: {sport}. Must be one of {list(self.loaders.keys())}")
        
        # Default filenames
        default_files = {
            'NHL': 'nhl_finished_games.csv',
            'NFL': 'nfl_games.csv',
            'NBA': 'nba_games.csv',
            'MLB': 'mlb_games.csv'
        }
        
        filename = filename or default_files[sport]
        filepath = self.data_dir / filename
        
        self.logger.info(f"Loading {sport} data from {filepath}")
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        # Load using sport-specific loader
        df = self.loaders[sport](filepath)
        
        # Validate common schema
        df = self._validate_common_schema(df, sport)
        
        self.logger.info(f"Loaded {len(df)} records for {sport}")
        return df
    
    def _load_nhl_data(self, filepath: Path) -> pd.DataFrame:
        """
        Load NHL data (simple 7-column format)
        
        Schema: season, game_id, date, home_team, away_team, home_score, away_score
        
        Strategy: Convert match-level data (1 row per game) to team-level (2 rows per game)
        """
        self.logger.info("Loading NHL data (simple schema)...")
        
        df = pd.read_csv(filepath)
        self.logger.info(f"Raw NHL data shape: {df.shape}, columns: {df.columns.tolist()}")
        
        # Convert match-level to team-level
        home_df = pd.DataFrame({
            'game_date': pd.to_datetime(df['date'], utc=True),
            'game_id': df['game_id'].astype(str),
            'season': df['season'],
            'team_id': df['home_team'],
            'opponent_id': df['away_team'],
            'team_won': (df['home_score'] > df['away_score']).astype(int),
            'points_scored': df['home_score'],
            'points_allowed': df['away_score'],
            'is_home': 1,
            'sport': 'NHL'
        })
        
        away_df = pd.DataFrame({
            'game_date': pd.to_datetime(df['date'], utc=True),
            'game_id': df['game_id'].astype(str),
            'season': df['season'],
            'team_id': df['away_team'],
            'opponent_id': df['home_team'],
            'team_won': (df['away_score'] > df['home_score']).astype(int),
            'points_scored': df['away_score'],
            'points_allowed': df['home_score'],
            'is_home': 0,
            'sport': 'NHL'
        })
        
        combined = pd.concat([home_df, away_df], ignore_index=True)
        combined = combined.sort_values('game_date').reset_index(drop=True)
        
        self.logger.info(f"Converted to team-level: {len(combined)} rows ({len(df)} games * 2)")
        return combined
    
    def _load_nfl_data(self, filepath: Path) -> pd.DataFrame:
        """
        Load NFL data (complex 35+ column format)
        
        Schema: league, season, game_id, date, week, venue, odds, home/away teams, scores, quarters
        
        Strategy: Extract essential columns, preserve metadata for advanced features
        """
        self.logger.info("Loading NFL data (complex schema with venue & odds)...")
        
        df = pd.read_csv(filepath)
        self.logger.info(f"Raw NFL data shape: {df.shape}")
        
        # Extract date from complex datetime dict string
        df['date_str'] = df['date'].str.extract(r"'date': '([^']+)'")[0]
        df['game_date'] = pd.to_datetime(df['date_str'], errors='coerce')
        
        # Calculate winners from scores (home_winner/away_winner columns are often empty)
        df['home_won_calc'] = (df['home_score_total'] > df['away_score_total']).astype(int)
        df['away_won_calc'] = (df['away_score_total'] > df['home_score_total']).astype(int)
        
        # Convert to team-level
        home_df = pd.DataFrame({
            'game_date': df['game_date'],
            'game_id': df['game_id'].astype(str),
            'season': df['season'],
            'team_id': df['home_team_name'],
            'opponent_id': df['away_team_name'],
            'team_won': df['home_won_calc'],
            'points_scored': df['home_score_total'].fillna(0).astype(int),
            'points_allowed': df['away_score_total'].fillna(0).astype(int),
            'is_home': 1,
            'sport': 'NFL',
            # Preserve metadata for advanced features
            'week': df['week'],
            'venue_name': df.get('venue_name', None),
            'venue_surface': df.get('venue_surface', None),
            'odds_home': pd.to_numeric(df.get('odds_home'), errors='coerce'),
            'odds_away': pd.to_numeric(df.get('odds_away'), errors='coerce'),
            'over_under': pd.to_numeric(df.get('over_under_line'), errors='coerce')
        })
        
        away_df = pd.DataFrame({
            'game_date': df['game_date'],
            'game_id': df['game_id'].astype(str),
            'season': df['season'],
            'team_id': df['away_team_name'],
            'opponent_id': df['home_team_name'],
            'team_won': df['away_won_calc'],
            'points_scored': df['away_score_total'].fillna(0).astype(int),
            'points_allowed': df['home_score_total'].fillna(0).astype(int),
            'is_home': 0,
            'sport': 'NFL',
            'week': df['week'],
            'venue_name': df.get('venue_name', None),
            'venue_surface': df.get('venue_surface', None),
            'odds_home': pd.to_numeric(df.get('odds_away'), errors='coerce'),
            'odds_away': pd.to_numeric(df.get('odds_home'), errors='coerce'),
            'over_under': pd.to_numeric(df.get('over_under_line'), errors='coerce')
        })
        
        combined = pd.concat([home_df, away_df], ignore_index=True)
        combined = combined.sort_values('game_date').reset_index(drop=True)
        
        self.logger.info(f"NFL data processed: {len(combined)} team-games")
        return combined
    
    def _load_nba_data(self, filepath: Path) -> pd.DataFrame:
        """
        Load NBA data (basketball - similar structure to NFL)
        """
        self.logger.info("Loading NBA data (complex schema with quarters)...")
        
        if not filepath.exists():
            self.logger.warning(f"NBA file not found: {filepath}, returning empty DataFrame")
            return pd.DataFrame(columns=self.COMMON_SCHEMA)
        
        df = pd.read_csv(filepath)
        self.logger.info(f"Raw NBA data shape: {df.shape}")
        
        # Parse date
        df['game_date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Calculate winners from scores
        df['home_won_calc'] = (df['home_score_total'] > df['away_score_total']).astype(int)
        df['away_won_calc'] = (df['away_score_total'] > df['home_score_total']).astype(int)
        
        # Convert to team-level (home and away teams)
        home_df = pd.DataFrame({
            'game_date': df['game_date'],
            'game_id': df['game_id'].astype(str),
            'season': df['season'],
            'team_id': df['home_team_name'],
            'opponent_id': df['away_team_name'],
            'team_won': df['home_won_calc'],
            'points_scored': df['home_score_total'].fillna(0).astype(int),
            'points_allowed': df['away_score_total'].fillna(0).astype(int),
            'is_home': 1,
            'sport': 'NBA',
            'week': df.get('week', 1),
            'venue_name': df.get('venue_name', 'Arena'),
            'venue_surface': 'Court',
            'odds_home': pd.to_numeric(df.get('odds_home'), errors='coerce'),
            'odds_away': pd.to_numeric(df.get('odds_away'), errors='coerce'),
            'over_under': pd.to_numeric(df.get('over_under_line'), errors='coerce')
        })
        
        away_df = pd.DataFrame({
            'game_date': df['game_date'],
            'game_id': df['game_id'].astype(str),
            'season': df['season'],
            'team_id': df['away_team_name'],
            'opponent_id': df['home_team_name'],
            'team_won': df['away_won_calc'],
            'points_scored': df['away_score_total'].fillna(0).astype(int),
            'points_allowed': df['home_score_total'].fillna(0).astype(int),
            'is_home': 0,
            'sport': 'NBA',
            'week': df.get('week', 1),
            'venue_name': df.get('venue_name', 'Arena'),
            'venue_surface': 'Court',
            'odds_home': pd.to_numeric(df.get('odds_away'), errors='coerce'),
            'odds_away': pd.to_numeric(df.get('odds_home'), errors='coerce'),
            'over_under': pd.to_numeric(df.get('over_under_line'), errors='coerce')
        })
        
        combined = pd.concat([home_df, away_df], ignore_index=True)
        combined = combined.sort_values('game_date').reset_index(drop=True)
        
        self.logger.info(f"NBA data processed: {len(combined)} team-games")
        return combined
    
    def _load_mlb_data(self, filepath: Path) -> pd.DataFrame:
        """
        Load MLB data (baseball-specific structure)
        """
        self.logger.info("Loading MLB data...")
        
        if not filepath.exists():
            self.logger.warning(f"MLB file not found: {filepath}, returning empty DataFrame")
            return pd.DataFrame(columns=self.COMMON_SCHEMA)
        
        df = pd.read_csv(filepath)
        self.logger.info(f"Loaded {len(df)} MLB games")
        
        # Parse date from dictionary string or direct format
        if 'date' in df.columns:
            df['game_date'] = pd.to_datetime(df['date'].str.extract(r"'date': '([^']+)'")[0], errors='coerce')
            if df['game_date'].isna().all():
                df['game_date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Calculate winners from scores
        df['home_won_calc'] = (df['home_score_total'] > df['away_score_total']).astype(int)
        df['away_won_calc'] = (df['away_score_total'] > df['home_score_total']).astype(int)
        
        # Convert to team-level
        home_df = pd.DataFrame({
            'game_date': df['game_date'],
            'game_id': df['game_id'].astype(str),
            'season': df['season'],
            'team_id': df['home_team_name'],
            'opponent_id': df['away_team_name'],
            'team_won': df['home_won_calc'],
            'points_scored': df['home_score_total'].fillna(0).astype(int),
            'points_allowed': df['away_score_total'].fillna(0).astype(int),
            'is_home': 1,
            'sport': 'MLB'
        })
        
        away_df = pd.DataFrame({
            'game_date': df['game_date'],
            'game_id': df['game_id'].astype(str),
            'season': df['season'],
            'team_id': df['away_team_name'],
            'opponent_id': df['home_team_name'],
            'team_won': df['away_won_calc'],
            'points_scored': df['away_score_total'].fillna(0).astype(int),
            'points_allowed': df['home_score_total'].fillna(0).astype(int),
            'is_home': 0,
            'sport': 'MLB'
        })
        
        combined = pd.concat([home_df, away_df], ignore_index=True)
        combined = combined.sort_values('game_date').reset_index(drop=True)
        
        self.logger.info(f"MLB data processed: {len(combined)} team-games")
        return combined
    
    def _validate_common_schema(self, df: pd.DataFrame, sport: str) -> pd.DataFrame:
        """
        Validate and clean common schema columns
        """
        # Ensure all common columns exist
        for col in self.COMMON_SCHEMA:
            if col not in df.columns:
                self.logger.warning(f"Missing column {col} for {sport}, filling with default")
                if col == 'sport':
                    df[col] = sport
                elif col in ['team_won', 'is_home']:
                    df[col] = 0
                elif col in ['points_scored', 'points_allowed', 'season']:
                    df[col] = 0
                else:
                    df[col] = None
        
        # Type conversions
        df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')
        df['team_won'] = pd.to_numeric(df['team_won'], errors='coerce').fillna(0).astype(int)
        df['is_home'] = pd.to_numeric(df['is_home'], errors='coerce').fillna(0).astype(int)
        df['points_scored'] = pd.to_numeric(df['points_scored'], errors='coerce').fillna(0).astype(int)
        df['points_allowed'] = pd.to_numeric(df['points_allowed'], errors='coerce').fillna(0).astype(int)
        
        # Remove invalid rows
        df = df.dropna(subset=['game_date', 'team_id', 'opponent_id'])
        
        # Sort by date
        df = df.sort_values('game_date').reset_index(drop=True)
        
        self.logger.info(f"Schema validation complete: {len(df)} valid records")
        return df
    
    def get_sport_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for loaded sport data
        """
        stats = {
            'total_games': len(df),
            'total_teams': df['team_id'].nunique(),
            'date_range': (df['game_date'].min(), df['game_date'].max()),
            'seasons': df['season'].nunique() if 'season' in df.columns else None,
            'home_win_rate': df[df['is_home'] == 1]['team_won'].mean() if len(df) > 0 else None,
            'avg_points_scored': df['points_scored'].mean(),
            'avg_point_differential': (df['points_scored'] - df['points_allowed']).mean()
        }
        return stats


if __name__ == "__main__":
    # Test data loading
    logging.basicConfig(level=logging.INFO)
    
    loader = MultiSportDataLoader()
    
    print("\n" + "="*80)
    print("MULTI-SPORT DATA LOADER - TESTING")
    print("="*80 + "\n")
    
    # Test each sport
    for sport in ['NHL', 'NFL']:
        print(f"\n{'='*40}")
        print(f"Testing {sport} Data Loader")
        print(f"{'='*40}")
        
        try:
            df = loader.load_sport_data(sport)
            stats = loader.get_sport_statistics(df)
            
            print(f"\n Data Shape: {df.shape}")
            print(f" Columns: {df.columns.tolist()}")
            print(f"\nStatistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            
            print(f"\nSample Data:")
            print(df.head(10))
            
        except Exception as e:
            print(f" ERROR loading {sport}: {e}")
    
    print("\n" + "="*80)
    print("Testing Complete")
    print("="*80 + "\n")
