"""
Prediction Service Layer for Sports Forecast Application
- Loads pre-trained Bayesian Ensemble (Over/Under) and Spread Regression models.
- Loads Winner Classification models.
- Calculates the projected final score (ml_prediction) used in Monte Carlo blending.
- Calculates the projected spread (margin of victory).
- 🔑 Calculates the projected winner probability (Moneyline).
- Calculates SHAP values for prediction explainability.

**FIX v2.0:** Implemented dynamic blending for `calculate_winner_prediction`
to fix illogical live-game probabilities.
**FIX v2.1 (NHL FIX):** Implemented sport-specific score impact factor for
Winner Probability blending.
**NHL v3.0 (Custom Model):** Integrated dedicated NHL pre-game and live
winner models (`nhl_pre_game_win_model.pkl` & `nhl_live_win_model.pkl`)
trained on Kaggle with play-by-play features.
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import logging
from typing import Dict, Tuple, Optional, Any, List
from datetime import datetime, date

try:
    import shap
except Exception as e:
    shap = None
    logger = logging.getLogger("prediction")
    logger.warning(f"SHAP import failed, SHAP features will be disabled. Reason: {e}")
# NOTE: Assumes simulation.py is in the same directory or properly imported
from .simulation import OverUnderSimulator
# 🔑 --- START FIX: Import TimeParser for live game-state awareness ---
from .sport_config import TimeParser, get_sport_config
# 🔑 --- END FIX ---


logger = logging.getLogger("prediction")

# --- CONFIGURATION (Paths and file names are preserved) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_ROOT / "LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP"

# Individual sport model directories (FOR OVER/UNDER CLASSIFICATION)
NFL_MODEL_DIR = MODEL_DIR / "NFL_MODELS"
NBA_MODEL_DIR = MODEL_DIR / "NBA_MODELS"
MLB_MODEL_DIR = MODEL_DIR / "MLB_MODELS"
NHL_MODEL_DIR = MODEL_DIR / "NHL_MODELS"

# Directory for SPREAD REGRESSION models
SPREAD_MODEL_DIR = MODEL_DIR / "SPREAD_MODELS"

# Directory for WINNER CLASSIFICATION models
WINNER_MODEL_DIR = PROJECT_ROOT / "Sports-Project-main" / "WINNER_MODELS" if (PROJECT_ROOT / "Sports-Project-main" / "WINNER_MODELS").exists() else (MODEL_DIR.parent / "WINNER_MODELS")

# ✅ NHL custom Kaggle models (pre-game & live)
NHL_PREGAME_MODEL_PATH = WINNER_MODEL_DIR / "nhl_pre_game_win_model.pkl"
NHL_LIVE_MODEL_PATH = WINNER_MODEL_DIR / "nhl_live_win_model.pkl"

# Enriched feature CSVs (used for static lookups)
FEATURE_DATA_DIR = MODEL_DIR / "FINAL_SUPER_ENRICHED_FIXED"
NFL_FEATURE_CSV = FEATURE_DATA_DIR / "american_football_SUPER_FINAL_FIXED.csv"
NBA_FEATURE_CSV = FEATURE_DATA_DIR / "basketball_SUPER_FINAL_FIXED.csv"
MLB_FEATURE_CSV = FEATURE_DATA_DIR / "baseball_SUPER_FINAL_FIXED.csv"
NHL_FEATURE_CSV = FEATURE_DATA_DIR / "ice_hockey_SUPER_FINAL_FIXED.csv"

# Original training data folder (used for getting feature names)
ML_TRAIN_DATA_DIR = PROJECT_ROOT / "READY_FOR_TRAINING"
NFL_X_TRAIN_CSV = ML_TRAIN_DATA_DIR / "NFL_X_train.csv"
NBA_X_TRAIN_CSV = ML_TRAIN_DATA_DIR / "NBA_X_train.csv"
MLB_X_TRAIN_CSV = ML_TRAIN_DATA_DIR / "MLB_X_train.csv"
NHL_X_TRAIN_CSV = ML_TRAIN_DATA_DIR / "NHL_X_train.csv"

logger.info(f"Model directories configured:")
logger.info(f"  O/U -> {NFL_MODEL_DIR} (and other sports)")
logger.info(f"  Spread -> {SPREAD_MODEL_DIR}")
logger.info(f"  Winner -> {WINNER_MODEL_DIR}")

logger.info(f"Feature CSVs configured:")
logger.info(f"  NFL -> {NFL_FEATURE_CSV}")
logger.info(f"  NBA -> {NBA_FEATURE_CSV}")
logger.info(f"  MLB -> {MLB_FEATURE_CSV}")
logger.info(f"  NHL -> {NHL_FEATURE_CSV}")


# --- DOMAIN-AWARE FEATURE BUILDER (Copied EXACTLY from your training script) ---
def enrich_domain_features(df):
    df = df.copy()
    # Guard for missing columns
    for c in ["venue_advantage","momentum_diff","team_efficiency_home",
             "team_efficiency_away","rest_diff","player_injuries","over_under_line",
             "home_total", "away_total"]:
        if c not in df.columns: df[c] = 0.0

    # Derived / contextual features
    df["efficiency_gap"] = df["team_efficiency_home"] - df["team_efficiency_away"]
    df["momentum_eff_combo"] = df["momentum_diff"] * df["efficiency_gap"]
    df["fatigue_penalty"] = np.exp(-np.abs(df["rest_diff"]).clip(0,3))
    df["injury_penalty"] = np.tanh(df["player_injuries"])
    df["home_adv_boost"] = np.log1p(df["venue_advantage"] + 1)
    
    # Clip the line at a minimum value to prevent log(0) errors if the line is 0.0 or less
    df["expected_points_scaled"] = np.log1p(df["over_under_line"].clip(lower=1e-6))
    
    df["synergy_factor"] = df["efficiency_gap"] * df["fatigue_penalty"] * (1 - df["injury_penalty"])

    # FIX FOR SPREAD/WINNER MODEL (These two columns are critical for comparative models)
    safe_ou_line = df['over_under_line'].clip(lower=1e-6)
    df['home_total_norm'] = df['home_total'] / safe_ou_line
    df['away_total_norm'] = df['away_total'] / safe_ou_line

    # Normalize
    df = df.replace([np.inf, -np.inf], 0).fillna(0)
    return df
# --- END DOMAIN-AWARE FEATURE BUILDER ---


# -------------------------------------------------------------------------------------
# Static Feature Loader (Reads your actual CSVs)
# (Unchanged)
# -------------------------------------------------------------------------------------
class StaticFeatureLoader:
    def __init__(self):
        self.feature_dfs: Dict[str, pd.DataFrame] = {}
        self.load_all_features()

    def _get_csv_path(self, sport: str) -> Optional[Path]:
        if sport == 'NFL': return NFL_FEATURE_CSV
        if sport == 'MLB': return MLB_FEATURE_CSV
        if sport == 'NBA': return NBA_FEATURE_CSV
        if sport == 'NHL': return NHL_FEATURE_CSV
        return None

    def load_all_features(self):
        """Loads all CSV files into memory once at initialization."""
        for sport in ['NFL', 'NBA', 'MLB', 'NHL']:
            file_path = self._get_csv_path(sport)
            if not file_path: continue
            
            if file_path.exists():
                try:
                    df = pd.read_csv(file_path)
                    if 'date' in df.columns:
                        # Use a safe date type for merging/comparison
                        df['date'] = pd.to_datetime(df['date']).dt.date 
                    self.feature_dfs[sport] = df
                    logger.info(f"Loaded {sport} static features: {len(df)} rows.")
                except Exception as e:
                    logger.error(f"Failed to load static features for {sport} from {file_path}: {e}")
            else:
                logger.warning(f"Static feature file not found at: {file_path}. ML model will use zero-defaults for static features.")
    
    def lookup_features(self, sport: str, game_date_str: str, home_team: str, away_team: str) -> Dict[str, Any]:
        """
        Performs the feature lookup based on the game's sport, date, and home/away teams.
        """
        df = self.feature_dfs.get(sport)
        if df is None or df.empty:
            return {}
        
        try:
            if not isinstance(game_date_str, str) or len(game_date_str) < 10:
                game_date_str = datetime.now().strftime('%Y-%m-%d')
            
            if 'T' in game_date_str:
                game_date_str = game_date_str.split('T')[0]
                
            target_date = datetime.strptime(game_date_str, '%Y-%m-%d').date()
            
            # Match the team combination on the closest *past* date
            team_df = df[
                (df['home_team'] == home_team) & 
                (df['away_team'] == away_team) &
                (df['date'] < target_date)
            ].copy()
            
            if not team_df.empty:
                # Get the row with the latest date before the target date
                latest_data = team_df.sort_values('date', ascending=False).iloc[0].to_dict()
                
                ml_features_from_df = {}
                for col, val in latest_data.items():
                    # Safely convert to float, ignore non-numeric columns like 'date'
                    try:
                        ml_features_from_df[col] = float(val)
                    except (ValueError, TypeError):
                        ml_features_from_df[col] = 0.0 # Default non-used features to 0.0
                return ml_features_from_df
            
        except Exception as e:
            logger.error(f"Error during feature lookup for {sport} ({home_team} vs {away_team} on {game_date_str}): {e}")
        
        return {}


# -------------------------------------------------------------------------------------
# FeatureService (Updated to match training script input and column set)
# (Unchanged)
# -------------------------------------------------------------------------------------
class FeatureService:
    """Provides the combined real-time and static feature vector for the ML model."""

    # 🔑 FIX: Added the new ratio features to the input feature list
    BASE_FEATURES = [
        'home_total', 'away_total', 'total_points', 'over_under_line', 'beat_over', 
        'home_ppg_last5', 'away_ppg_last5', 'home_momentum', 'away_momentum', 
        'rest_home', 'rest_away', 
        'month', 'is_weekend', 'home_last5_avg', 'away_last5_avg', 'home_away_diff', 
        'rest_diff', 'over_signal', 'api_odds', 'home_total_norm', 'away_total_norm'
    ]
    
    PAD_FEATURES = [
        'venue_advantage', 'player_injuries', 'team_efficiency', 'weather_factor', 
        'team_efficiency_home', 'team_efficiency_away', 'momentum_diff' 
    ]
    
    ALL_ML_INPUT_FEATURES = sorted(list(set(BASE_FEATURES + PAD_FEATURES)))
    
    _loader = StaticFeatureLoader() 

    @staticmethod
    def get_live_base_features(game_state_dict: Dict, contextual_data: Dict) -> Dict[str, Any]:
        """Gathers all base and padding features by combining live GUI inputs and static feature lookups."""
        sport = game_state_dict.get('sport', 'NFL')
        
        game_date_val = game_state_dict.get('date')
        if isinstance(game_date_val, dict):
            game_date_str = game_date_val.get('date', datetime.now().strftime('%Y-%m-%d'))
        elif isinstance(game_date_val, str):
            game_date_str = game_date_val.split('T')[0]
        else:
            game_date_str = datetime.now().strftime('%Y-%m-%d')
            
        home_team = game_state_dict.get('home_team', 'HOME')
        away_team = game_state_dict.get('away_team', 'AWAY')

        # 1. Get Static (Historical) Features
        static_features = FeatureService._loader.lookup_features(
            sport, game_date_str, home_team, away_team
        )
        
        features = {}
        for key in FeatureService.ALL_ML_INPUT_FEATURES:
            features[key] = 0.0

        # Inject static features (fallback)
        for key, val in static_features.items():
            if key in features and val is not None:
                features[key] = val

        # 2. Inject Live/Manual Overrides
        ou_line_live = game_state_dict.get('ou_line')
        features['over_under_line'] = float(ou_line_live) if ou_line_live is not None and ou_line_live != '' else features['over_under_line']
        
        juice_live = game_state_dict.get('juice')
        features['api_odds'] = float(juice_live) if juice_live is not None and juice_live != '' else features['api_odds']

        # Add current home/away total scores for domain enrichment
        features['home_total'] = float(game_state_dict.get('home_score', 0.0))
        features['away_total'] = float(game_state_dict.get('away_score', 0.0))
        features['total_points'] = features['home_total'] + features['away_total']
        
        # 3. Time/Contextual Data
        try:
            parsed_date = datetime.strptime(game_date_str, '%Y-%m-%d')
            features['month'] = float(parsed_date.month)
            features['is_weekend'] = 1.0 if parsed_date.weekday() >= 5 else 0.0
        except Exception:
            pass 

        # 4. Derived Contextual Overwrites
        if 'team_efficiency' in features:
            features['team_efficiency_home'] = features.get('team_efficiency', 0.0)
            features['team_efficiency_away'] = features.get('team_efficiency', 0.0)
        
        if 'home_momentum' in features and 'away_momentum' in features:
            features['momentum_diff'] = features.get('home_momentum', 0.0) - features.get('away_momentum', 0.0)
            
        features['weather_factor'] = contextual_data.get('weather_factor', 1.0) 
        features['player_injuries'] = contextual_data.get('player_injuries', 0.0)
        
        # 5. Final Numeric Check
        for key in features:
            if features[key] is None or features[key] == '':
                features[key] = 0.0
            try:
                features[key] = float(features[key])
            except (TypeError, ValueError):
                features[key] = 0.0

        return features


# -------------------------------------------------------------------------------------
# PredictionService (Model Layer)
# -------------------------------------------------------------------------------------

class PredictionService:
    """Service layer for calculating over/under predictions, now including real ML and SHAP."""
    
    def __init__(self, sport: str):
        self.sport = sport
        self.simulator = OverUnderSimulator(sport=sport)
        
        # 🔑 --- START FIX: Initialize TimeParser for live state ---
        try:
            self.sport_config = get_sport_config(sport)
            self.time_parser = TimeParser(self.sport_config)
        except Exception as e:
            logger.error(f"Failed to load sport_config or TimeParser for {sport}: {e}")
            # Fallback to NFL config if import fails but class exists
            self.sport_config = get_sport_config('NFL')
            self.time_parser = TimeParser(self.sport_config)
        # 🔑 --- END FIX ---
            
        # O/U Classification Models
        self.models: Dict[str, Any] = {}
        self.feature_names: Optional[list] = None 
        self.base_feature_names: Optional[list] = None
        
        # Spread Regression Models
        self.spread_models: Dict[str, Any] = {}
        self.spread_feature_names: Optional[list] = None
        
        # 🔑 Winner Classification Models
        self.winner_models: Dict[str, Any] = {}
        self.winner_feature_names: Optional[list] = None 

        # 🔥 NEW: NHL custom Kaggle models (pre-game + live)
        self.nhl_pregame_bundle: Optional[Dict[str, Any]] = None
        self.nhl_live_bundle: Optional[Dict[str, Any]] = None
        
        if sport == 'NFL': self.model_path = NFL_MODEL_DIR
        elif sport == 'NBA': self.model_path = NBA_MODEL_DIR
        elif sport == 'MLB': self.model_path = MLB_MODEL_DIR
        elif sport == 'NHL': self.model_path = NHL_MODEL_DIR
        else: self.model_path = Path(".") 
        
        if sport == 'NFL': self.feature_csv = NFL_X_TRAIN_CSV
        elif sport == 'NBA': self.feature_csv = NBA_X_TRAIN_CSV
        elif sport == 'MLB': self.feature_csv = MLB_X_TRAIN_CSV
        elif sport == 'NHL': self.feature_csv = NHL_X_TRAIN_CSV
        else: self.feature_csv = None
        
        # Perform initial loading and feature detection
        self._load_models()
        self._load_feature_names() 

        # 🔥 Load NHL custom winner models if sport is NHL
        if self.sport == "NHL":
            self._load_nhl_custom_models()

    # 🔥 NEW: Load NHL Kaggle models
    def _load_nhl_custom_models(self):
        """Loads the dedicated NHL pre-game and live winner models (Kaggle pipelines)."""
        try:
            if NHL_PREGAME_MODEL_PATH.exists():
                self.nhl_pregame_bundle = joblib.load(NHL_PREGAME_MODEL_PATH)
                logger.info(f"NHL pre-game winner model loaded from {NHL_PREGAME_MODEL_PATH}")
            else:
                logger.warning(f"NHL pre-game model not found at {NHL_PREGAME_MODEL_PATH}")

            if NHL_LIVE_MODEL_PATH.exists():
                self.nhl_live_bundle = joblib.load(NHL_LIVE_MODEL_PATH)
                logger.info(f"NHL live winner model loaded from {NHL_LIVE_MODEL_PATH}")
            else:
                logger.warning(f"NHL live model not found at {NHL_LIVE_MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error loading NHL custom models: {e}", exc_info=True)
            self.nhl_pregame_bundle = None
            self.nhl_live_bundle = None

    def _load_models(self):
        """Loads the pre-trained ML models and calibrator using joblib."""
        
        # --- 1. Load O/U Classification Models ---
        if not self.model_path.exists():
            logger.error(f"Model directory not found for {self.sport}: {self.model_path}")
            return
        try:
            self.models['calibrator'] = joblib.load(self.model_path / "calibrator.pkl")
            self.models['xgboost'] = joblib.load(self.model_path / "xgboost.pkl")
            self.models['random_forest'] = joblib.load(self.model_path / "random_forest.pkl")
            self.models['lightgbm'] = joblib.load(self.model_path / "lightgbm.pkl")
            logger.info(f"Successfully loaded 4 ensemble base models for {self.sport}.")
        except Exception as e:
            logger.error(f"Failed to load required O/U model files for {self.sport} from {self.model_path}: {e}", exc_info=True)
            self.models = {}

        # --- 2. Load Spread Regression Models ---
        if not SPREAD_MODEL_DIR.exists():
            logger.error(f"Spread Model directory not found: {SPREAD_MODEL_DIR}")
        else:
            try:
                self.spread_models['xgboost'] = joblib.load(SPREAD_MODEL_DIR / f"{self.sport}_spread_xgb.pkl")
                self.spread_models['lightgbm'] = joblib.load(SPREAD_MODEL_DIR / f"{self.sport}_spread_lgb.pkl")
                self.spread_models['random_forest'] = joblib.load(SPREAD_MODEL_DIR / f"{self.sport}_spread_rf.pkl")
                logger.info(f"Successfully loaded 3 ensemble SPREAD models for {self.sport}.")
            except Exception as e:
                logger.error(f"Failed to load required SPREAD model files for {self.sport} from {SPREAD_MODEL_DIR}: {e}", exc_info=True)
                self.spread_models = {}

        # --- 3. Load Winner Classification Models ---
        if not WINNER_MODEL_DIR.exists():
            logger.error(f"Winner Model directory not found: {WINNER_MODEL_DIR}")
        else:
            try:
                self.winner_models['random_forest_calibrated'] = joblib.load(WINNER_MODEL_DIR / f"{self.sport}_winner_calibrator.pkl")
                self.winner_models['xgboost_calibrated'] = joblib.load(WINNER_MODEL_DIR / f"{self.sport}_winner_xgb_calibrator.pkl")
                self.winner_models['lightgbm_calibrated'] = joblib.load(WINNER_MODEL_DIR / f"{self.sport}_winner_lgb_calibrator.pkl")
                logger.info(f"Successfully loaded 3 ensemble WINNER models for {self.sport}.")
            except Exception as e:
                logger.error(f"Failed to load required WINNER model files for {self.sport} from {WINNER_MODEL_DIR}: {e}", exc_info=True)
                self.winner_models = {}

    def _load_feature_names(self):
        """
        Loads the feature name lists, falling back to all enriched features if 
        model-specific names are unavailable (e.g., if the base model wasn't saved).
        """
        try:
            # 1. Load base features from training CSV
            if self.feature_csv and self.feature_csv.exists():
                X_train_base = pd.read_csv(self.feature_csv, nrows=1)
                self.base_feature_names = X_train_base.columns.tolist()
            else:
                self.base_feature_names = FeatureService.BASE_FEATURES
                
            # 2. O/U features
            lgbm_model = self.models.get('lightgbm')
            if lgbm_model and hasattr(lgbm_model, 'booster_'):
                self.feature_names = lgbm_model.booster_.feature_name()
            else:
                self.feature_names = []
            
            # 3. Spread features
            lgbm_spread_model = self.spread_models.get('lightgbm')
            if lgbm_spread_model and hasattr(lgbm_spread_model, 'booster_'):
                self.spread_feature_names = lgbm_spread_model.booster_.feature_name()
            else:
                self.spread_feature_names = []
            
            # ------------------------------------------------------------------
            # 🔑 4. WINNER features: Fallback protection is critical here
            # ------------------------------------------------------------------
            base_lgbm_model = None
            try:
                # Attempt to load the base LGBM model to get the feature names
                base_lgbm_model = joblib.load(WINNER_MODEL_DIR / f"{self.sport}_winner_lgb.pkl")
            except Exception:
                logger.warning(f"Could not load base winner model for {self.sport} to get feature names.")

            if base_lgbm_model and hasattr(base_lgbm_model, 'booster_'):
                self.winner_feature_names = base_lgbm_model.booster_.feature_name()
                logger.info(f"Loaded {len(self.winner_feature_names)} *final WINNER* features.")
            elif self.winner_models:
                logger.warning(f"Winner model features failed to load. Falling back to dummy enriched feature set for {self.sport}.")
                dummy_state = {'sport': self.sport, 'home_team': 'H', 'away_team': 'A', 'date': '2024-01-01', 'ou_line': 50.0}
                X_enriched_dummy = self._get_enriched_feature_df(dummy_state, {})
                if X_enriched_dummy is not None:
                    self.winner_feature_names = X_enriched_dummy.columns.tolist()
                else:
                    self.winner_feature_names = []
            else:
                self.winner_feature_names = []
            # ------------------------------------------------------------------
                
        except Exception as e:
            logger.error(f"Could not load feature names: {e}", exc_info=True)
            self.base_feature_names = []
            self.feature_names = []
            self.spread_feature_names = []
            self.winner_feature_names = [] 

    def _get_enriched_feature_df(self, game_state_dict: Dict, contextual_data: Dict) -> Optional[pd.DataFrame]:
        """Gathers and transforms current game data into the ML model's required DataFrame."""
        
        raw_features = FeatureService.get_live_base_features(game_state_dict, contextual_data)
        
        # Ensure all required ALL_ML_INPUT_FEATURES keys exist before creating DataFrame
        data = {col: [raw_features.get(col, 0.0)] for col in FeatureService.ALL_ML_INPUT_FEATURES}
        
        X_all_input = pd.DataFrame(data)
        X_live_enriched = enrich_domain_features(X_all_input)
        
        return X_live_enriched

    def _prepare_features(self, game_state_dict: Dict, contextual_data: Dict) -> Optional[pd.DataFrame]:
        """Prepares the feature vector for the O/U CLASSIFICATION model."""
        if not self.feature_names:
            logger.error("O/U Classification feature names not loaded. Cannot prepare feature vector.")
            return None
            
        X_live_enriched = self._get_enriched_feature_df(game_state_dict, contextual_data)
        if X_live_enriched is None:
            return None 

        try:
            # Select and order features based on the saved model's feature names
            X_live_final = X_live_enriched[self.feature_names] 
        except KeyError:
            missing_cols = set(self.feature_names) - set(X_live_enriched.columns)
            logger.error(f"FATAL O/U FEATURE ERROR for {self.sport}: Missing columns: {missing_cols}")
            return None
        
        return X_live_final

    def _prepare_spread_features(self, game_state_dict: Dict, contextual_data: Dict) -> Optional[pd.DataFrame]:
        """Prepares the feature vector for the SPREAD REGRESSION model."""
        if not self.spread_feature_names:
            logger.error("Spread Regression feature names not loaded. Cannot prepare feature vector.")
            return None
            
        X_live_enriched = self._get_enriched_feature_df(game_state_dict, contextual_data)
        if X_live_enriched is None:
            return None 

        try:
            # Select and order features based on the saved model's feature names
            X_spread_final = X_live_enriched[self.spread_feature_names]
        except KeyError:
            missing_cols = set(self.spread_feature_names) - set(X_live_enriched.columns)
            logger.error(f"FATAL SPREAD FEATURE ERROR for {self.sport}: Missing columns: {missing_cols}")
            return None
        except Exception as e:
            logger.error(f"Error during spread feature preparation: {e}", exc_info=True)
            return None
        
        return X_spread_final

    def _prepare_winner_features(self, game_state_dict: Dict, contextual_data: Dict) -> Optional[pd.DataFrame]:
        """Prepares the feature vector for the WINNER CLASSIFICATION model."""
        
        feature_list_to_use = self.winner_feature_names
        
        if not feature_list_to_use:
            logger.error("Winner Classification feature names not loaded. Cannot prepare feature vector.")
            return None
            
        X_live_enriched = self._get_enriched_feature_df(game_state_dict, contextual_data)
        if X_live_enriched is None:
            return None 

        try:
            X_winner_final = X_live_enriched[feature_list_to_use]
        except KeyError:
            missing_cols = set(feature_list_to_use) - set(X_live_enriched.columns)
            logger.error(f"FATAL WINNER FEATURE ERROR for {self.sport}: Missing columns: {missing_cols}. Winner prediction may be inaccurate.")
            for col in missing_cols:
                X_live_enriched[col] = 0.0
            X_winner_final = X_live_enriched[feature_list_to_use]
        except Exception as e:
            logger.error(f"Error during winner feature preparation: {e}", exc_info=True)
            return None
        
        return X_winner_final


    def get_ml_prediction_proba(self, X_live_final: pd.DataFrame) -> Optional[float]:
        """Gets the final over/under probability from the Calibrated Ensemble Model."""
        if 'calibrator' not in self.models:
            logger.warning("ML Prediction: Calibrator model not loaded. Returning 50/50 baseline.")
            return 0.5 
        
        try:
            pred_matrix = np.column_stack([
                model.predict_proba(X_live_final)[:, 1] 
                for name, model in self.models.items() if name in ['random_forest', 'xgboost', 'lightgbm']
            ])
            over_proba = self.models['calibrator'].predict_proba(pred_matrix)[:, 1][0]
            return float(over_proba)
        except Exception as e:
            logger.error(f"Error during live ML prediction: {e}", exc_info=True)
            return 0.5 


    def calculate_ml_prediction_score(self, game_state_dict: Dict, ml_weights: Dict = None) -> Optional[float]:
        """Calculates the ML model's projected final score based on its predicted probability."""
        
        ou_line_raw = game_state_dict.get('ou_line')
        if ou_line_raw is None or not isinstance(ou_line_raw, (int, float)) or float(ou_line_raw) <= 0.0:
            logger.warning(f"ML Score: O/U line is None, invalid, or <= 0. Cannot calculate ML score deviation.")
            return None
            
        ou_line = float(ou_line_raw)
        
        X_live_final = self._prepare_features(game_state_dict, game_state_dict.get('contextual', {}))
        if X_live_final is None or X_live_final.empty:
            return None 
            
        over_prob = self.get_ml_prediction_proba(X_live_final)
            
        score_deviation_factor = 0.4 
        score_deviation = (over_prob - 0.5) * ou_line * score_deviation_factor
        projected_score = ou_line + score_deviation

        logger.debug(f"ML Prob: {over_prob:.2f} -> Projected Score: {projected_score:.1f}")
        return projected_score
    
    def calculate_spread_prediction(self, game_state_dict: Dict) -> Optional[Dict[str, float]]:
        """Calculates the ML model's projected spread (home_margin_of_victory)."""
        
        X_spread_final = self._prepare_spread_features(game_state_dict, game_state_dict.get('contextual', {}))
        
        if X_spread_final is None or X_spread_final.empty:
            logger.error("Spread Prediction: Failed to prepare feature vector.")
            return None
            
        if not self.spread_models:
            logger.error("Spread Prediction: No spread models are loaded.")
            return None
            
        try:
            pred_xgb = self.spread_models['xgboost'].predict(X_spread_final)[0]
            pred_lgb = self.spread_models['lightgbm'].predict(X_spread_final)[0]
            pred_rf = self.spread_models['random_forest'].predict(X_spread_final)[0]
            
            avg_spread_prediction = (pred_xgb + pred_lgb + pred_rf) / 3.0
            
            result = {
                'predicted_spread': float(avg_spread_prediction),
                'xgb': float(pred_xgb),
                'lgb': float(pred_lgb),
                'rf': float(pred_rf)
            }
            
            logger.info(f"Spread Prediction successful: {result}")
            return result
        except Exception as e:
            logger.error(f"Error during live SPREAD prediction: {e}", exc_info=True)
            return None

    
    # 🔑 --- START: NEW HELPER FUNCTION ---
    def _get_ml_winner_prob(self, X_live_final: pd.DataFrame) -> float:
        """
        Runs the pre-game ML ensemble models to get the baseline winner probability.
        """
        if not self.winner_models:
            logger.error("Winner Prediction: No winner models are loaded. Returning 0.5")
            return 0.5

        try:
            prob_rf = self.winner_models['random_forest_calibrated'].predict_proba(X_live_final)[:, 1][0]
            prob_xgb = self.winner_models['xgboost_calibrated'].predict_proba(X_live_final)[:, 1][0]
            prob_lgbm = self.winner_models['lightgbm_calibrated'].predict_proba(X_live_final)[:, 1][0]
            
            home_win_proba = (prob_rf + prob_xgb + prob_lgbm) / 3.0
            return float(home_win_proba)
            
        except Exception as e:
            logger.error(f"Error during _get_ml_winner_prob: {e}", exc_info=True)
            return 0.5
    # 🔑 --- END: NEW HELPER FUNCTION ---

    # 🔥 NEW: NHL feature builder for Kaggle live/pregame models
    def _build_nhl_feature_row(
        self,
        bundle: Dict[str, Any],
        game_state_dict: Dict[str, Any],
        is_live: bool
    ) -> pd.DataFrame:
        """
        Builds a single-row feature DataFrame for the NHL Kaggle models based on bundle['feature_cols'].
        It tries to map from generic game_state_dict keys (home_score, shots_home, etc.).
        Any missing stat is filled with 0.0.
        """
        feature_cols: List[str] = bundle.get("feature_cols", [])
        row_values: List[float] = []

        # Use TimeParser to approximate snapshot_time if needed
        try:
            period = game_state_dict.get("period")
            time_remaining = game_state_dict.get("time_remaining")
            progress = self.time_parser.calculate_progress(period, time_remaining) if is_live else 0.0
        except Exception:
            progress = 0.0

        # NHL: 3 periods * 1200 seconds = 3600 seconds
        approx_snapshot_time = float(progress * 3600.0)

        for col in feature_cols:
            val = None
            key_lower = col.lower()

            # 1) Exact key in the dict
            if col in game_state_dict:
                val = game_state_dict[col]
            else:
                # 2) Smart mappings
                if key_lower == "goals_home":
                    val = game_state_dict.get("home_score", 0.0)
                elif key_lower == "goals_away":
                    val = game_state_dict.get("away_score", 0.0)
                elif key_lower == "snapshot_time":
                    val = approx_snapshot_time
                elif key_lower == "shots_home":
                    val = game_state_dict.get("shots_home", 0.0)
                elif key_lower == "shots_away":
                    val = game_state_dict.get("shots_away", 0.0)
                elif key_lower == "hits_home":
                    val = game_state_dict.get("hits_home", 0.0)
                elif key_lower == "hits_away":
                    val = game_state_dict.get("hits_away", 0.0)
                elif key_lower == "takeaways_home":
                    val = game_state_dict.get("takeaways_home", 0.0)
                elif key_lower == "takeaways_away":
                    val = game_state_dict.get("takeaways_away", 0.0)
                elif key_lower == "giveaways_home":
                    val = game_state_dict.get("giveaways_home", 0.0)
                elif key_lower == "giveaways_away":
                    val = game_state_dict.get("giveaways_away", 0.0)
                elif key_lower == "blocked_home":
                    val = game_state_dict.get("blocked_home", 0.0)
                elif key_lower == "blocked_away":
                    val = game_state_dict.get("blocked_away", 0.0)
                elif key_lower == "penalties_home":
                    val = game_state_dict.get("penalties_home", 0.0)
                elif key_lower == "penalties_away":
                    val = game_state_dict.get("penalties_away", 0.0)
                else:
                    # Generic fallback (for columns like season, team IDs etc.)
                    val = 0.0

            try:
                row_values.append(float(val))
            except (TypeError, ValueError):
                row_values.append(0.0)

        df = pd.DataFrame([row_values], columns=feature_cols)
        return df

    # 🔥 NEW: NHL-specific winner calculation using Kaggle models
    def _calculate_nhl_winner_with_custom_models(self, game_state_dict: Dict) -> Optional[Dict[str, float]]:
        """
        NHL ONLY:
        Uses dedicated Kaggle models:
          - pre-game model when game hasn't started
          - live model during the game (period/time + stats)
          - deterministic outcome if final
        """
        if self.nhl_live_bundle is None:
            logger.error("NHL custom live model not loaded. Falling back to generic logic.")
            return None

        try:
            status = str(game_state_dict.get("status", "")).upper()
            home_score = float(game_state_dict.get("home_score", 0))
            away_score = float(game_state_dict.get("away_score", 0))
            period = game_state_dict.get("period")
            time_remaining = game_state_dict.get("time_remaining")

            # Progress in [0,1]
            try:
                game_progress = self.time_parser.calculate_progress(period, time_remaining)
            except Exception:
                game_progress = 0.0
        except Exception as e:
            logger.error(f"NHL Winner: error parsing game state: {e}")
            return None

        # Final / finished
        is_final_status = status in ['FINAL', 'FT', 'FINISHED', 'F/OT', 'AOT']
        if game_progress >= 0.99 or is_final_status:
            if home_score > away_score:
                return {"home_win_prob": 1.0, "away_win_prob": 0.0}
            elif home_score < away_score:
                return {"home_win_prob": 0.0, "away_win_prob": 1.0}
            else:
                return {"home_win_prob": 0.5, "away_win_prob": 0.5}

        # Pre-game (no time elapsed)
        if game_progress < 0.01:
            if self.nhl_pregame_bundle is None:
                # If no pre-game model, just use live model with 0 stats
                bundle = self.nhl_live_bundle
            else:
                bundle = self.nhl_pregame_bundle

            X = self._build_nhl_feature_row(bundle, game_state_dict, is_live=False)
            try:
                proba = bundle["model"].predict_proba(X)[:, 1][0]
            except Exception as e:
                logger.error(f"NHL pre-game model failed, fallback 0.5: {e}")
                proba = 0.5

            proba = float(np.clip(proba, 0.02, 0.98))
            return {"home_win_prob": proba, "away_win_prob": 1.0 - proba}

        # Live game: use live model
        bundle = self.nhl_live_bundle
        X_live = self._build_nhl_feature_row(bundle, game_state_dict, is_live=True)
        try:
            proba_live = bundle["model"].predict_proba(X_live)[:, 1][0]
        except Exception as e:
            logger.error(f"NHL live model failed, fallback 0.5: {e}")
            proba_live = 0.5

        proba_live = float(np.clip(proba_live, 0.02, 0.98))
        return {"home_win_prob": proba_live, "away_win_prob": 1.0 - proba_live}

    # 🔑 --- START: REBUILT FUNCTION WITH NHL FIX + CUSTOM MODEL HOOK ---
    def calculate_winner_prediction(self, game_state_dict: Dict) -> Optional[Dict[str, float]]:
        """
        Calculates the ML model's projected winner probability (Home vs Away).
        
        FIX v2.0: Dynamic blending implemented.
        FIX v2.1 (NHL): Uses a sport-specific score impact factor for dynamic blending.
        NHL v3.0: For sport='NHL', uses dedicated Kaggle models for winner prediction.
        """

        # 🔥 If NHL custom models are available, use them directly
        if self.sport == "NHL" and self.nhl_live_bundle is not None:
            nhl_result = self._calculate_nhl_winner_with_custom_models(game_state_dict)
            if nhl_result is not None:
                return nhl_result
            # If something failed, fall back to generic logic below

        # 1. Prepare features (this vector includes live score data)
        X_live_final = self._prepare_winner_features(game_state_dict, game_state_dict.get('contextual', {}))
        
        if X_live_final is None or X_live_final.empty:
            logger.error("Winner Prediction: Failed to prepare WINNER feature vector.")
            return None
            
        # 2. Get the baseline (pre-game focused) ML probability
        ml_home_prob = self._get_ml_winner_prob(X_live_final)

        # 3. Get live game state for dynamic blending
        try:
            status = game_state_dict.get('status')
            period = game_state_dict.get('period')
            time_remaining = game_state_dict.get('time_remaining')
            home_score = float(game_state_dict.get('home_score', 0))
            away_score = float(game_state_dict.get('away_score', 0))
            sport = game_state_dict.get('sport', 'NBA')

            game_progress = self.time_parser.calculate_progress(period, time_remaining)
            
        except Exception as e:
            logger.error(f"Winner Prediction: Error parsing game state: {e}. Returning pure ML prob.")
            return {'home_win_prob': ml_home_prob, 'away_win_prob': 1.0 - ml_home_prob}

        # 4. Handle different game states
        
        # --- State 1: Pre-Game (progress is 0%) ---
        if game_progress < 0.01:
            logger.debug(f"Winner Prediction (Pre-Game): Using pure ML prob: {ml_home_prob:.3f}")
            return {'home_win_prob': ml_home_prob, 'away_win_prob': 1.0 - ml_home_prob}

        # --- State 2: Final Game (progress is 100%) ---
        is_final_status = str(status).upper() in ['FINAL', 'FT', 'FINISHED', 'F/OT', 'AOT']
        if game_progress >= 0.99 or is_final_status:
            if home_score > away_score:
                final_home_prob = 1.0
            elif home_score < away_score:
                final_home_prob = 0.0
            else:
                final_home_prob = 0.5
            
            logger.debug(f"Winner Prediction (Final): Using deterministic prob: {final_home_prob:.3f}")
            return {'home_win_prob': final_home_prob, 'away_win_prob': 1.0 - final_home_prob}

        # --- State 3: Live Game (Blending) ---
        score_diff = home_score - away_score
        
        if sport == 'NHL':
            score_impact_factor = 0.18 
        elif sport == 'MLB':
            score_impact_factor = 0.10
        else:
            score_impact_factor = 0.05 
        
        dynamic_home_prob = np.clip(0.5 + (score_diff * score_impact_factor), 0.05, 0.95)
        
        ml_weight = 1.0 - game_progress
        dynamic_weight = game_progress
        
        final_home_prob = (ml_home_prob * ml_weight) + (dynamic_home_prob * dynamic_weight)
        
        logger.info(f"Winner Prediction (Live @ {game_progress:.0%} - {sport} Factor: {score_impact_factor}): "
                    f"ML={ml_home_prob:.2f} (w={ml_weight:.2f}), "
                    f"Dynamic={dynamic_home_prob:.2f} (w={dynamic_weight:.2f}), "
                    f"Final={final_home_prob:.3f}")

        return {
            'home_win_prob': float(final_home_prob),
            'away_win_prob': 1.0 - float(final_home_prob)
        }
    # 🔑 --- END: REBUILT FUNCTION WITH NHL FIX + CUSTOM MODEL HOOK ---

    
    def get_shap_plot_data(self, game_state_dict: Dict) -> Dict[str, List[float]]:
        """Calculates SHAP values and formats them for the visualization bar chart."""
        
        lgbm_model = self.models.get('lightgbm')
        
        if lgbm_model is None or not self.feature_names:
            logger.warning("SHAP: Model or feature names not loaded. Returning mock data.")
            return {
                'Feature': ['O/U Line', 'Momentum Diff.', 'Rest Diff.'],
                'Contribution': [3.5, 1.2, -0.8],
                'Value': [game_state_dict.get('ou_line') or 45.5, 0.5, 0.0]
            }
        
        shap_contributions = self.calculate_shap_values(game_state_dict, {})
        
        if not shap_contributions:
            logger.warning("SHAP: Calculation failed. Returning mock data.")
            return {
                'Feature': ['O/U Line', 'Momentum Diff.', 'Rest Diff.'],
                'Contribution': [3.5, 1.2, -0.8],
                'Value': [game_state_dict.get('ou_line') or 45.5, 0.5, 0.0]
            }

        features = list(shap_contributions.keys())[:5]
        contributions = list(shap_contributions.values())[:5]
        
        feature_values = []
        raw_features = FeatureService.get_live_base_features(game_state_dict, game_state_dict.get('contextual', {})) 

        for feature_key_human in features:
            key_snake_case = feature_key_human.lower().replace(' ', '_').replace('.', '').replace('/', '_').replace(':', '')
            val = raw_features.get(key_snake_case)
            
            if val is None:
                if key_snake_case == 'home_total_norm' and raw_features.get('over_under_line', 0.0) > 0:
                    val = raw_features.get('home_total', 0.0) / raw_features['over_under_line']
                elif key_snake_case == 'away_total_norm' and raw_features.get('over_under_line', 0.0) > 0:
                    val = raw_features.get('away_total', 0.0) / raw_features['over_under_line']
                elif key_snake_case == 'momentum_diff':
                    val = raw_features.get('home_momentum', 0.0) - raw_features.get('away_momentum', 0.0)
                else:
                    val = 0.0

            if isinstance(val, (int, float)):
                feature_values.append(val)
            else:
                feature_values.append(0.0)
                
        return {
            'Feature': features,
            'Contribution': contributions,
            'Value': feature_values
        }

    
    def calculate_shap_values(self, game_state_dict: Dict, ml_weights: Dict = None) -> Optional[Dict[str, float]]:
        """
        Calculates SHAP values using the LightGBM model for prediction explainability.
        """
        
        lgbm_model = self.models.get('lightgbm')
        
        if lgbm_model is None or not self.feature_names:
            return None
            
        X_live = self._prepare_features(game_state_dict, game_state_dict.get('contextual', {}))
        if X_live is None or X_live.empty:
            return None

        try:
            explainer = shap.TreeExplainer(lgbm_model) 
            shap_values = explainer.shap_values(X_live)
            
            if isinstance(shap_values, list):
                shap_values_class1 = shap_values[1]
            else:
                shap_values_class1 = shap_values

            shap_dict = {}
            for feature, value in zip(self.feature_names, shap_values_class1[0]):
                shap_dict[feature] = float(value) * 0.1 
                
            high_impact_shap = {k: v for k, v in shap_dict.items() if abs(v) > 0.001} 
            sorted_shap = dict(sorted(high_impact_shap.items(), key=lambda item: abs(item[1]), reverse=True))
            
            formatted_shap = {}
            for k, v in sorted_shap.items():
                new_k = k.replace('_', ' ').title().replace('Ppg', 'PPG').replace('Diff', 'Difference').replace('Ou Line', 'O/U Line').replace('Api Odds', 'Juice/Odds').replace('Total Norm', 'Total Ratio')
                formatted_shap[new_k] = v
                
            return formatted_shap
        except Exception as e:
            logger.error(f"Error during SHAP calculation (using LightGBM): {e}", exc_info=True)
            return None


    def calculate_over_under_probability(self, current_score, over_under, status, period=None, time_remaining=None, contextual_data=None, ml_weights: Dict = None):
        """Calculates probability and runs simulation, injecting the real ML prediction."""
        
        game_state_dict = contextual_data if contextual_data is not None else {}
        
        if over_under is None:
            over_under = 0.0
        elif isinstance(over_under, (str, int)):
            try:
                over_under = float(over_under)
            except ValueError:
                over_under = 0.0
            
        ml_pred_score = self.calculate_ml_prediction_score(game_state_dict, ml_weights)
        
        result = self.simulator.calculate_probability(
            current_score=current_score,
            over_under=over_under,
            status=status,
            period=period,
            time_remaining=time_remaining,
            contextual_data=contextual_data,
            ml_prediction=ml_pred_score 
        )

        return result

    def generate_probability_distribution(self, *args, **kwargs):
        """Pass-through to simulator distribution generation."""
        return self.simulator.generate_probability_distribution(*args, **kwargs)
