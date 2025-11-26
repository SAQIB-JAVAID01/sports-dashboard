"""
Advanced Feature Engineering for Sports Prediction (FIXED VERSION)
Handles missing columns gracefully and works with team-level data

Usage:
    engineer = SportsFeatureEngineer(sport='NHL')
    df, features = engineer.transform(df)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger("feature_engineering")


class SportsFeatureEngineer:
    """
    Advanced feature engineering for sports prediction
    
    Fixed version that:
    1. Handles missing columns gracefully
    2. Works with team-level data (one row per team per game)
    3. Doesn't assume home_team_id/away_team_id structure
    4. Converts string dates to datetime
    5. Validates data types before operations
    """
    
    def __init__(self, sport: str = 'NBA'):
        """Initialize feature engineer for a specific sport"""
        self.sport = sport.upper()
        self.feature_list = []
        self.logger = logger
        
        if self.sport not in ['NBA', 'NFL', 'MLB', 'NHL']:
            raise ValueError(f"Unknown sport: {sport}")
    
    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Apply all feature engineering transformations
        
        Returns:
            Tuple of (enhanced DataFrame, list of feature names)
        """
        self.logger.info(f"Starting feature engineering for {self.sport}...")
        self.logger.info(f"Input shape: {df.shape}, columns: {df.columns.tolist()}")
        
        # Ensure data is sorted by date
        if 'game_date' in df.columns:
            df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')
            df = df.sort_values('game_date').reset_index(drop=True)
        
        # Ensure required columns exist
        required_cols = ['team_id', 'game_date', 'team_won', 'points_scored', 'points_allowed']
        for col in required_cols:
            if col not in df.columns:
                self.logger.warning(f"Missing required column: {col}")
        
        # Ensure numeric columns are numeric
        numeric_cols = ['team_won', 'points_scored', 'points_allowed']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Apply transformations in order
        try:
            self.logger.info("Creating rolling statistics...")
            df = self._create_rolling_statistics(df)
        except Exception as e:
            self.logger.warning(f"Error in rolling statistics: {e}")
        
        try:
            self.logger.info("Creating momentum indicators...")
            df = self._create_momentum_indicators(df)
        except Exception as e:
            self.logger.warning(f"Error in momentum indicators: {e}")
        
        try:
            self.logger.info("Creating opponent-adjusted metrics...")
            df = self._create_opponent_adjusted_metrics(df)
        except Exception as e:
            self.logger.warning(f"Error in opponent metrics: {e}")
        
        try:
            self.logger.info("Creating situational features...")
            df = self._create_situational_features(df)
        except Exception as e:
            self.logger.warning(f"Error in situational features: {e}")
        
        try:
            self.logger.info("Creating market intelligence features...")
            df = self._create_market_intelligence_features(df)
        except Exception as e:
            self.logger.warning(f"Error in market features: {e}")
        
        try:
            self.logger.info("Creating head-to-head features...")
            df = self._create_head_to_head_features(df)
        except Exception as e:
            self.logger.warning(f"Error in H2H features: {e}")
        
        try:
            self.logger.info(f"Creating {self.sport}-specific advanced metrics...")
            df = self._create_sport_specific_advanced_metrics(df)
        except Exception as e:
            self.logger.warning(f"Error in sport-specific metrics: {e}")
        
        # Remove rows with NaN values from rolling calculations
        initial_rows = len(df)
        df = df.dropna()
        final_rows = len(df)
        self.logger.info(f"Dropped {initial_rows - final_rows} rows with NaN values")
        
        self.logger.info(f"✓ Feature engineering complete: {len(self.feature_list)} features")
        self.logger.info(f"✓ Final shape: {df.shape}")
        
        return df, self.feature_list
    
    # ========================================================================
    # ROLLING STATISTICS
    # ========================================================================
    
    def _create_rolling_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create rolling statistics (wins, points scored/allowed)"""
        if 'team_id' not in df.columns:
            self.logger.warning("team_id column not found, skipping rolling statistics")
            return df
        
        # Ensure proper sorting by date and team
        if 'game_date' in df.columns:
            df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')
            df = df.sort_values(['team_id', 'game_date']).reset_index(drop=True)
        
        # Ensure required columns are numeric
        if 'team_won' in df.columns:
            df['team_won'] = pd.to_numeric(df['team_won'], errors='coerce')
        if 'points_scored' in df.columns:
            df['points_scored'] = pd.to_numeric(df['points_scored'], errors='coerce')
        if 'points_allowed' in df.columns:
            df['points_allowed'] = pd.to_numeric(df['points_allowed'], errors='coerce')
        
        windows = [5, 10, 20]
        
        for window in windows:
            # Win rate
            try:
                if 'team_won' in df.columns:
                    df[f'win_rate_L{window}'] = (
                        df.groupby('team_id')['team_won']
                        .transform(lambda x: x.rolling(window, min_periods=1).mean())
                    )
                    self.feature_list.append(f'win_rate_L{window}')
            except Exception as e:
                self.logger.debug(f"Error calculating win_rate_L{window}: {e}")
            
            # Points scored average
            try:
                if 'points_scored' in df.columns:
                    df[f'pts_scored_L{window}'] = (
                        df.groupby('team_id')['points_scored']
                        .transform(lambda x: x.rolling(window, min_periods=1).mean())
                    )
                    self.feature_list.append(f'pts_scored_L{window}')
            except Exception as e:
                self.logger.debug(f"Error calculating pts_scored_L{window}: {e}")
            
            # Points allowed average
            try:
                if 'points_allowed' in df.columns:
                    df[f'pts_allowed_L{window}'] = (
                        df.groupby('team_id')['points_allowed']
                        .transform(lambda x: x.rolling(window, min_periods=1).mean())
                    )
                    self.feature_list.append(f'pts_allowed_L{window}')
            except Exception as e:
                self.logger.debug(f"Error calculating pts_allowed_L{window}: {e}")
            
            # Point differential
            try:
                if f'pts_scored_L{window}' in df.columns and f'pts_allowed_L{window}' in df.columns:
                    df[f'pt_diff_L{window}'] = (
                        df[f'pts_scored_L{window}'] - df[f'pts_allowed_L{window}']
                    )
                    self.feature_list.append(f'pt_diff_L{window}')
            except Exception as e:
                self.logger.debug(f"Error calculating pt_diff_L{window}: {e}")
        
        return df
    
    # ========================================================================
    # MOMENTUM INDICATORS
    # ========================================================================
    
    def _create_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create momentum indicators"""
        if 'team_id' not in df.columns or 'team_won' not in df.columns:
            return df
        
        try:
            # Momentum (L5 weighted)
            df['momentum'] = (
                df.groupby('team_id')['team_won']
                .transform(lambda x: x.rolling(5, min_periods=1).mean())
            )
            self.feature_list.append('momentum')
        except:
            pass
        
        try:
            # Current streak
            df['current_streak'] = (
                df.groupby('team_id')['team_won']
                .transform(lambda x: self._calculate_streak(x))
            )
            self.feature_list.append('current_streak')
        except:
            pass
        
        return df
    
    def _calculate_streak(self, x):
        """Calculate current winning/losing streak"""
        if len(x) == 0:
            return 0
        
        streak = 0
        last_win = x.iloc[-1] if len(x) > 0 else 0
        
        for i in range(len(x) - 1, -1, -1):
            if x.iloc[i] == last_win:
                streak += 1 if last_win == 1 else -1
            else:
                break
        
        return streak
    
    # ========================================================================
    # OPPONENT-ADJUSTED METRICS
    # ========================================================================
    
    def _create_opponent_adjusted_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adjust team stats based on opponent strength"""
        if 'opponent_id' not in df.columns or 'points_allowed' not in df.columns:
            return df
        
        try:
            league_avg_pts_allowed = df['points_allowed'].mean()
            
            df['opponent_avg_pts_allowed'] = (
                df.groupby('opponent_id')['points_allowed'].transform('mean')
            )
            
            df['strength_of_schedule'] = (
                df['opponent_avg_pts_allowed'] / league_avg_pts_allowed
            )
            self.feature_list.append('strength_of_schedule')
        except:
            pass
        
        return df
    
    # ========================================================================
    # SITUATIONAL FEATURES
    # ========================================================================
    
    def _create_situational_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create situational features (rest, back-to-back, season phase)"""
        if 'team_id' not in df.columns or 'game_date' not in df.columns:
            return df
        
        try:
            # Ensure game_date is datetime
            df['game_date'] = pd.to_datetime(df['game_date'], errors='coerce')
            
            # Calculate days of rest per team
            # First, ensure the dataframe is sorted by team and date
            df_sorted = df.sort_values(['team_id', 'game_date']).copy()
            
            # Calculate time difference for each team
            df_sorted['days_rest'] = (
                df_sorted.groupby('team_id')['game_date']
                .diff()
                .dt.days
                .fillna(3)  # First game of season has 3 days rest
            )
            
            # Clip to reasonable range (1-7 days)
            df_sorted['days_rest'] = df_sorted['days_rest'].clip(lower=1, upper=7)
            
            # Merge back into original dataframe
            df = df.merge(
                df_sorted[['game_date', 'team_id', 'days_rest']].drop_duplicates(['team_id', 'game_date']),
                on=['game_date', 'team_id'],
                how='left'
            )
            
            self.feature_list.append('days_rest')
        except Exception as e:
            self.logger.debug(f"Error calculating days_rest: {e}")
            # Create a default column with 3 days rest
            if 'days_rest' not in df.columns:
                df['days_rest'] = 3
        
        try:
            # Back-to-back (days_rest == 1)
            if 'days_rest' in df.columns:
                df['is_back_to_back'] = (df['days_rest'] == 1).astype(int)
                self.feature_list.append('is_back_to_back')
        except:
            pass
        
        try:
            # Games into season
            if 'season' in df.columns and 'team_id' in df.columns:
                df['games_into_season'] = df.groupby(['team_id', 'season']).cumcount() + 1
                self.feature_list.append('games_into_season')
        except:
            pass
        
        return df
    
    # ========================================================================
    # MARKET INTELLIGENCE
    # ========================================================================
    
    def _create_market_intelligence_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create betting market features"""
        # Just pass through - these require external data
        return df
    
    # ========================================================================
    # HEAD-TO-HEAD HISTORY
    # ========================================================================
    
    def _create_head_to_head_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create head-to-head matchup features"""
        if 'team_id' not in df.columns or 'opponent_id' not in df.columns:
            return df
        
        try:
            # H2H win rate
            df['h2h_win_rate_L10'] = (
                df.groupby(['team_id', 'opponent_id'])['team_won']
                .transform(lambda x: x.rolling(10, min_periods=1).mean())
            )
            self.feature_list.append('h2h_win_rate_L10')
        except:
            pass
        
        return df
    
    # ========================================================================
    # SPORT-SPECIFIC ADVANCED METRICS
    # ========================================================================
    
    def _create_sport_specific_advanced_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Route to sport-specific feature creation"""
        if self.sport == 'NHL':
            return self._create_nhl_advanced_metrics(df)
        # Add other sports as needed
        return df
    
    def _create_nhl_advanced_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """NHL-specific metrics"""
        # For now, just create some basic hockey metrics
        try:
            df['goals_per_game'] = df['points_scored']
            self.feature_list.append('goals_per_game')
        except:
            pass
        
        return df
