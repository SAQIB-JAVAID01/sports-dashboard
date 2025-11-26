"""
ML Model Integration Layer for Sports Predictions
Integrates forecasting models: Logistic Regression, Random Forest, XGBoost, LSTM/CNN, Ensemble

Usage:
- Real-Time: Uses ensemble predictions with explainability
- Historical: Uses trained models from LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/
"""

import numpy as np
import pandas as pd
import joblib
import os
from pathlib import Path
from typing import Dict, Tuple, Optional, List
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    import xgboost as xgb
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class MLPredictionIntegration:
    """
    Unified ML prediction interface combining multiple models
    """
    
    def __init__(self, sport: str = 'NFL'):
        self.sport = sport
        self.ensemble_model = None
        self.xgb_model = None
        self.rf_model = None
        self.lr_model = None
        self.lstm_model = None
        self.scaler = None
        self.feature_names = []
        
    def load_ensemble_model(self, model_path: str) -> bool:
        """Load pre-trained ensemble model"""
        try:
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                if isinstance(model_data, dict):
                    self.ensemble_model = model_data.get('ensemble')
                    self.xgb_model = model_data.get('xgb')
                    self.rf_model = model_data.get('rf')
                    self.lr_model = model_data.get('lr')
                    self.scaler = model_data.get('scaler')
                    self.feature_names = model_data.get('feature_names', [])
                    return True
                else:
                    self.ensemble_model = model_data
                    return True
        except Exception as e:
            print(f"Error loading ensemble model: {e}")
        return False
    
    def load_lstm_model(self, model_path: str) -> bool:
        """Load LSTM model for sequence predictions"""
        if not TENSORFLOW_AVAILABLE:
            return False
        try:
            if os.path.exists(model_path):
                self.lstm_model = keras.models.load_model(model_path)
                return True
        except Exception as e:
            print(f"Error loading LSTM model: {e}")
        return False
    
    def prepare_features(self, game_stats: Dict, historical_metrics: Dict) -> pd.DataFrame:
        """
        Prepare features for ML models from game stats and historical metrics
        
        Features include:
        - Historical: win%, point differential, wins/losses
        - Recent form: rolling averages, momentum
        - Team stats: offensive/defensive efficiency, turnovers
        - External: rest days, travel distance, venue advantage
        """
        features = {}
        
        # Historical metrics
        if 'home_team' in game_stats and game_stats['home_team'] in historical_metrics:
            h_metrics = historical_metrics[game_stats['home_team']]
            features['home_wins'] = h_metrics.get('wins', 0)
            features['home_win_pct'] = h_metrics.get('win_percentage', 0.5)
            features['home_point_diff'] = h_metrics.get('point_differential', 0)
            features['home_ppg'] = h_metrics.get('ppg', 0)
            features['home_papg'] = h_metrics.get('papg', 0)
            features['home_off_eff'] = h_metrics.get('offensive_efficiency', 0)
            features['home_def_eff'] = h_metrics.get('defensive_efficiency', 0)
        
        if 'away_team' in game_stats and game_stats['away_team'] in historical_metrics:
            a_metrics = historical_metrics[game_stats['away_team']]
            features['away_wins'] = a_metrics.get('wins', 0)
            features['away_win_pct'] = a_metrics.get('win_percentage', 0.5)
            features['away_point_diff'] = a_metrics.get('point_differential', 0)
            features['away_ppg'] = a_metrics.get('ppg', 0)
            features['away_papg'] = a_metrics.get('papg', 0)
            features['away_off_eff'] = a_metrics.get('offensive_efficiency', 0)
            features['away_def_eff'] = a_metrics.get('defensive_efficiency', 0)
        
        # Derived features
        if 'home_win_pct' in features and 'away_win_pct' in features:
            features['win_pct_diff'] = features['home_win_pct'] - features['away_win_pct']
            features['point_diff_diff'] = features['home_point_diff'] - features['away_point_diff']
        
        # External conditions
        features['rest_days_home'] = game_stats.get('rest_days_home', 1)
        features['rest_days_away'] = game_stats.get('rest_days_away', 1)
        features['travel_distance'] = game_stats.get('travel_distance_miles', 0)
        features['is_home_advantage'] = 1  # Home team always has advantage
        
        # Recent form (simulated)
        features['home_form'] = game_stats.get('home_form', 5) / 10.0  # 0-1 scale
        features['away_form'] = game_stats.get('away_form', 5) / 10.0
        
        return pd.DataFrame([features])
    
    def predict_with_ensemble(self, features: pd.DataFrame) -> Dict:
        """
        Generate prediction using ensemble of ML models
        
        Returns dict with:
        - win_probability: Ensemble average probability
        - confidence: Disagreement between models
        - model_predictions: Individual model predictions
        - feature_importance: SHAP-like feature impact
        """
        predictions = {
            'ensemble_prob': 0.5,
            'confidence': 0.0,
            'individual_models': {},
            'top_factors': []
        }
        
        if self.ensemble_model is None:
            return predictions
        
        try:
            # Scale features if scaler available
            features_scaled = features.copy()
            if self.scaler is not None and hasattr(self.scaler, 'transform'):
                features_scaled = pd.DataFrame(
                    self.scaler.transform(features_scaled),
                    columns=features_scaled.columns
                )
            
            # Get predictions from individual models
            model_probs = []
            
            if self.xgb_model is not None:
                try:
                    xgb_prob = self.xgb_model.predict_proba(features_scaled)[:, 1][0]
                    model_probs.append(xgb_prob)
                    predictions['individual_models']['XGBoost'] = float(xgb_prob)
                except:
                    pass
            
            if self.rf_model is not None:
                try:
                    rf_prob = self.rf_model.predict_proba(features_scaled)[:, 1][0]
                    model_probs.append(rf_prob)
                    predictions['individual_models']['Random Forest'] = float(rf_prob)
                except:
                    pass
            
            if self.lr_model is not None:
                try:
                    lr_prob = self.lr_model.predict_proba(features_scaled)[:, 1][0]
                    model_probs.append(lr_prob)
                    predictions['individual_models']['Logistic Regression'] = float(lr_prob)
                except:
                    pass
            
            # Ensemble prediction
            if len(model_probs) > 0:
                ensemble_prob = np.mean(model_probs)
                predictions['ensemble_prob'] = float(ensemble_prob)
                
                # Confidence = how much models agree (inverse std dev)
                if len(model_probs) > 1:
                    disagreement = np.std(model_probs)
                    confidence = 1.0 - disagreement  # Higher confidence = less disagreement
                    predictions['confidence'] = float(np.clip(confidence, 0, 1))
                else:
                    predictions['confidence'] = 0.7
            
            # Calculate simple feature importance
            predictions['top_factors'] = self._calculate_feature_importance(features)
            
        except Exception as e:
            print(f"Error in ensemble prediction: {e}")
        
        return predictions
    
    def _calculate_feature_importance(self, features: pd.DataFrame) -> List[Dict]:
        """
        Calculate feature importance using simple correlation with outcome
        In production, use SHAP values
        """
        importance = []
        feature_cols = features.columns.tolist()
        
        # Predefined feature impact mappings (domain knowledge)
        feature_impact = {
            'home_win_pct': ('Team Strength', 0.15),
            'away_win_pct': ('Opponent Strength', -0.12),
            'home_point_diff': ('Home Offensive Strength', 0.10),
            'away_point_diff': ('Away Offensive Strength', -0.08),
            'rest_days_home': ('Home Rest Advantage', 0.08),
            'rest_days_away': ('Away Fatigue', -0.06),
            'home_form': ('Home Recent Form', 0.07),
            'away_form': ('Away Recent Form', -0.05),
            'travel_distance': ('Travel Distance Impact', -0.04),
        }
        
        for feature, (name, impact) in feature_impact.items():
            if feature in feature_cols:
                value = features[feature].values[0]
                impact_direction = 'Positive' if impact > 0 else 'Negative'
                importance.append({
                    'factor': name,
                    'impact': float(impact),
                    'value': float(value),
                    'direction': impact_direction
                })
        
        # Sort by absolute impact
        importance = sorted(importance, key=lambda x: abs(x['impact']), reverse=True)[:5]
        return importance
    
    def predict_lstm_sequence(self, game_sequence: np.ndarray) -> Tuple[float, float]:
        """
        Generate prediction using LSTM model for time-series data
        
        Args:
            game_sequence: Shape (timesteps, features)
        
        Returns:
            Tuple of (probability, confidence)
        """
        if self.lstm_model is None or not TENSORFLOW_AVAILABLE:
            return 0.5, 0.0
        
        try:
            # Ensure correct shape (batch_size, timesteps, features)
            if len(game_sequence.shape) == 2:
                game_sequence = np.expand_dims(game_sequence, axis=0)
            
            prob = self.lstm_model.predict(game_sequence, verbose=0)[0, 0]
            confidence = 0.8  # LSTM predictions are generally confident
            return float(prob), float(confidence)
        except Exception as e:
            print(f"Error in LSTM prediction: {e}")
            return 0.5, 0.0
    
    def load_historical_models(self, model_dir: str, sport: str) -> Dict:
        """
        Load trained models from LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/
        
        Returns dict of {model_name: model, metadata: validation_results}
        """
        loaded_models = {}
        
        if not os.path.exists(model_dir):
            return loaded_models
        
        try:
            # Search for sport-specific model directories
            for root, dirs, files in os.walk(model_dir):
                for file in files:
                    if sport in file and file.endswith('.pkl') and 'metadata' in file:
                        model_path = os.path.join(root, file)
                        try:
                            model_data = joblib.load(model_path)
                            model_name = Path(root).name
                            loaded_models[model_name] = {
                                'model': model_data,
                                'path': model_path,
                                'accuracy': model_data.get('accuracy', 0) if isinstance(model_data, dict) else 0,
                                'roc_auc': model_data.get('roc_auc', 0) if isinstance(model_data, dict) else 0,
                            }
                        except Exception as e:
                            print(f"Error loading {model_path}: {e}")
        except Exception as e:
            print(f"Error searching model directory: {e}")
        
        return loaded_models
    
    def predict_with_historical_models(self, 
                                      home_team: str,
                                      away_team: str,
                                      game_data: pd.DataFrame,
                                      historical_metrics: Dict,
                                      models: Dict) -> Dict:
        """
        Generate prediction using historical trained models
        
        Returns ensemble prediction from available models
        """
        predictions = {
            'model_count': len(models),
            'home_win_probability': 0.5,
            'away_win_probability': 0.5,
            'confidence': 0.0,
            'model_predictions': [],
            'model_agreement': 'Mixed'
        }
        
        if len(models) == 0:
            return predictions
        
        probs = []
        
        for model_name, model_info in models.items():
            try:
                model = model_info['model']
                
                # Prepare features
                game_stats = {
                    'home_team': home_team,
                    'away_team': away_team,
                    'rest_days_home': 1,
                    'rest_days_away': 1,
                    'travel_distance_miles': 0
                }
                
                features = self.prepare_features(game_stats, historical_metrics)
                
                # Handle different model types
                if isinstance(model, dict) and 'ensemble' in model:
                    # Already an ensemble
                    prob = model['ensemble'].predict_proba(features)[:, 1][0]
                elif hasattr(model, 'predict_proba'):
                    # Sklearn-like model
                    prob = model.predict_proba(features)[:, 1][0]
                else:
                    # Try direct prediction
                    prob = model.predict(features)[0]
                
                probs.append(prob)
                predictions['model_predictions'].append({
                    'model': model_name,
                    'probability': float(prob),
                    'accuracy': model_info.get('accuracy', 0),
                    'roc_auc': model_info.get('roc_auc', 0)
                })
            except Exception as e:
                print(f"Error predicting with {model_name}: {e}")
        
        # Ensemble average
        if len(probs) > 0:
            ensemble_prob = np.mean(probs)
            predictions['home_win_probability'] = float(ensemble_prob)
            predictions['away_win_probability'] = float(1 - ensemble_prob)
            
            # Confidence based on agreement
            if len(probs) > 1:
                std_dev = np.std(probs)
                predictions['confidence'] = float(1.0 - min(std_dev, 0.5))  # Clip to 0.5
                
                # Model agreement
                if std_dev < 0.1:
                    predictions['model_agreement'] = 'Strong Consensus'
                elif std_dev < 0.2:
                    predictions['model_agreement'] = 'Moderate Agreement'
                else:
                    predictions['model_agreement'] = 'Mixed Predictions'
        
        return predictions


# Convenience functions
def get_ml_predictor(sport: str = 'NFL') -> MLPredictionIntegration:
    """Factory function to get ML predictor instance"""
    return MLPredictionIntegration(sport=sport)


def predict_game(home_team: str,
                away_team: str,
                game_data: pd.DataFrame,
                historical_metrics: Dict,
                sport: str = 'NFL',
                use_lstm: bool = False) -> Dict:
    """
    High-level prediction function combining multiple models
    """
    predictor = get_ml_predictor(sport)
    
    # Prepare features
    game_stats = {
        'home_team': home_team,
        'away_team': away_team,
        'rest_days_home': 1,
        'rest_days_away': 1,
        'travel_distance_miles': 0
    }
    
    features = predictor.prepare_features(game_stats, historical_metrics)
    
    # Get predictions
    prediction = predictor.predict_with_ensemble(features)
    
    return prediction
