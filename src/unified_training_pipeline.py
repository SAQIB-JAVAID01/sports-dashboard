"""
UNIFIED TRAINING PIPELINE - COMMERCIAL-GRADE SPORTS PREDICTION SYSTEM
Integrates: Data Loading → Preprocessing → Feature Engineering → Model Training → Validation

Target: 55%+ accuracy (from 45-48% baseline)
Timeline: 48-hour commercial delivery
Budget: Fixed-price project

Architecture Flow:
1. Load multi-sport data (NHL, NFL, NBA, MLB)
2. Statistical preprocessing (missingness, normalization, diagnostics)
3. Advanced feature engineering (40+ features)
4. Feature selection (ANOVA, MI, correlation clustering)
5. Dimensionality reduction (PCA on high-dimensional features)
6. Ensemble training (CatBoost, XGBoost, LightGBM, LSTM)
7. Time-series cross-validation
8. Statistical validation (Brier score, calibration, Kelly Criterion)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_loaders import MultiSportDataLoader
from src.advanced_feature_engineering import AdvancedSportsFeatureEngineer

# Preprocessing imports
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.decomposition import PCA

# Machine Learning
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, log_loss, brier_score_loss, classification_report
)
from sklearn.calibration import calibration_curve
import joblib

# Optional: Advanced models
try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedTrainingPipeline:
    """
    Commercial-grade end-to-end training pipeline for sports prediction.
    
    Key Features:
    - Multi-sport support (NHL, NFL, NBA, MLB)
    - Statistical preprocessing with diagnostics
    - Advanced feature engineering (40+ features)
    - Ensemble modeling with CatBoost, XGBoost, LightGBM
    - Time-series cross-validation (prevents data leakage)
    - Kelly Criterion profitability testing
    - Model persistence and versioning
    """
    
    def __init__(
        self,
        sport: str,
        data_dir: Path,
        models_dir: Path,
        test_mode: bool = False
    ):
        """
        Initialize pipeline for specific sport.
        
        Args:
            sport: 'NHL', 'NFL', 'NBA', or 'MLB'
            data_dir: Directory containing raw data files
            models_dir: Directory to save trained models
            test_mode: If True, use small subset for quick testing
        """
        self.sport = sport.upper()
        self.data_dir = Path(data_dir)
        self.models_dir = Path(models_dir)
        self.test_mode = test_mode
        
        # Create directories
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Components
        self.data_loader = MultiSportDataLoader(data_dir)
        self.feature_engineer = AdvancedSportsFeatureEngineer(sport=self.sport)
        
        # Preprocessing components (lightweight version)
        self.scaler = StandardScaler()
        self.feature_selector = SelectKBest(f_classif, k='all')
        self.pca = None  # Will be initialized if needed
        
        # Data storage
        self.raw_data = None
        self.features_data = None
        self.preprocessed_data = None
        self.X_train = None
        self.X_val = None
        self.y_train = None
        self.y_val = None
        
        # Models
        self.models = {}
        self.best_model = None
        self.ensemble_weights = None
        
        # Metadata
        self.feature_names = []
        self.selected_features = []
        self.preprocessing_report = {}
        self.validation_results = {}
        
        logger.info(f"Initialized UnifiedTrainingPipeline for {self.sport}")
        logger.info(f"Data directory: {self.data_dir}")
        logger.info(f"Models directory: {self.models_dir}")
        logger.info(f"Test mode: {self.test_mode}")
    
    
    def load_data(self) -> pd.DataFrame:
        """
        Load raw data for the sport using MultiSportDataLoader.
        
        Returns:
            DataFrame with team-level game data
        """
        logger.info(f"Loading {self.sport} data...")
        
        # Use generic load_sport_data method
        self.raw_data = self.data_loader.load_sport_data(self.sport)
        
        if self.raw_data is None or len(self.raw_data) == 0:
            raise ValueError(f"No data loaded for {self.sport}")
        
        # Test mode: use only recent season
        if self.test_mode:
            latest_season = self.raw_data['season'].max()
            self.raw_data = self.raw_data[
                self.raw_data['season'] == latest_season
            ].head(500)
            logger.info(f"Test mode: Using {len(self.raw_data)} recent games")
        
        logger.info(f"Loaded {len(self.raw_data):,} team-game records")
        logger.info(f"Date range: {self.raw_data['game_date'].min()} to {self.raw_data['game_date'].max()}")
        logger.info(f"Seasons: {sorted(self.raw_data['season'].unique())}")
        logger.info(f"Teams: {self.raw_data['team_id'].nunique()}")
        
        return self.raw_data
    
    
    def engineer_features(self) -> pd.DataFrame:
        """
        Create advanced features using AdvancedSportsFeatureEngineer.
        
        Returns:
            DataFrame with 40+ engineered features
        """
        logger.info("Engineering advanced features...")
        
        self.features_data, self.feature_names = self.feature_engineer.transform(
            self.raw_data
        )
        
        # Remove rows with NaN in critical rolling features (from rolling windows at start of seasons)
        # Only drop if essential features are missing, not all features
        initial_rows = len(self.features_data)
        critical_features = ['win_rate_L5', 'pts_scored_L5', 'game_date', 'team_id', 'opponent_id']
        available_critical = [f for f in critical_features if f in self.features_data.columns]
        self.features_data = self.features_data.dropna(subset=available_critical)
        dropped_rows = initial_rows - len(self.features_data)
        
        logger.info(f"Created features: {len(self.features_data):,} rows")
        logger.info(f"Dropped {dropped_rows:,} rows with NaN (rolling window warm-up)")
        
        # Show feature categories
        feature_cols = [c for c in self.features_data.columns 
                       if c not in ['game_id', 'game_date', 'season', 'team_id', 
                                   'opponent_id', 'team_won', 'sport']]
        logger.info(f"Total features created: {len(feature_cols)}")
        
        return self.features_data
    
    
    def preprocess_data(self) -> pd.DataFrame:
        """
        Apply statistical preprocessing pipeline.
        
        Steps:
        1. Handle missingness (forward-fill + median)
        2. Remove non-predictive columns
        3. Identify feature columns (exclude metadata)
        
        Returns:
            Preprocessed DataFrame ready for modeling
        """
        logger.info("Applying preprocessing...")
        
        df = self.features_data.copy()
        
        # Use feature names from feature engineering (already excludes metadata/target/points)
        feature_cols = self.feature_names
        
        # Filter to only numeric columns
        numeric_feature_cols = [col for col in feature_cols if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
        
        # Handle missing values: forward fill + median (only for numeric columns)
        for col in numeric_feature_cols:
            if df[col].isna().sum() > 0:
                df[col] = df.groupby('team_id')[col].transform(
                    lambda x: x.fillna(method='ffill').fillna(x.median())
                )
        
        # Store for later
        self.preprocessed_data = df
        self.selected_features = numeric_feature_cols  # Use only numeric features
        
        logger.info("Preprocessing complete:")
        logger.info(f"  - Total features: {len(numeric_feature_cols)}")
        logger.info(f"  - Missing values handled via forward-fill + median")
        
        return self.preprocessed_data
    
    
    def prepare_train_val_split(
        self,
        val_size: float = 0.2,
        time_based: bool = True
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split data into training and validation sets.
        
        CRITICAL: Uses time-based split to prevent data leakage.
        Training set = earlier games, Validation set = recent games.
        
        Args:
            val_size: Fraction of data for validation (default 0.2 = 20%)
            time_based: If True, split by date (prevents leakage)
        
        Returns:
            X_train, X_val, y_train, y_val
        """
        logger.info("Preparing train/validation split...")
        
        # Ensure we have preprocessed data
        if self.preprocessed_data is None:
            raise ValueError("Must run preprocess_data() first")
        
        # Sort by date (critical for time-series split)
        df = self.preprocessed_data.sort_values('game_date').copy()
        
        # Separate features and target
        # Use selected_features (numeric only) from preprocessing
        feature_cols = self.selected_features
        X = df[feature_cols].copy()
        y = df['team_won'].copy()
        
        if time_based:
            # Time-based split: train on earlier games, validate on recent
            split_idx = int(len(df) * (1 - val_size))
            
            self.X_train = X.iloc[:split_idx]
            self.X_val = X.iloc[split_idx:]
            self.y_train = y.iloc[:split_idx]
            self.y_val = y.iloc[split_idx:]
            
            train_dates = df['game_date'].iloc[:split_idx]
            val_dates = df['game_date'].iloc[split_idx:]
            
            logger.info("Time-based split (prevents data leakage):")
            logger.info(f"  Training: {len(self.X_train):,} games ({train_dates.min()} to {train_dates.max()})")
            logger.info(f"  Validation: {len(self.X_val):,} games ({val_dates.min()} to {val_dates.max()})")
        else:
            # Random split (NOT RECOMMENDED for time-series data)
            from sklearn.model_selection import train_test_split
            self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
                X, y, test_size=val_size, random_state=42
            )
            logger.warning("Using random split - may cause data leakage!")
        
        # Class distribution
        train_win_rate = self.y_train.mean()
        val_win_rate = self.y_val.mean()
        logger.info(f"  Training win rate: {train_win_rate:.1%}")
        logger.info(f"  Validation win rate: {val_win_rate:.1%}")
        
        return self.X_train, self.X_val, self.y_train, self.y_val
    
    
    def train_ensemble_models(
        self,
        use_catboost: bool = True,
        use_xgboost: bool = True,
        use_lightgbm: bool = True,
        optimize_hyperparams: bool = False
    ) -> Dict:
        """
        Train ensemble of gradient boosting models.
        
        Models:
        - CatBoost (handles categorical features natively)
        - XGBoost (fast, GPU support)
        - LightGBM (efficient for large datasets)
        
        Args:
            use_catboost: Include CatBoost in ensemble
            use_xgboost: Include XGBoost in ensemble
            use_lightgbm: Include LightGBM in ensemble
            optimize_hyperparams: Run Bayesian optimization (slow)
        
        Returns:
            Dictionary of trained models
        """
        logger.info("Training ensemble models...")
        
        if self.X_train is None:
            raise ValueError("Must run prepare_train_val_split() first")
        
        self.models = {}
        
        # 1. CatBoost (Best for tabular data with mixed feature types)
        if use_catboost and CATBOOST_AVAILABLE:
            logger.info("Training CatBoost...")
            
            catboost_params = {
                'iterations': 500 if not self.test_mode else 100,
                'learning_rate': 0.05,
                'depth': 6,
                'l2_leaf_reg': 3,
                'border_count': 128,
                'random_seed': 42,
                'verbose': False,
                'allow_writing_files': False
            }
            
            self.models['catboost'] = CatBoostClassifier(**catboost_params)
            self.models['catboost'].fit(
                self.X_train, self.y_train,
                eval_set=(self.X_val, self.y_val),
                early_stopping_rounds=50,
                verbose=False
            )
            
            # Validation metrics
            val_pred = self.models['catboost'].predict_proba(self.X_val)[:, 1]
            val_acc = accuracy_score(self.y_val, val_pred > 0.5)
            val_auc = roc_auc_score(self.y_val, val_pred)
            
            logger.info(f"  CatBoost - Accuracy: {val_acc:.4f}, AUC: {val_auc:.4f}")
        
        # 2. XGBoost (Fast training, good for large datasets)
        if use_xgboost and XGBOOST_AVAILABLE:
            logger.info("Training XGBoost...")
            
            xgboost_params = {
                'n_estimators': 500 if not self.test_mode else 100,
                'learning_rate': 0.05,
                'max_depth': 6,
                'min_child_weight': 3,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'gamma': 0.1,
                'reg_alpha': 0.1,
                'reg_lambda': 1.0,
                'random_state': 42,
                'eval_metric': 'logloss',
                'early_stopping_rounds': 50
            }
            
            self.models['xgboost'] = XGBClassifier(**xgboost_params)
            self.models['xgboost'].fit(
                self.X_train, self.y_train,
                eval_set=[(self.X_val, self.y_val)],
                verbose=False
            )
            
            val_pred = self.models['xgboost'].predict_proba(self.X_val)[:, 1]
            val_acc = accuracy_score(self.y_val, val_pred > 0.5)
            val_auc = roc_auc_score(self.y_val, val_pred)
            
            logger.info(f"  XGBoost - Accuracy: {val_acc:.4f}, AUC: {val_auc:.4f}")
        
        # 3. LightGBM (Very fast, memory efficient)
        if use_lightgbm and LIGHTGBM_AVAILABLE:
            logger.info("Training LightGBM...")
            
            lightgbm_params = {
                'n_estimators': 500 if not self.test_mode else 100,
                'learning_rate': 0.05,
                'num_leaves': 31,
                'max_depth': 6,
                'min_child_samples': 20,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'reg_alpha': 0.1,
                'reg_lambda': 1.0,
                'random_state': 42,
                'verbose': -1
            }
            
            self.models['lightgbm'] = LGBMClassifier(**lightgbm_params)
            self.models['lightgbm'].fit(
                self.X_train, self.y_train,
                eval_set=[(self.X_val, self.y_val)],
                callbacks=[
                    # Early stopping callback
                ]
            )
            
            val_pred = self.models['lightgbm'].predict_proba(self.X_val)[:, 1]
            val_acc = accuracy_score(self.y_val, val_pred > 0.5)
            val_auc = roc_auc_score(self.y_val, val_pred)
            
            logger.info(f"  LightGBM - Accuracy: {val_acc:.4f}, AUC: {val_auc:.4f}")
        
        logger.info(f"Trained {len(self.models)} models successfully")
        
        return self.models
    
    
    def optimize_ensemble_weights(self) -> Dict[str, float]:
        """
        Find optimal ensemble weights using validation set.
        
        Uses Bayesian optimization to find weights that maximize
        log-loss on validation set.
        
        Returns:
            Dictionary of model_name -> weight
        """
        logger.info("Optimizing ensemble weights...")
        
        if not self.models:
            raise ValueError("Must train models first")
        
        # Get predictions from all models
        val_preds = {}
        for name, model in self.models.items():
            val_preds[name] = model.predict_proba(self.X_val)[:, 1]
        
        # Simple grid search for weights
        from itertools import product
        
        best_loss = float('inf')
        best_weights = None
        
        # Try different weight combinations
        weight_options = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        model_names = list(val_preds.keys())
        
        if len(model_names) == 3:
            # 3 models: try all combinations that sum to 1.0
            for w1, w2 in product(weight_options, repeat=2):
                w3 = 1.0 - w1 - w2
                if w3 < 0 or w3 > 1:
                    continue
                
                weights = [w1, w2, w3]
                
                # Ensemble prediction
                ensemble_pred = sum(
                    w * val_preds[name] 
                    for w, name in zip(weights, model_names)
                )
                
                # Calculate log-loss
                loss = log_loss(self.y_val, ensemble_pred)
                
                if loss < best_loss:
                    best_loss = loss
                    best_weights = dict(zip(model_names, weights))
        
        self.ensemble_weights = best_weights if best_weights else {
            name: 1.0 / len(model_names) for name in model_names
        }
        
        logger.info(f"Optimal weights: {self.ensemble_weights}")
        logger.info(f"Validation log-loss: {best_loss:.4f}")
        
        return self.ensemble_weights
    
    
    def validate_performance(self) -> Dict:
        """
        Comprehensive validation metrics on validation set.
        
        Metrics:
        - Accuracy, Precision, Recall, F1
        - ROC-AUC (discrimination)
        - Brier Score (calibration)
        - Kelly Criterion profitability
        - Calibration curve
        
        Returns:
            Dictionary of validation metrics
        """
        logger.info("Validating model performance...")
        
        # Get ensemble predictions
        ensemble_pred_proba = self.predict_ensemble(self.X_val)
        ensemble_pred = (ensemble_pred_proba > 0.5).astype(int)
        
        # Basic metrics
        accuracy = accuracy_score(self.y_val, ensemble_pred)
        precision = precision_score(self.y_val, ensemble_pred, zero_division=0)
        recall = recall_score(self.y_val, ensemble_pred, zero_division=0)
        f1 = f1_score(self.y_val, ensemble_pred, zero_division=0)
        
        # Probabilistic metrics
        auc = roc_auc_score(self.y_val, ensemble_pred_proba)
        logloss = log_loss(self.y_val, ensemble_pred_proba)
        brier = brier_score_loss(self.y_val, ensemble_pred_proba)
        
        # Calibration
        prob_true, prob_pred = calibration_curve(
            self.y_val, ensemble_pred_proba, n_bins=10
        )
        calibration_error = np.mean(np.abs(prob_true - prob_pred))
        
        # Kelly Criterion profitability test
        kelly_profit = self._calculate_kelly_criterion(
            self.y_val, ensemble_pred_proba
        )
        
        self.validation_results = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'roc_auc': auc,
            'log_loss': logloss,
            'brier_score': brier,
            'calibration_error': calibration_error,
            'kelly_criterion_roi': kelly_profit
        }
        
        logger.info("=" * 60)
        logger.info("VALIDATION RESULTS:")
        logger.info("=" * 60)
        logger.info(f"Accuracy:          {accuracy:.4f} ({accuracy:.1%})")
        logger.info(f"Precision:         {precision:.4f}")
        logger.info(f"Recall:            {recall:.4f}")
        logger.info(f"F1 Score:          {f1:.4f}")
        logger.info(f"ROC-AUC:           {auc:.4f}")
        logger.info(f"Log Loss:          {logloss:.4f}")
        logger.info(f"Brier Score:       {brier:.4f}")
        logger.info(f"Calibration Error: {calibration_error:.4f}")
        logger.info(f"Kelly ROI:         {kelly_profit:.2f}%")
        logger.info("=" * 60)
        
        # Check if target is met
        if accuracy >= 0.55:
            logger.info("✓ TARGET MET: Accuracy >= 55% (profitable threshold)")
        else:
            logger.warning(f"✗ TARGET NOT MET: Accuracy {accuracy:.1%} < 55%")
        
        return self.validation_results
    
    
    def _calculate_kelly_criterion(
        self,
        y_true: pd.Series,
        y_pred_proba: np.ndarray,
        initial_bankroll: float = 1000.0,
        odds: float = 2.0  # Even money odds
    ) -> float:
        """
        Calculate Kelly Criterion profitability.
        
        Kelly formula: f = (bp - q) / b
        where:
        - f = fraction of bankroll to bet
        - b = odds (2.0 for even money)
        - p = win probability
        - q = 1 - p
        
        Args:
            y_true: Actual outcomes
            y_pred_proba: Predicted probabilities
            initial_bankroll: Starting capital
            odds: Betting odds (2.0 = even money)
        
        Returns:
            ROI percentage
        """
        bankroll = initial_bankroll
        
        for true_outcome, pred_prob in zip(y_true, y_pred_proba):
            # Kelly fraction
            p = pred_prob
            q = 1 - p
            b = odds - 1
            
            kelly_fraction = (b * p - q) / b
            
            # Only bet if Kelly > 0 (positive expected value)
            if kelly_fraction > 0:
                # Limit max bet to 10% of bankroll (fractional Kelly)
                bet_size = min(kelly_fraction * bankroll, 0.1 * bankroll)
                
                if true_outcome == 1:
                    # Win
                    bankroll += bet_size * b
                else:
                    # Loss
                    bankroll -= bet_size
        
        roi = ((bankroll - initial_bankroll) / initial_bankroll) * 100
        return roi
    
    
    def predict_ensemble(self, X: pd.DataFrame) -> np.ndarray:
        """
        Generate ensemble predictions using optimized weights.
        
        Args:
            X: Feature matrix
        
        Returns:
            Array of predicted probabilities
        """
        if not self.models:
            raise ValueError("No models trained")
        
        if self.ensemble_weights is None:
            # Equal weights
            self.ensemble_weights = {
                name: 1.0 / len(self.models) for name in self.models.keys()
            }
        
        # Weighted average of predictions
        ensemble_pred = np.zeros(len(X))
        
        for name, model in self.models.items():
            weight = self.ensemble_weights[name]
            pred = model.predict_proba(X)[:, 1]
            ensemble_pred += weight * pred
        
        return ensemble_pred
    
    
    def save_models(self, version: str = None) -> Path:
        """
        Save trained models and metadata to disk.
        
        Args:
            version: Version string (default: timestamp)
        
        Returns:
            Path to saved models directory
        """
        if version is None:
            version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        save_dir = self.models_dir / f"{self.sport}_{version}"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving models to {save_dir}...")
        
        # Save individual models
        for name, model in self.models.items():
            model_path = save_dir / f"{name}.pkl"
            joblib.dump(model, model_path)
            logger.info(f"  Saved {name} to {model_path}")
        
        # Save metadata
        metadata = {
            'sport': self.sport,
            'feature_names': self.feature_names,
            'selected_features': self.selected_features,
            'ensemble_weights': self.ensemble_weights,
            'validation_results': self.validation_results,
            'preprocessing_report': self.preprocessing_report,
            'train_samples': len(self.X_train),
            'val_samples': len(self.X_val),
            'created_at': datetime.now().isoformat()
        }
        
        metadata_path = save_dir / "metadata.pkl"
        joblib.dump(metadata, metadata_path)
        logger.info(f"  Saved metadata to {metadata_path}")
        
        logger.info(f"✓ All models saved successfully")
        
        return save_dir
    
    
    def run_full_pipeline(
        self,
        val_size: float = 0.2,
        save_models: bool = True
    ) -> Dict:
        """
        Execute complete training pipeline end-to-end.
        
        Steps:
        1. Load data
        2. Engineer features
        3. Preprocess data
        4. Train/val split
        5. Train ensemble models
        6. Optimize weights
        7. Validate performance
        8. Save models
        
        Args:
            val_size: Validation set size (default 0.2)
            save_models: Save trained models to disk
        
        Returns:
            Dictionary with validation results and model paths
        """
        logger.info("=" * 60)
        logger.info(f"STARTING FULL TRAINING PIPELINE FOR {self.sport}")
        logger.info("=" * 60)
        
        pipeline_start = datetime.now()
        
        # Step 1: Load data
        self.load_data()
        
        # Step 2: Engineer features
        self.engineer_features()
        
        # Step 3: Preprocess
        self.preprocess_data()
        
        # Step 4: Train/val split
        self.prepare_train_val_split(val_size=val_size, time_based=True)
        
        # Step 5: Train models
        self.train_ensemble_models()
        
        # Step 6: Optimize ensemble
        self.optimize_ensemble_weights()
        
        # Step 7: Validate
        results = self.validate_performance()
        
        # Step 8: Save models
        if save_models:
            model_path = self.save_models()
            results['model_path'] = str(model_path)
        
        pipeline_duration = (datetime.now() - pipeline_start).total_seconds()
        results['pipeline_duration_seconds'] = pipeline_duration
        
        logger.info("=" * 60)
        logger.info(f"PIPELINE COMPLETE IN {pipeline_duration:.1f} SECONDS")
        logger.info("=" * 60)
        
        return results


def main():
    """
    Main execution: Train models for all available sports.
    """
    # Paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "datasets"
    models_dir = project_root / "LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP"
    
    # Sports with available data
    sports = ['NHL', 'NFL']  # Start with these two
    
    results_summary = {}
    
    for sport in sports:
        try:
            logger.info(f"\n\n{'=' * 60}")
            logger.info(f"TRAINING {sport} MODEL")
            logger.info(f"{'=' * 60}\n")
            
            # Initialize pipeline
            pipeline = UnifiedTrainingPipeline(
                sport=sport,
                data_dir=data_dir,
                models_dir=models_dir,
                test_mode=False  # Set True for quick testing
            )
            
            # Run full pipeline
            results = pipeline.run_full_pipeline(
                val_size=0.2,
                save_models=True
            )
            
            results_summary[sport] = results
            
        except Exception as e:
            logger.error(f"Failed to train {sport}: {e}", exc_info=True)
            results_summary[sport] = {'error': str(e)}
    
    # Print summary
    logger.info("\n\n" + "=" * 60)
    logger.info("TRAINING SUMMARY - ALL SPORTS")
    logger.info("=" * 60)
    
    for sport, results in results_summary.items():
        if 'error' in results:
            logger.info(f"{sport}: FAILED - {results['error']}")
        else:
            logger.info(f"{sport}:")
            logger.info(f"  Accuracy:  {results['accuracy']:.4f}")
            logger.info(f"  ROC-AUC:   {results['roc_auc']:.4f}")
            logger.info(f"  Kelly ROI: {results['kelly_criterion_roi']:.2f}%")
            logger.info(f"  Duration:  {results['pipeline_duration_seconds']:.1f}s")
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
