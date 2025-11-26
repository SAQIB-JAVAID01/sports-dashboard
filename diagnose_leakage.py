"""Diagnose data leakage - check if target is in features"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from src.unified_training_pipeline import UnifiedTrainingPipeline

def main():
    print("=" * 70)
    print("DATA LEAKAGE DIAGNOSTIC")
    print("=" * 70)
    print()
    
    # Initialize pipeline
    pipeline = UnifiedTrainingPipeline(
        sport='NHL',
        data_dir=Path('.'),
        models_dir=Path('LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP'),
        test_mode=True
    )
    
    # Load and engineer features
    pipeline.load_data()
    pipeline.engineer_features()
    pipeline.preprocess_data()
    
    # Check feature names
    print("Feature columns:")
    print("-" * 70)
    for i, feat in enumerate(pipeline.feature_names, 1):
        print(f"{i:3d}. {feat}")
    
    print()
    print(f"Total features: {len(pipeline.feature_names)}")
    
    # Check if target is in features
    if 'team_won' in pipeline.feature_names:
        print("\n⚠️  CRITICAL: 'team_won' found in features! DATA LEAKAGE!")
    else:
        print("\n✓ 'team_won' not in features")
    
    # Check if any feature correlates perfectly with target
    pipeline.prepare_train_val_split()
    
    print("\n" + "=" * 70)
    print("CORRELATION WITH TARGET")
    print("=" * 70)
    
    # Calculate correlations
    X_combined = pd.concat([pipeline.X_train, pipeline.X_val])
    y_combined = pd.concat([pipeline.y_train, pipeline.y_val])
    
    correlations = {}
    for col in pipeline.feature_names:
        corr = X_combined[col].corr(y_combined)
        if abs(corr) > 0.95:  # Very high correlation
            correlations[col] = corr
    
    if correlations:
        print("\n⚠️  Features with >95% correlation to target:")
        for feat, corr in sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True):
            print(f"  {feat}: {corr:.4f}")
    else:
        print("\n✓ No features with >95% correlation to target")
    
    # Check first few rows
    print("\n" + "=" * 70)
    print("SAMPLE DATA (First 5 training samples)")
    print("=" * 70)
    sample_df = pd.concat([
        pipeline.X_train.head(),
        pipeline.y_train.head().rename('team_won')
    ], axis=1)
    
    print(sample_df[['win_rate_L5', 'pts_scored_L5', 'team_won']].to_string())

if __name__ == "__main__":
    main()
