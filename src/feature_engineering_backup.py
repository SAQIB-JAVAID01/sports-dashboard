"""
Advanced Feature Engineering for Sports Prediction
Implements rolling statistics, momentum, opponent-adjusted metrics, and sport-specific analytics

Usage:
    engineer = SportsFeatureEngineer(sport='NBA')
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
    
    Transforms raw game data into predictive features across categories:
    1. Rolling Statistics (temporal features capturing momentum)
    2. Momentum Indicators (recent performance weighting)
    3. Opponent-Adjusted Metrics (strength of schedule)
    4. Situational Features (context-dependent factors)
    5. Market Intelligence (betting signals)
    6. Head-to-Head History (team matchup patterns)
    7. Sport-Specific Advanced Metrics (NBA, NFL, MLB, NHL)
    """
    
    def __init__(self, sport: str = 'NBA'):
        """
        Initialize feature engineer for a specific sport
        
        Args:
            sport: 'NBA', 'NFL', 'MLB', or 'NHL'
        """
        self.sport = sport.upper()
        self.feature_list = []
        self.logger = logger
        
        if self.sport not in ['NBA', 'NFL', 'MLB', 'NHL']:
            raise ValueError(f"Unknown sport: {sport}")
    
    def transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Apply all feature engineering transformations
        
        Args:
            df: DataFrame with raw game data
            
        Returns:
            Tuple of (enhanced DataFrame, list of feature names)
        """
        self.logger.info(f"Starting feature engineering for {self.sport}...")
        
        # Ensure data is sorted by date
        df = df.sort_values('game_date').reset_index(drop=True)
        
        # Apply transformations in order
        self.logger.info("Creating rolling statistics...")
        df = self._create_rolling_statistics(df)
        
        self.logger.info("Creating momentum indicators...")
        df = self._create_momentum_indicators(df)
        
        self.logger.info("Creating opponent-adjusted metrics...")
        df = self._create_opponent_adjusted_metrics(df)
        
        self.logger.info("Creating situational features...")
        df = self._create_situational_features(df)
        
        self.logger.info("Creating market intelligence features...")
        df = self._create_market_intelligence_features(df)
        
        self.logger.info("Creating head-to-head features...")
        df = self._create_head_to_head_features(df)
        
        self.logger.info(f"Creating {self.sport}-specific advanced metrics...")
        df = self._create_sport_specific_advanced_metrics(df)
        
        # Remove rows with NaN values from rolling calculations
        df = df.dropna()
        
        self.logger.info(f"✓ Feature engineering complete: {len(self.feature_list)} features created")
        self.logger.info(f"✓ Data shape: {df.shape}")
        
        return df, self.feature_list
    
    # ========================================================================
    # ROLLING STATISTICS
    # ========================================================================
    
    def _create_rolling_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create rolling statistics that capture recent team performance
        
        Rolling windows: 5, 10, 20 games
        Metrics: win rate, points scored, points allowed, point differential
        
        Why: A team on a 10-game winning streak is fundamentally different
        than the same team on a 10-game losing streak
        """
        windows = [5, 10, 20]
        
        # Use 'team_id' if it exists, otherwise 'home_team_id'
        team_col_to_use = 'team_id' if 'team_id' in df.columns else 'home_team_id'
        
        # Win rate (most important rolling stat)
        df[f'win_rate_L5'] = (
            df.groupby(team_col_to_use)['team_won']
            .transform(lambda x: x.rolling(5, min_periods=1).mean())
        )
        df[f'win_rate_L10'] = (
            df.groupby(team_col_to_use)['team_won']
            .transform(lambda x: x.rolling(10, min_periods=1).mean())
        )
        df[f'win_rate_L20'] = (
            df.groupby(team_col_to_use)['team_won']
            .transform(lambda x: x.rolling(20, min_periods=1).mean())
        )
                
                # Points scored average
                df[f'{team_col}_pts_scored_L{window}'] = (
                    df.groupby(team_col)['points_scored']
                    .transform(lambda x: x.rolling(window, min_periods=1).mean())
                )
                
                # Points allowed average
                df[f'{team_col}_pts_allowed_L{window}'] = (
                    df.groupby(team_col)['points_allowed']
                    .transform(lambda x: x.rolling(window, min_periods=1).mean())
                )
                
                # Point differential (net scoring)
                df[f'{team_col}_pt_diff_L{window}'] = (
                    df[f'{team_col}_pts_scored_L{window}'] - 
                    df[f'{team_col}_pts_allowed_L{window}']
                )
                
                # Shooting percentage (NBA/NHL)
                if self.sport in ['NBA', 'NHL']:
                    fg_col = 'field_goal_pct' if self.sport == 'NBA' else 'shooting_pct'
                    if fg_col in df.columns:
                        df[f'{team_col}_fg_pct_L{window}'] = (
                            df.groupby(team_col)[fg_col]
                            .transform(lambda x: x.rolling(window, min_periods=1).mean())
                        )
        
        # Add features to list
        self.feature_list.extend([
            'win_rate_L5', 'win_rate_L10', 'win_rate_L20',
            'pts_scored_L5', 'pts_scored_L10', 'pts_scored_L20',
            'pts_allowed_L5', 'pts_allowed_L10', 'pts_allowed_L20',
            'pt_diff_L5', 'pt_diff_L10', 'pt_diff_L20'
        ])
        
        if self.sport in ['NBA', 'NHL']:
            self.feature_list.extend(['fg_pct_L5', 'fg_pct_L10', 'fg_pct_L20'])
        
        return df
    
    # ========================================================================
    # MOMENTUM INDICATORS
    # ========================================================================
    
    def _create_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create momentum indicators using weighted recent performance
        
        Weights recent games more heavily than older games
        Current streak (positive = winning, negative = losing)
        """
        # Weights for last 5 games: [1.0, 0.9, 0.8, 0.7, 0.6]
        weights = np.array([1.0, 0.9, 0.8, 0.7, 0.6])
        
        for team_col in ['home_team_id', 'away_team_id']:
            # Momentum (weighted recent win rate)
            df[f'{team_col}_momentum'] = (
                df.groupby(team_col)['team_won']
                .transform(lambda x: self._weighted_rolling_mean(x, weights))
            )
            
            # Current winning/losing streak
            df[f'{team_col}_current_streak'] = (
                df.groupby(team_col)['team_won']
                .transform(self._calculate_streak)
            )
            
            # Momentum direction (accelerating or decelerating)
            df[f'{team_col}_momentum_recent_vs_long'] = (
                df[f'{team_col}_win_rate_L5'] - df[f'{team_col}_win_rate_L20']
            )
        
        self.feature_list.extend([
            'momentum', 'current_streak', 'momentum_recent_vs_long'
        ])
        
        return df
    
    # ========================================================================
    # OPPONENT-ADJUSTED METRICS
    # ========================================================================
    
    def _create_opponent_adjusted_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Adjust team stats based on opponent strength
        
        Example: Scoring 120 points vs #1 defense is more impressive
        than scoring 120 vs #30 defense
        """
        # Calculate league average
        league_avg_pts_allowed = df['points_allowed'].mean()
        
        # Opponent strength (based on their defensive rating)
        df['opponent_avg_pts_allowed'] = (
            df.groupby('opponent_id')['points_allowed'].transform('mean')
        )
        
        # Strength of schedule (how tough are the opponents)
        df['strength_of_schedule'] = (
            df['opponent_avg_pts_allowed'] / league_avg_pts_allowed
        )
        
        # Adjusted offensive rating (offensive efficiency vs league average defense)
        df['adjusted_offensive_rating'] = (
            (df['points_scored'] / df['opponent_avg_pts_allowed']) * 100
        ).fillna(100)
        
        # Adjusted defensive rating (defensive efficiency vs league average offense)
        league_avg_pts_scored = df['points_scored'].mean()
        df['adjusted_defensive_rating'] = (
            (df['points_allowed'] / league_avg_pts_scored) * 100
        ).fillna(100)
        
        self.feature_list.extend([
            'strength_of_schedule',
            'adjusted_offensive_rating',
            'adjusted_defensive_rating'
        ])
        
        return df
    
    # ========================================================================
    # SITUATIONAL FEATURES
    # ========================================================================
    
    def _create_situational_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Context-dependent factors that affect game outcomes
        
        Rest, back-to-back games, season phase, home court, playoffs
        """
        # Days of rest (fatigue indicator)
        df['days_rest'] = (
            df.groupby('team_id')['game_date'].diff().dt.days.fillna(3)
        )
        df['days_rest'] = df['days_rest'].clip(lower=0, upper=7)  # Cap at 7 days
        
        # Back-to-back games (critical fatigue factor)
        df['is_back_to_back'] = (df['days_rest'] == 1).astype(int)
        
        # Back-to-back-to-back
        df['is_b2b2b'] = (df['days_rest'] < 1).astype(int)
        
        # Games into season (early/mid/late season)
        season_length = 82 if self.sport == 'NBA' else (16 if self.sport == 'NFL' else 162 if self.sport == 'MLB' else 84)
        df['games_into_season'] = df.groupby(['team_id', 'season']).cumcount() + 1
        
        # Season phase (early/mid/late)
        phase_boundaries = [0, season_length // 3, 2 * season_length // 3, season_length]
        df['season_phase'] = pd.cut(
            df['games_into_season'],
            bins=phase_boundaries,
            labels=['early', 'mid', 'late']
        )
        
        # Home court advantage
        df['is_home'] = (df['location'] == 'home').astype(int) if 'location' in df.columns else 0
        
        # Travel distance (if available)
        if 'travel_distance' in df.columns:
            df['travel_distance'] = df['travel_distance'].fillna(0)
        else:
            df['travel_distance'] = 0
        
        # Playoff implications (teams fighting for playoff spots)
        df['is_playoff_race'] = (
            (df['games_into_season'] > season_length * 0.75) &
            (df['team_rank'] >= 8) &
            (df['team_rank'] <= 10)
        ).astype(int) if 'team_rank' in df.columns else 0
        
        # Weather factors (NFL/MLB outdoor games)
        if self.sport in ['NFL', 'MLB']:
            df['is_outdoor'] = (df['venue_type'] == 'outdoor').astype(int) if 'venue_type' in df.columns else 1
            df['temperature'] = df.get('weather_temp', 70).fillna(70)  # Fahrenheit
            df['wind_speed'] = df.get('weather_wind', 0).fillna(0)
            df['precipitation'] = df.get('weather_precip', 0).fillna(0)
        
        self.feature_list.extend([
            'days_rest', 'is_back_to_back', 'is_b2b2b',
            'games_into_season', 'is_home', 'travel_distance', 'is_playoff_race'
        ])
        
        if self.sport in ['NFL', 'MLB']:
            self.feature_list.extend(['is_outdoor', 'temperature', 'wind_speed', 'precipitation'])
        
        return df
    
    # ========================================================================
    # MARKET INTELLIGENCE
    # ========================================================================
    
    def _create_market_intelligence_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Betting market signals
        
        The betting market is highly efficient - use it as a feature!
        Sharp money vs public money movements
        """
        # Opening spread vs current spread (line movement)
        if 'current_spread' in df.columns and 'opening_spread' in df.columns:
            df['line_movement'] = df['current_spread'] - df['opening_spread']
            df['line_movement_abs'] = df['line_movement'].abs()
        else:
            df['line_movement'] = 0
            df['line_movement_abs'] = 0
        
        # Implied probability from betting odds
        if 'moneyline_odds' in df.columns:
            df['implied_prob'] = df['moneyline_odds'].apply(self._odds_to_probability)
        else:
            df['implied_prob'] = 0.5
        
        # Reverse line movement (sharp money indicator)
        if 'public_bet_pct' in df.columns:
            df['reverse_line_movement'] = (
                ((df['line_movement'] > 0) & (df['public_bet_pct'] < 50)) |
                ((df['line_movement'] < 0) & (df['public_bet_pct'] > 50))
            ).astype(int)
        else:
            df['reverse_line_movement'] = 0
        
        self.feature_list.extend([
            'line_movement', 'line_movement_abs', 'implied_prob', 'reverse_line_movement'
        ])
        
        return df
    
    # ========================================================================
    # HEAD-TO-HEAD HISTORY
    # ========================================================================
    
    def _create_head_to_head_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Historical matchup data between specific teams
        
        Some teams just match up well against certain opponents
        """
        # H2H win rate (last 10 meetings)
        df['h2h_win_rate_L10'] = (
            df.groupby(['team_id', 'opponent_id'])['team_won']
            .transform(lambda x: x.rolling(10, min_periods=1).mean())
        )
        
        # H2H average point differential (last 10 meetings)
        if 'point_differential' in df.columns:
            df['h2h_avg_pt_diff_L10'] = (
                df.groupby(['team_id', 'opponent_id'])['point_differential']
                .transform(lambda x: x.rolling(10, min_periods=1).mean())
            )
        else:
            df['h2h_avg_pt_diff_L10'] = 0
        
        # Home record vs this opponent
        df['h2h_home_win_rate'] = (
            df[df['is_home'] == 1].groupby(['team_id', 'opponent_id'])['team_won']
            .transform(lambda x: x.expanding().mean())
        ).fillna(0.5)
        
        # Recent trend (last 3 meetings)
        df['h2h_recent_trend'] = (
            df.groupby(['team_id', 'opponent_id'])['team_won']
            .transform(lambda x: x.rolling(3, min_periods=1).mean())
        )
        
        self.feature_list.extend([
            'h2h_win_rate_L10', 'h2h_avg_pt_diff_L10',
            'h2h_home_win_rate', 'h2h_recent_trend'
        ])
        
        return df
    
    # ========================================================================
    # SPORT-SPECIFIC ADVANCED METRICS
    # ========================================================================
    
    def _create_sport_specific_advanced_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Route to sport-specific feature creation
        """
        if self.sport == 'NBA':
            return self._create_nba_advanced_metrics(df)
        elif self.sport == 'NFL':
            return self._create_nfl_advanced_metrics(df)
        elif self.sport == 'MLB':
            return self._create_mlb_advanced_metrics(df)
        elif self.sport == 'NHL':
            return self._create_nhl_advanced_metrics(df)
        
        return df
    
    def _create_nba_advanced_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        NBA-specific advanced metrics (Four Factors + more)
        
        Dean Oliver's Four Factors explain 80% of game outcomes:
        1. Effective Field Goal %
        2. Turnover Rate
        3. Offensive Rebound %
        4. Free Throw Rate
        """
        # Four Factors
        # 1. Effective FG% (accounts for 3-point bonus)
        if 'FGM' in df.columns and '3PM' in df.columns and 'FGA' in df.columns:
            df['eFG_pct'] = ((df['FGM'] + 0.5 * df['3PM']) / df['FGA'].clip(lower=1)).fillna(0.5)
            self.feature_list.append('eFG_pct')
        
        # 2. Turnover Rate
        if 'TOV' in df.columns and 'FGA' in df.columns and 'FTA' in df.columns:
            df['TOV_rate'] = (df['TOV'] / (df['FGA'] + 0.44 * df['FTA'] + df['TOV']).clip(lower=1)).fillna(0.1)
            self.feature_list.append('TOV_rate')
        
        # 3. Offensive Rebound %
        if 'ORB' in df.columns:
            df['ORB_pct'] = (df['ORB'] / (df['ORB'] + df.groupby('opponent_id')['DRB'].transform('mean')).clip(lower=1)).fillna(0.3)
            self.feature_list.append('ORB_pct')
        
        # 4. Free Throw Rate
        if 'FTA' in df.columns and 'FGA' in df.columns:
            df['FT_rate'] = (df['FTA'] / df['FGA'].clip(lower=1)).fillna(0.2)
            self.feature_list.append('FT_rate')
        
        # Pace Factor (possessions per game)
        if 'FGA' in df.columns and 'FTA' in df.columns and 'ORB' in df.columns and 'TOV' in df.columns:
            df['pace'] = (df['FGA'] + 0.44 * df['FTA'] - df['ORB'] + df['TOV']).fillna(100)
            self.feature_list.append('pace')
        
        # True Shooting % (overall scoring efficiency)
        if 'PTS' in df.columns and 'FGA' in df.columns and 'FTA' in df.columns:
            df['TS_pct'] = (df['PTS'] / (2 * (df['FGA'] + 0.44 * df['FTA'])).clip(lower=1)).fillna(0.5)
            self.feature_list.append('TS_pct')
        
        # Assist to Turnover Ratio
        if 'AST' in df.columns and 'TOV' in df.columns:
            df['AST_TOV_ratio'] = (df['AST'] / df['TOV'].clip(lower=1)).fillna(1.0)
            self.feature_list.append('AST_TOV_ratio')
        
        # Three-point rate
        if '3PM' in df.columns and 'FGM' in df.columns:
            df['3P_rate'] = (df['3PM'] / df['FGM'].clip(lower=1)).fillna(0.3)
            self.feature_list.append('3P_rate')
        
        return df
    
    def _create_nfl_advanced_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        NFL-specific advanced metrics
        """
        # EPA (Expected Points Added) per play
        if 'epa_per_play' in df.columns:
            df['epa_offense'] = df['epa_per_play'].fillna(0)
            df['epa_defense'] = df.groupby('opponent_id')['epa_per_play'].transform('mean').fillna(0)
            self.feature_list.extend(['epa_offense', 'epa_defense'])
        
        # Success Rate (plays gaining 50%+ of yards needed)
        if 'successful_plays' in df.columns and 'total_plays' in df.columns:
            df['success_rate'] = (df['successful_plays'] / df['total_plays'].clip(lower=1)).fillna(0.45)
            self.feature_list.append('success_rate')
        
        # Third Down Conversion %
        if 'third_down_conversions' in df.columns and 'third_down_attempts' in df.columns:
            df['third_down_pct'] = (
                df['third_down_conversions'] / df['third_down_attempts'].clip(lower=1)
            ).fillna(0.35)
            self.feature_list.append('third_down_pct')
        
        # Red Zone TD %
        if 'red_zone_tds' in df.columns and 'red_zone_attempts' in df.columns:
            df['red_zone_td_pct'] = (
                df['red_zone_tds'] / df['red_zone_attempts'].clip(lower=1)
            ).fillna(0.5)
            self.feature_list.append('red_zone_td_pct')
        
        # Turnover Differential
        if 'turnovers_gained' in df.columns and 'turnovers_lost' in df.columns:
            df['turnover_differential'] = (df['turnovers_gained'] - df['turnovers_lost']).fillna(0)
            self.feature_list.append('turnover_differential')
        
        # Sack Rate
        if 'sacks' in df.columns and 'pass_attempts' in df.columns:
            df['sack_rate'] = (df['sacks'] / df['pass_attempts'].clip(lower=1)).fillna(0.05)
            self.feature_list.append('sack_rate')
        
        return df
    
    def _create_mlb_advanced_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        MLB-specific advanced metrics
        """
        # FIP (Fielding Independent Pitching) - ERA variant
        if 'HR' in df.columns and 'BB' in df.columns and 'K' in df.columns and 'IP' in df.columns:
            df['team_FIP'] = ((13*df['HR'] + 3*df['BB'] - 2*df['K']) / df['IP'].clip(lower=0.1)) + 3.20
            self.feature_list.append('team_FIP')
        
        # BABIP (Batting Average on Balls In Play)
        if 'H' in df.columns and 'HR' in df.columns and 'AB' in df.columns and 'K' in df.columns:
            df['BABIP'] = (
                (df['H'] - df['HR']) / (df['AB'] - df['K'] - df['HR'] + df.get('SF', 0)).clip(lower=1)
            ).fillna(0.3)
            self.feature_list.append('BABIP')
        
        # Starter Quality (ERA)
        if 'starter_earned_runs' in df.columns and 'starter_innings_pitched' in df.columns:
            df['SP_ERA'] = (
                df['starter_earned_runs'] / df['starter_innings_pitched'].clip(lower=0.1) * 9
            ).fillna(4.0)
            self.feature_list.append('SP_ERA')
        
        # Bullpen Usage (recent workload)
        if 'bullpen_innings' in df.columns:
            df['bullpen_workload_L3'] = (
                df.groupby('team_id')['bullpen_innings'].transform(lambda x: x.rolling(3, min_periods=1).sum())
            ).fillna(0)
            self.feature_list.append('bullpen_workload_L3')
        
        return df
    
    def _create_nhl_advanced_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        NHL-specific advanced metrics
        """
        # Corsi (shot attempts differential)
        if 'shots_on_goal' in df.columns and 'missed_shots' in df.columns:
            df['corsi_for'] = (
                df['shots_on_goal'] + df.get('missed_shots', 0) + df.get('blocked_shots', 0)
            ).fillna(25)
            df['corsi_against'] = (
                df.groupby('opponent_id')['corsi_for'].transform('mean')
            ).fillna(25)
            df['corsi_for_pct'] = (
                df['corsi_for'] / (df['corsi_for'] + df['corsi_against']).clip(lower=1)
            ).fillna(0.5)
            self.feature_list.append('corsi_for_pct')
        
        # PDO (shooting % + save %)
        if 'shooting_pct' in df.columns and 'save_pct' in df.columns:
            df['PDO'] = (df['shooting_pct'] + df['save_pct']).fillna(1.0)
            self.feature_list.append('PDO')
        
        # Power Play %
        if 'PP_goals' in df.columns and 'PP_opportunities' in df.columns:
            df['power_play_pct'] = (
                df['PP_goals'] / df['PP_opportunities'].clip(lower=1)
            ).fillna(0.18)
            self.feature_list.append('power_play_pct')
        
        # Penalty Kill %
        if 'opponent_PP_goals' in df.columns and 'PK_opportunities' in df.columns:
            df['penalty_kill_pct'] = (
                1 - (df['opponent_PP_goals'] / df['PK_opportunities'].clip(lower=1))
            ).fillna(0.82)
            self.feature_list.append('penalty_kill_pct')
        
        return df
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    @staticmethod
    def _weighted_rolling_mean(series: pd.Series, weights: np.ndarray) -> pd.Series:
        """Calculate weighted moving average"""
        result = []
        for i in range(len(series)):
            window = series.iloc[max(0, i-len(weights)+1):i+1]
            if len(window) > 0:
                w = weights[-len(window):]
                result.append(np.average(window, weights=w))
            else:
                result.append(0.5)
        return pd.Series(result, index=series.index)
    
    @staticmethod
    def _calculate_streak(series: pd.Series) -> pd.Series:
        """
        Calculate current winning/losing streak
        Positive = winning, Negative = losing
        """
        result = []
        for i in range(len(series)):
            streak = 0
            for j in range(i, -1, -1):
                if series.iloc[j] == 1:
                    if streak >= 0:
                        streak += 1
                    else:
                        break
                else:
                    if streak <= 0:
                        streak -= 1
                    else:
                        break
            result.append(streak)
        return pd.Series(result, index=series.index)
    
    @staticmethod
    def _odds_to_probability(american_odds: float) -> float:
        """Convert American odds to implied probability"""
        if pd.isna(american_odds) or american_odds == 0:
            return 0.5
        
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return -american_odds / (-american_odds + 100)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Example: Create features for NBA games
    print("Loading sample data...")
    df = pd.read_csv('sample_games.csv')  # Your game data
    
    engineer = SportsFeatureEngineer(sport='NBA')
    df_engineered, features = engineer.transform(df)
    
    print(f"\nOriginal shape: {df.shape}")
    print(f"Engineered shape: {df_engineered.shape}")
    print(f"Number of features: {len(features)}")
    print(f"\nFeature list:\n{features}")
