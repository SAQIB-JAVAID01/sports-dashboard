"""
Demo: NHL Prediction Using Trained Model
Demonstrates loading models and making predictions
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

# Find latest NHL model
models_dir = Path("LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP")
nhl_dirs = [d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith('NHL_') and (d / 'catboost.pkl').exists()]

if not nhl_dirs:
    print("❌ No NHL models found!")
    print(f"   Searched in: {models_dir.absolute()}")
    print(f"   Directories found: {[d.name for d in models_dir.iterdir() if d.is_dir()]}")
    exit(1)

latest_model_dir = sorted(nhl_dirs)[-1]
print("="*80)
print("NHL PREDICTION DEMO - Using Trained Model")
print("="*80)
print(f"\nLoading model from: {latest_model_dir.name}\n")

# Load models
try:
    catboost_model = joblib.load(latest_model_dir / "catboost.pkl")
    lightgbm_model = joblib.load(latest_model_dir / "lightgbm.pkl")
    metadata = joblib.load(latest_model_dir / "metadata.pkl")
    
    print("✅ Models loaded successfully!")
    print(f"   Features: {len(metadata['feature_names'])} features")
    print(f"   Training Accuracy: {metadata['validation_results']['accuracy']:.1%}")
    print(f"   ROC-AUC: {metadata['validation_results']['roc_auc']:.3f}")
    print(f"   Ensemble Weights: CatBoost {metadata['ensemble_weights']['catboost']:.0%}, LightGBM {metadata['ensemble_weights']['lightgbm']:.0%}")
    
except Exception as e:
    print(f"❌ Error loading models: {e}")
    exit(1)

# Load validation data for demo
print("\n" + "="*80)
print("LOADING RECENT NHL GAMES FOR DEMO")
print("="*80)

try:
    from src.data_loaders import MultiSportDataLoader
    from src.advanced_feature_engineering import AdvancedSportsFeatureEngineer
    
    loader = MultiSportDataLoader()
    df = loader.load_sport_data('NHL', 'nhl_finished_games.csv')
    
    # Engineer features
    engineer = AdvancedSportsFeatureEngineer(sport='NHL')
    features_df, feature_names = engineer.transform(df)
    features_df = features_df.dropna()
    
    # Get last 10 games
    recent_games = features_df.tail(10).copy()
    
    print(f"\n✅ Loaded {len(recent_games)} recent games for demo\n")
    
    # Prepare features
    X = recent_games[metadata['feature_names']]
    y_true = recent_games['team_won'].values
    
    # Make predictions
    print("="*80)
    print("MAKING PREDICTIONS")
    print("="*80 + "\n")
    
    # CatBoost predictions
    catboost_probs = catboost_model.predict_proba(X)[:, 1]
    
    # LightGBM predictions
    lightgbm_probs = lightgbm_model.predict_proba(X)[:, 1]
    
    # Ensemble predictions
    ensemble_probs = (
        metadata['ensemble_weights']['catboost'] * catboost_probs +
        metadata['ensemble_weights']['lightgbm'] * lightgbm_probs
    )
    
    # Display predictions
    print(f"{'Game':<6} {'Date':<12} {'Team':<6} {'Opponent':<6} {'Home':<6} {'Predicted':<12} {'Actual':<8} {'Result':<8}")
    print("-"*80)
    
    for idx, (i, row) in enumerate(recent_games.iterrows()):
        game_date = pd.to_datetime(row['game_date']).strftime('%Y-%m-%d')
        team = row['team_id']
        opponent = row['opponent_id']
        is_home = '✓' if row['is_home'] == 1 else '✗'
        pred_prob = ensemble_probs[idx]
        pred_label = 'WIN' if pred_prob > 0.5 else 'LOSS'
        actual = 'WIN' if y_true[idx] == 1 else 'LOSS'
        correct = '✅' if pred_label == actual else '❌'
        
        print(f"{idx+1:<6} {game_date:<12} {team:<6} {opponent:<6} {is_home:<6} {pred_label} ({pred_prob:.1%})<12 {actual:<8} {correct}")
    
    # Calculate accuracy
    predictions = (ensemble_probs > 0.5).astype(int)
    accuracy = (predictions == y_true).mean()
    
    print("\n" + "="*80)
    print(f"DEMO RESULTS: {accuracy:.1%} Accuracy on {len(recent_games)} recent games")
    print("="*80)
    
    # Feature importance
    print("\n" + "="*80)
    print("TOP 10 PREDICTIVE FEATURES")
    print("="*80 + "\n")
    
    if hasattr(catboost_model, 'feature_importances_'):
        importances = catboost_model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'Feature': metadata['feature_names'],
            'Importance': importances
        }).sort_values('Importance', ascending=False).head(10)
        
        for idx, row in feature_importance_df.iterrows():
            print(f"  {row['Feature']:<30} {row['Importance']:>8.1f}")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE - NHL Model Working Successfully!")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Launch dashboard: streamlit run simple_dashboard.py --server.port 8502")
    print("  2. Train other sports: python train_all_sports.py (fix bug first)")
    print("  3. Integrate API: Add API_FOOTBALL_KEY to .env file")
    print("  4. Make predictions: Use src/prediction.py PredictionService")
    
except Exception as e:
    print(f"\n❌ Error during demo: {e}")
    import traceback
    traceback.print_exc()
