"""
Time-Series Cross-Validation Framework for Sports Predictions

CRITICAL: Sports prediction data MUST NOT be shuffled during validation!

Traditional shuffle-based cross-validation causes data leakage:
- Future game information leaks into past training data
- Model appears accurate but fails in real-world deployment
- Accuracy drops from 55% in validation to 45-48% in production

Solution: Walk-Forward Validation
- Train on historical data
- Test on future data
- Move window forward, never backwards
- Respects temporal causality

This mimics real-world betting:
- You see past 3 years of games
- You predict next week's games
- You evaluate accuracy on those outcomes
- Then you have new data and retrain
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict
import logging
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

# Optional imports for advanced models
try:
    import xgboost as xgb
except ImportError:
    xgb = None

try:
    import lightgbm as lgb
except ImportError:
    lgb = None

logger = logging.getLogger("time_series_validation")


class TimeSeriesValidator:
    """
    Walk-forward time-series validation for sports predictions
    
    Ensures proper temporal ordering and prevents data leakage
    """
    
    def __init__(self, n_splits: int = 5):
        """
        Initialize time-series validator
        
        Args:
            n_splits: Number of train/test splits (default 5)
        """
        self.n_splits = n_splits
        self.cv_results = []
        self.split_info = []
        self.logger = logger
    
    # ========================================================================
    # WALK-FORWARD VALIDATION
    # ========================================================================
    
    def walk_forward_split(self, X: pd.DataFrame, y: pd.Series, 
                          min_train_size: int = 300) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Walk-forward time-series split
        
        Key features:
        - Training set is FIXED at beginning
        - Test set grows over time
        - Never looks into future
        - Respects temporal causality
        
        Example with min_train_size=300:
        Split 1: Train [0:300]    → Test [300:350]
        Split 2: Train [0:350]    → Test [350:400]
        Split 3: Train [0:400]    → Test [400:450]
        Split 4: Train [0:450]    → Test [450:500]
        Split 5: Train [0:500]    → Test [500:end]
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target vector (n_samples,)
            min_train_size: Minimum training samples (default 300 games)
        
        Yields:
            (train_indices, test_indices) tuples
        """
        n_samples = len(X)
        if min_train_size < 100:
            self.logger.warning("min_train_size < 100 may be too small")
        
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        
        for i, (train_idx, test_idx) in enumerate(tscv.split(X)):
            # Ensure we have at least min_train_size training samples
            if len(train_idx) < min_train_size:
                self.logger.warning(f"Split {i}: train size {len(train_idx)} < {min_train_size}")
            
            self.logger.info(f"Split {i}: Train [{train_idx[0]}:{train_idx[-1]}] → Test [{test_idx[0]}:{test_idx[-1]}]")
            self.logger.info(f"  Train size: {len(train_idx)}, Test size: {len(test_idx)}")
            
            yield train_idx, test_idx
    
    # ========================================================================
    # SEASON-BASED SPLIT
    # ========================================================================
    
    def season_based_split(self, X: pd.DataFrame, y: pd.Series, 
                          season_col: str = 'season') -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Season-by-season cross-validation
        
        For sports data with explicit season column:
        - Train on seasons 1-3
        - Test on season 4
        - Train on seasons 1-4
        - Test on season 5
        - etc.
        
        More realistic for sports (seasons are natural splits)
        
        Args:
            X: Feature matrix (must include season column)
            y: Target vector
            season_col: Column name for season identifier
        
        Yields:
            (train_indices, test_indices) tuples
        """
        if season_col not in X.columns:
            raise ValueError(f"Column '{season_col}' not found in X")
        
        seasons = sorted(X[season_col].unique())
        n_seasons = len(seasons)
        
        if n_seasons < 2:
            raise ValueError("Need at least 2 seasons for validation")
        
        self.logger.info(f"Season-based split: {n_seasons} seasons found")
        self.logger.info(f"Seasons: {seasons}")
        
        # Train on progressively more seasons, test on next season
        for test_season_idx in range(1, n_seasons):
            train_seasons = seasons[:test_season_idx]
            test_season = seasons[test_season_idx]
            
            train_mask = X[season_col].isin(train_seasons)
            test_mask = X[season_col] == test_season
            
            train_idx = np.where(train_mask)[0]
            test_idx = np.where(test_mask)[0]
            
            self.logger.info(f"Train on {train_seasons} → Test on {test_season}")
            self.logger.info(f"  Train size: {len(train_idx)}, Test size: {len(test_idx)}")
            
            yield train_idx, test_idx
    
    # ========================================================================
    # SLIDING WINDOW VALIDATION
    # ========================================================================
    
    def sliding_window_split(self, X: pd.DataFrame, y: pd.Series,
                            window_size: int = 300,
                            step_size: int = 100) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Sliding window validation
        
        More aggressive than walk-forward (smaller training sets)
        
        Example with window_size=300, step_size=100:
        Split 1: Train [0:300]    → Test [300:400]
        Split 2: Train [100:400]  → Test [400:500]
        Split 3: Train [200:500]  → Test [500:600]
        etc.
        
        Args:
            X: Feature matrix
            y: Target vector
            window_size: Size of training window
            step_size: How much to slide window forward
        
        Yields:
            (train_indices, test_indices) tuples
        """
        n_samples = len(X)
        
        split_num = 0
        for start_idx in range(0, n_samples - window_size - 1, step_size):
            train_start = start_idx
            train_end = start_idx + window_size
            test_start = train_end
            test_end = min(test_start + 100, n_samples)  # 100-game test set
            
            if test_end - test_start < 50:
                # Skip if test set too small
                continue
            
            train_idx = np.arange(train_start, train_end)
            test_idx = np.arange(test_start, test_end)
            
            self.logger.info(f"Split {split_num}: Train [{train_start}:{train_end}] → Test [{test_start}:{test_end}]")
            
            split_num += 1
            yield train_idx, test_idx
    
    # ========================================================================
    # CROSS-VALIDATION EVALUATION
    # ========================================================================
    
    def evaluate_model_cv(self, model, X: pd.DataFrame, y: pd.Series,
                         split_method: str = 'walk_forward') -> Dict:
        """
        Evaluate model using time-series cross-validation
        
        Args:
            model: Sklearn-compatible model with fit() and predict_proba()
            X: Feature matrix
            y: Target vector
            split_method: 'walk_forward', 'season_based', or 'sliding_window'
        
        Returns:
            Dictionary with CV results
        """
        self.logger.info(f"Evaluating model with {split_method} CV...")
        
        # Get split generator
        if split_method == 'walk_forward':
            splits = self.walk_forward_split(X, y)
        elif split_method == 'season_based':
            splits = self.season_based_split(X, y)
        elif split_method == 'sliding_window':
            splits = self.sliding_window_split(X, y)
        else:
            raise ValueError(f"Unknown split method: {split_method}")
        
        fold_scores = []
        fold_details = []
        
        for fold, (train_idx, test_idx) in enumerate(splits):
            self.logger.info(f"\n--- Fold {fold} ---")
            
            # Split data
            X_train = X.iloc[train_idx]
            y_train = y.iloc[train_idx]
            X_test = X.iloc[test_idx]
            y_test = y.iloc[test_idx]
            
            # Train model
            try:
                model.fit(X_train, y_train)
            except Exception as e:
                self.logger.error(f"Error training model on fold {fold}: {e}")
                continue
            
            # Predict
            try:
                y_pred_proba = model.predict_proba(X_test)[:, 1]
            except Exception as e:
                self.logger.error(f"Error predicting on fold {fold}: {e}")
                continue
            
            # Evaluate
            from sklearn.metrics import accuracy_score, roc_auc_score, log_loss
            
            acc = accuracy_score(y_test, y_pred_proba > 0.5)
            auc = roc_auc_score(y_test, y_pred_proba)
            ll = log_loss(y_test, y_pred_proba)
            
            self.logger.info(f"  Accuracy: {acc:.4f}")
            self.logger.info(f"  ROC-AUC: {auc:.4f}")
            self.logger.info(f"  Log Loss: {ll:.4f}")
            
            fold_scores.append({
                'fold': fold,
                'accuracy': acc,
                'roc_auc': auc,
                'log_loss': ll,
                'n_train': len(train_idx),
                'n_test': len(test_idx)
            })
            
            fold_details.append({
                'fold': fold,
                'y_test': y_test.values,
                'y_pred_proba': y_pred_proba,
                'indices': test_idx
            })
        
        # Aggregate results
        results = {
            'method': split_method,
            'fold_scores': fold_scores,
            'fold_details': fold_details,
            'mean_accuracy': np.mean([f['accuracy'] for f in fold_scores]),
            'std_accuracy': np.std([f['accuracy'] for f in fold_scores]),
            'mean_roc_auc': np.mean([f['roc_auc'] for f in fold_scores]),
            'std_roc_auc': np.std([f['roc_auc'] for f in fold_scores]),
            'mean_log_loss': np.mean([f['log_loss'] for f in fold_scores]),
        }
        
        self.cv_results.append(results)
        
        return results
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def print_cv_summary(self, results: Dict):
        """Print cross-validation summary"""
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║               TIME-SERIES CROSS-VALIDATION RESULTS                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

Method: {results['method'].upper()}
Number of Folds: {len(results['fold_scores'])}

INDIVIDUAL FOLD RESULTS
────────────────────────────────────────────────────────────────────────────────
"""
        
        for fold in results['fold_scores']:
            report += f"""
Fold {fold['fold']}:
  Train Size: {fold['n_train']:,} games
  Test Size:  {fold['n_test']:,} games
  Accuracy:   {fold['accuracy']:.4f}
  ROC-AUC:    {fold['roc_auc']:.4f}
  Log Loss:   {fold['log_loss']:.4f}
"""
        
        report += f"""
AGGREGATE RESULTS
────────────────────────────────────────────────────────────────────────────────

Mean Accuracy:    {results['mean_accuracy']:.4f} ± {results['std_accuracy']:.4f}
Mean ROC-AUC:     {results['mean_roc_auc']:.4f} ± {results['std_roc_auc']:.4f}
Mean Log Loss:    {results['mean_log_loss']:.4f}

INTERPRETATION
────────────────────────────────────────────────────────────────────────────────

Accuracy > 0.55:
  ✓ Model has predictive edge over 50% random baseline
  ✓ Can be profitable with proper bet sizing

ROC-AUC > 0.55:
  ✓ Good discrimination ability
  ✓ Model properly ranks predictions by confidence

Consistency (Low Std):
  ✓ Performance stable across time periods
  ✗ High std = model sensitive to season changes

═════════════════════════════════════════════════════════════════════════════════
"""
        return report


class DataLeakageDetector:
    """
    Detect common data leakage issues in sports predictions
    """
    
    @staticmethod
    def check_temporal_overlap(X_train: pd.DataFrame, X_test: pd.DataFrame,
                              date_col: str = 'game_date') -> bool:
        """
        Check if training and test sets overlap temporally
        
        Data leakage if: max(train_date) >= min(test_date)
        """
        if date_col not in X_train.columns or date_col not in X_test.columns:
            return True  # Can't check, assume OK
        
        max_train_date = X_train[date_col].max()
        min_test_date = X_test[date_col].min()
        
        if max_train_date >= min_test_date:
            logger.error(f"⚠ TEMPORAL LEAKAGE DETECTED!")
            logger.error(f"  Max train date: {max_train_date}")
            logger.error(f"  Min test date:  {min_test_date}")
            return False
        
        logger.info(f"✓ No temporal leakage")
        logger.info(f"  Train: {X_train[date_col].min()} to {max_train_date}")
        logger.info(f"  Test:  {min_test_date} to {X_test[date_col].max()}")
        return True
    
    @staticmethod
    def check_future_information(feature_names: List[str]) -> bool:
        """
        Check if features contain obvious future information
        
        Suspicious features:
        - 'actual_final_score'
        - 'actual_winner'
        - 'is_winner'
        - 'final_margin'
        """
        suspicious = ['actual_', 'final_', 'is_winner', 'margin', 'outcome']
        
        leakage_found = False
        for feature in feature_names:
            for sus in suspicious:
                if sus in feature.lower():
                    logger.error(f"⚠ SUSPICIOUS FEATURE: {feature}")
                    logger.error(f"  This feature may contain future information!")
                    leakage_found = True
        
        if not leakage_found:
            logger.info("✓ No obviously leaked features detected")
        
        return not leakage_found
    
    @staticmethod
    def check_feature_stationarity(X: pd.DataFrame, lookback: int = 100) -> Dict:
        """
        Check if features are stationary over time
        
        Non-stationary features can cause temporal leakage:
        - Mean shifts over time
        - Variance changes
        - Trends present
        """
        from scipy import stats
        
        results = {}
        for col in X.select_dtypes(include=[np.number]).columns:
            # Split into early and late periods
            early = X[col].iloc[:lookback].dropna()
            late = X[col].iloc[-lookback:].dropna()
            
            if len(early) > 1 and len(late) > 1:
                # Kolmogorov-Smirnov test
                stat, p_value = stats.ks_2samp(early, late)
                
                results[col] = {
                    'mean_early': early.mean(),
                    'mean_late': late.mean(),
                    'ks_statistic': stat,
                    'p_value': p_value,
                    'is_stationary': p_value > 0.05
                }
        
        return results


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create sample data
    n_samples = 2000
    n_features = 20
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    # Add season column
    X['season'] = np.repeat([2020, 2021, 2022, 2023], n_samples // 4)
    X['game_date'] = pd.date_range('2020-10-01', periods=n_samples, freq='D')
    
    # Create target (slightly better than random)
    y = pd.Series(np.random.binomial(1, 0.52, n_samples))
    
    # Validate
    validator = TimeSeriesValidator(n_splits=5)
    
    # Walk-forward validation
    results = validator.evaluate_model_cv(
        RandomForestClassifier(n_estimators=100, random_state=42),
        X, y,
        split_method='walk_forward'
    )
    print(validator.print_cv_summary(results))
    
    # Season-based validation
    results_season = validator.evaluate_model_cv(
        RandomForestClassifier(n_estimators=100, random_state=42),
        X, y,
        split_method='season_based'
    )
    print(validator.print_cv_summary(results_season))
    
    # Check for leakage
    detector = DataLeakageDetector()
    detector.check_temporal_overlap(X, X, date_col='game_date')
    detector.check_future_information(X.columns.tolist())
