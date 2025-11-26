"""
FULL MODEL TRAINING - ALL DATA
Train on complete NHL dataset (22,526 games) to achieve 55%+ accuracy
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from src.unified_training_pipeline import UnifiedTrainingPipeline

def main():
    print("=" * 80)
    print("FULL MODEL TRAINING - NHL (Complete Dataset)")
    print("=" * 80)
    print()
    print("Target: 55%+ accuracy (profitable threshold)")
    print("Dataset: 22,526 team-games (11,263 NHL games)")
    print()
    
    start_time = time.time()
    
    # Initialize pipeline with FULL data (test_mode=False)
    pipeline = UnifiedTrainingPipeline(
        sport='NHL',
        data_dir=Path('.'),
        models_dir=Path('LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP'),
        test_mode=False  # Use ALL data
    )
    
    print("Training with CatBoost, XGBoost, and LightGBM...")
    print()
    
    # Run full pipeline with all models
    results = pipeline.run_full_pipeline(
        val_size=0.2,  # 80% train, 20% validation
        save_models=True
    )
    
    elapsed = time.time() - start_time
    
    # Print detailed results
    print()
    print("=" * 80)
    print("FINAL RESULTS - FULL TRAINING")
    print("=" * 80)
    print(f"Training Duration:     {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print()
    print("Performance Metrics:")
    print(f"  Accuracy:            {results['accuracy']:.1%}")
    print(f"  Precision:           {results['precision']:.4f}")
    print(f"  Recall:              {results['recall']:.4f}")
    print(f"  F1 Score:            {results['f1_score']:.4f}")
    print(f"  ROC-AUC:             {results['roc_auc']:.4f}")
    print(f"  Log Loss:            {results['log_loss']:.4f}")
    print(f"  Brier Score:         {results['brier_score']:.4f}")
    print(f"  Calibration Error:   {results['calibration_error']:.4f}")
    print()
    print("Profitability:")
    print(f"  Kelly Criterion ROI: {results['kelly_criterion_roi']:.2f}%")
    print()
    
    if results['accuracy'] >= 0.55:
        print("SUCCESS: Target accuracy >= 55% achieved!")
        print("Model is profitable for sports betting applications.")
    else:
        print(f"CAUTION: Accuracy {results['accuracy']:.1%} is below 55% target")
        print("Consider: More features, hyperparameter tuning, or additional data")
    
    print()
    print(f"Models saved to: {results.get('model_path', 'N/A')}")
    print("=" * 80)

if __name__ == "__main__":
    main()
