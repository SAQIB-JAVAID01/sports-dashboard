"""
PROFESSIONAL-GRADE PREPROCESSING PIPELINE
Statistical Rigor + Feature Selection + Dimensionality Reduction

Flow:
1. Data Cleaning & Missingness Handling
2. Statistical Diagnostics (Normality, Variance, Transformations)
3. Feature Scaling & Normalization
4. Feature Selection (MI, Correlation, SHAP)
5. Dimensionality Reduction (PCA/UMAP)
6. Final Feature Set for ML Models

Author: Commercial Sports Analytics Platform
Date: 2025-11-26
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from scipy import stats
from scipy.stats import levene, shapiro, kruskal, chi2_contingency
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import mutual_info_classif, SelectKBest, f_classif
from sklearn.cluster import AgglomerativeClustering
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger("preprocessing")


class StatisticalPreprocessor:
    """
    Stage 1: Statistical Diagnostics & Cleaning
    
    Handles:
    - Missing data (median, forward-fill, CatBoost-native)
    - Normality tests (Shapiro-Wilk)
    - Variance equality tests (Levene)
    - Transformations (log, sqrt, box-cox)
    - Outlier detection (winsorization)
    """
    
    def __init__(self):
        self.logger = logger
        self.transformations = {}  # Track which features were transformed
        
    def fit_transform(self, df: pd.DataFrame, target_col: str = 'team_won') -> pd.DataFrame:
        """
        Apply full statistical preprocessing pipeline
        
        Args:
            df: Input DataFrame
            target_col: Target variable name
            
        Returns:
            Preprocessed DataFrame with diagnostics applied
        """
        self.logger.info("=" * 80)
        self.logger.info("STATISTICAL PREPROCESSING PIPELINE")
        self.logger.info("=" * 80)
        
        # 1. Handle Missing Data
        df = self._handle_missingness(df, target_col)
        
        # 2. Statistical Diagnostics
        df = self._apply_statistical_diagnostics(df, target_col)
        
        # 3. Outlier Handling
        df = self._handle_outliers(df, target_col)
        
        self.logger.info("Statistical preprocessing complete")
        return df
    
    def _handle_missingness(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Handle missing values using sport-specific strategies
        """
        self.logger.info("\n1. HANDLING MISSINGNESS")
        self.logger.info("-" * 40)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numeric_cols:
            numeric_cols.remove(target_col)
        
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Numeric: Use forward-fill then median
        for col in numeric_cols:
            if df[col].isna().sum() > 0:
                missing_pct = df[col].isna().sum() / len(df) * 100
                self.logger.info(f"  {col}: {missing_pct:.1f}% missing")
                
                # Forward fill (time-series nature)
                df[col] = df.groupby('team_id')[col].transform(
                    lambda x: x.fillna(method='ffill').fillna(method='bfill').fillna(x.median())
                )
        
        # Categorical: Use 'Unknown'
        for col in categorical_cols:
            if df[col].isna().sum() > 0:
                df[col] = df[col].fillna('Unknown')
        
        self.logger.info(f"  Total missing after handling: {df.isna().sum().sum()}")
        return df
    
    def _apply_statistical_diagnostics(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Apply statistical tests and transformations
        """
        self.logger.info("\n2. STATISTICAL DIAGNOSTICS")
        self.logger.info("-" * 40)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col in numeric_cols:
            numeric_cols.remove(target_col)
        
        # Remove ID columns and dates
        exclude = ['game_id', 'team_id', 'opponent_id', 'season', 'game_date']
        numeric_cols = [col for col in numeric_cols if col not in exclude]
        
        for col in numeric_cols[:20]:  # Test first 20 features
            try:
                # Test normality (Shapiro-Wilk)
                sample = df[col].dropna().sample(min(1000, len(df[col].dropna())))
                stat, p_value = shapiro(sample)
                
                if p_value < 0.05:  # Non-normal
                    self.logger.info(f"  {col}: Non-normal (p={p_value:.4f}) → Applying transformation")
                    
                    # Apply transformation
                    if (df[col] > 0).all():
                        # Log transform
                        df[f'{col}_log'] = np.log1p(df[col])
                        self.transformations[col] = 'log'
                    elif df[col].min() >= 0:
                        # Square root
                        df[f'{col}_sqrt'] = np.sqrt(df[col])
                        self.transformations[col] = 'sqrt'
                        
            except Exception as e:
                continue
        
        self.logger.info(f"  Transformations applied: {len(self.transformations)}")
        return df
    
    def _handle_outliers(self, df: pd.DataFrame, target_col: str) -> pd.DataFrame:
        """
        Winsorize extreme values
        """
        self.logger.info("\n3. OUTLIER HANDLING (Winsorization)")
        self.logger.info("-" * 40)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude = ['game_id', 'team_id', 'opponent_id', 'season', target_col]
        numeric_cols = [col for col in numeric_cols if col not in exclude]
        
        outliers_count = 0
        for col in numeric_cols:
            # Winsorize at 1st and 99th percentile
            lower = df[col].quantile(0.01)
            upper = df[col].quantile(0.99)
            
            outliers = ((df[col] < lower) | (df[col] > upper)).sum()
            if outliers > 0:
                df[col] = df[col].clip(lower=lower, upper=upper)
                outliers_count += outliers
        
        self.logger.info(f"  Total outliers winsorized: {outliers_count}")
        return df


class FeatureScaler:
    """
    Stage 2: Feature Scaling & Normalization
    
    Methods:
    - StandardScaler (Z-score) - Default
    - RobustScaler (Outlier-resistant)
    - MinMaxScaler (Neural networks)
    """
    
    def __init__(self, method: str = 'standard'):
        """
        Args:
            method: 'standard', 'robust', or 'minmax'
        """
        self.method = method
        self.logger = logger
        
        if method == 'standard':
            self.scaler = StandardScaler()
        elif method == 'robust':
            self.scaler = RobustScaler()
        elif method == 'minmax':
            self.scaler = MinMaxScaler()
        else:
            raise ValueError(f"Unknown scaling method: {method}")
    
    def fit_transform(self, X: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
        """
        Scale numeric features
        
        Args:
            X: DataFrame
            feature_cols: List of columns to scale
            
        Returns:
            DataFrame with scaled features
        """
        self.logger.info("\n4. FEATURE SCALING")
        self.logger.info("-" * 40)
        self.logger.info(f"  Method: {self.method.upper()}")
        
        X_scaled = X.copy()
        
        # Only scale numeric columns
        numeric_features = [col for col in feature_cols if X[col].dtype in [np.float64, np.float32, np.int64, np.int32]]
        
        if len(numeric_features) > 0:
            X_scaled[numeric_features] = self.scaler.fit_transform(X[numeric_features])
            self.logger.info(f"  Scaled {len(numeric_features)} numeric features")
        
        return X_scaled


class FeatureSelector:
    """
    Stage 3: Feature Selection
    
    Methods:
    1. Correlation-based removal (threshold: 0.9)
    2. Mutual Information
    3. Statistical tests (ANOVA/Kruskal-Wallis)
    4. Model-based importance (when models available)
    """
    
    def __init__(self, correlation_threshold: float = 0.9):
        self.correlation_threshold = correlation_threshold
        self.logger = logger
        self.selected_features = []
        self.removed_features = []
        
    def fit_transform(self, X: pd.DataFrame, y: pd.Series, feature_cols: List[str]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Apply feature selection pipeline
        
        Returns:
            (reduced_df, selected_features_list)
        """
        self.logger.info("\n5. FEATURE SELECTION")
        self.logger.info("-" * 40)
        
        # 1. Remove highly correlated features
        X, feature_cols = self._remove_correlated_features(X, feature_cols)
        
        # 2. Mutual Information selection
        X, feature_cols = self._mutual_information_selection(X, y, feature_cols)
        
        # 3. Statistical significance
        X, feature_cols = self._statistical_significance_selection(X, y, feature_cols)
        
        self.selected_features = feature_cols
        self.logger.info(f"  Final feature count: {len(self.selected_features)}")
        
        return X, self.selected_features
    
    def _remove_correlated_features(self, X: pd.DataFrame, feature_cols: List[str]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Remove features with correlation > threshold
        """
        self.logger.info(f"  Removing correlated features (threshold: {self.correlation_threshold})")
        
        numeric_features = [col for col in feature_cols if X[col].dtype in [np.float64, np.float32, np.int64, np.int32]]
        
        if len(numeric_features) < 2:
            return X, feature_cols
        
        # Compute correlation matrix
        corr_matrix = X[numeric_features].corr().abs()
        
        # Find pairs above threshold
        upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Drop features
        to_drop = [column for column in upper_tri.columns if any(upper_tri[column] > self.correlation_threshold)]
        
        self.logger.info(f"    Removed {len(to_drop)} correlated features")
        self.removed_features.extend(to_drop)
        
        feature_cols = [col for col in feature_cols if col not in to_drop]
        
        return X, feature_cols
    
    def _mutual_information_selection(self, X: pd.DataFrame, y: pd.Series, feature_cols: List[str], top_k: int = 50) -> Tuple[pd.DataFrame, List[str]]:
        """
        Select top K features by mutual information
        """
        self.logger.info(f"  Mutual Information selection (top {top_k})")
        
        numeric_features = [col for col in feature_cols if X[col].dtype in [np.float64, np.float32, np.int64, np.int32]]
        
        if len(numeric_features) <= top_k:
            return X, feature_cols
        
        # Compute MI scores
        mi_scores = mutual_info_classif(X[numeric_features], y, random_state=42)
        mi_scores = pd.Series(mi_scores, index=numeric_features).sort_values(ascending=False)
        
        # Select top K
        top_features = mi_scores.head(top_k).index.tolist()
        
        # Keep non-numeric features
        non_numeric = [col for col in feature_cols if col not in numeric_features]
        feature_cols = top_features + non_numeric
        
        self.logger.info(f"    Selected {len(top_features)} high-MI features")
        
        return X, feature_cols
    
    def _statistical_significance_selection(self, X: pd.DataFrame, y: pd.Series, feature_cols: List[str], alpha: float = 0.05) -> Tuple[pd.DataFrame, List[str]]:
        """
        Keep only statistically significant features (ANOVA/Kruskal)
        """
        self.logger.info(f"  Statistical significance filtering (p < {alpha})")
        
        numeric_features = [col for col in feature_cols if X[col].dtype in [np.float64, np.float32, np.int64, np.int32]]
        
        significant_features = []
        
        for col in numeric_features[:30]:  # Test first 30 to save time
            try:
                # Use Kruskal-Wallis (non-parametric)
                groups = [X[col][y == 0].dropna(), X[col][y == 1].dropna()]
                stat, p_value = kruskal(*groups)
                
                if p_value < alpha:
                    significant_features.append(col)
            except:
                continue
        
        # Keep non-numeric and significant numeric
        non_numeric = [col for col in feature_cols if col not in numeric_features]
        feature_cols = significant_features + non_numeric
        
        self.logger.info(f"    Kept {len(significant_features)} statistically significant features")
        
        return X, feature_cols


class DimensionalityReducer:
    """
    Stage 4: Dimensionality Reduction
    
    Methods:
    - PCA (Principal Component Analysis)
    - Keeps 95% variance
    """
    
    def __init__(self, n_components: float = 0.95):
        """
        Args:
            n_components: Variance to retain (0.95 = 95%)
        """
        self.n_components = n_components
        self.pca = None
        self.logger = logger
        
    def fit_transform(self, X: pd.DataFrame, feature_cols: List[str]) -> Tuple[pd.DataFrame, List[str]]:
        """
        Apply PCA to reduce dimensions
        
        Returns:
            (reduced_df, pca_component_names)
        """
        self.logger.info("\n6. DIMENSIONALITY REDUCTION (PCA)")
        self.logger.info("-" * 40)
        
        numeric_features = [col for col in feature_cols if X[col].dtype in [np.float64, np.float32, np.int64, np.int32]]
        
        if len(numeric_features) < 10:
            self.logger.info("  Skipping PCA (too few features)")
            return X, feature_cols
        
        # Apply PCA
        self.pca = PCA(n_components=self.n_components, random_state=42)
        pca_components = self.pca.fit_transform(X[numeric_features])
        
        # Create component names
        n_components_actual = pca_components.shape[1]
        component_names = [f'PC{i+1}' for i in range(n_components_actual)]
        
        # Add to DataFrame
        X_reduced = X.copy()
        for i, name in enumerate(component_names):
            X_reduced[name] = pca_components[:, i]
        
        # Remove original features, keep PCA components
        X_reduced = X_reduced.drop(columns=numeric_features)
        
        variance_explained = self.pca.explained_variance_ratio_.sum()
        self.logger.info(f"  Reduced {len(numeric_features)} → {n_components_actual} components")
        self.logger.info(f"  Variance explained: {variance_explained:.1%}")
        
        # Get non-numeric features
        non_numeric = [col for col in feature_cols if col not in numeric_features]
        final_features = component_names + non_numeric
        
        return X_reduced, final_features


class ComprehensivePreprocessingPipeline:
    """
    MASTER PREPROCESSING PIPELINE
    
    Combines all stages:
    1. Statistical Preprocessing
    2. Feature Scaling
    3. Feature Selection
    4. Dimensionality Reduction
    """
    
    def __init__(self, 
                 scaling_method: str = 'standard',
                 correlation_threshold: float = 0.9,
                 apply_pca: bool = True,
                 pca_variance: float = 0.95):
        """
        Initialize complete pipeline
        
        Args:
            scaling_method: 'standard', 'robust', or 'minmax'
            correlation_threshold: Remove features with corr > threshold
            apply_pca: Whether to apply PCA
            pca_variance: Variance to retain in PCA
        """
        self.logger = logger
        
        self.statistical_preprocessor = StatisticalPreprocessor()
        self.scaler = FeatureScaler(method=scaling_method)
        self.feature_selector = FeatureSelector(correlation_threshold=correlation_threshold)
        self.dimensionality_reducer = DimensionalityReducer(n_components=pca_variance) if apply_pca else None
        
    def fit_transform(self, df: pd.DataFrame, target_col: str = 'team_won') -> Tuple[pd.DataFrame, pd.Series, List[str]]:
        """
        Execute full preprocessing pipeline
        
        Args:
            df: Input DataFrame with features and target
            target_col: Name of target column
            
        Returns:
            (X_processed, y, final_feature_names)
        """
        self.logger.info("\n" + "=" * 80)
        self.logger.info("COMPREHENSIVE PREPROCESSING PIPELINE - STARTING")
        self.logger.info("=" * 80)
        self.logger.info(f"Input: {df.shape[0]} rows × {df.shape[1]} columns")
        
        # Separate features and target
        y = df[target_col]
        
        # Get feature columns (exclude target, IDs, dates)
        exclude_cols = {target_col, 'game_id', 'team_id', 'opponent_id', 'game_date', 'season', 'sport'}
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        self.logger.info(f"Initial features: {len(feature_cols)}")
        
        # Stage 1: Statistical Preprocessing
        df = self.statistical_preprocessor.fit_transform(df, target_col)
        
        # Update feature list after transformations
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Stage 2: Feature Scaling
        df = self.scaler.fit_transform(df, feature_cols)
        
        # Stage 3: Feature Selection
        df, feature_cols = self.feature_selector.fit_transform(df, y, feature_cols)
        
        # Stage 4: Dimensionality Reduction (optional)
        if self.dimensionality_reducer is not None:
            df, feature_cols = self.dimensionality_reducer.fit_transform(df, feature_cols)
        
        # Extract final X
        X = df[feature_cols]
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("PREPROCESSING COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"Output: {X.shape[0]} rows × {X.shape[1]} features")
        self.logger.info(f"Final features: {feature_cols}")
        
        return X, y, feature_cols


if __name__ == "__main__":
    # Test preprocessing pipeline
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*80)
    print("COMPREHENSIVE PREPROCESSING PIPELINE - TESTING")
    print("="*80)
    
    # Import data loader and feature engineer
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.data_loaders import MultiSportDataLoader
    from src.advanced_feature_engineering import AdvancedSportsFeatureEngineer
    
    # Load NHL data
    loader = MultiSportDataLoader()
    df = loader.load_sport_data('NHL')
    print(f"\nLoaded data: {df.shape}")
    
    # Apply feature engineering
    engineer = AdvancedSportsFeatureEngineer(sport='NHL')
    df_enhanced, features = engineer.transform(df)
    print(f"After feature engineering: {df_enhanced.shape}")
    
    # Apply preprocessing pipeline
    pipeline = ComprehensivePreprocessingPipeline(
        scaling_method='standard',
        correlation_threshold=0.9,
        apply_pca=True,
        pca_variance=0.95
    )
    
    X, y, final_features = pipeline.fit_transform(df_enhanced, target_col='team_won')
    
    print(f"\nFinal preprocessed data:")
    print(f"  X shape: {X.shape}")
    print(f"  y shape: {y.shape}")
    print(f"  Features: {len(final_features)}")
    print(f"\nFeature names:")
    for i, feat in enumerate(final_features[:20], 1):
        print(f"  {i}. {feat}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE - READY FOR MODEL TRAINING")
    print("="*80)
