"""
Train Individual Sport - Quick Training Script
Trains a single sport model with the fixed pipeline
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.unified_training_pipeline import UnifiedTrainingPipeline

def train_sport(sport: str):
    """Train a single sport"""
    print("="*80)
    print(f"TRAINING {sport} MODEL")
    print("="*80)
    
    pipeline = UnifiedTrainingPipeline(
        sport=sport,
        data_dir='.',
        models_dir='LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP',
        test_mode=False
    )
    
    try:
        results = pipeline.run_full_pipeline(val_size=0.2, save_models=True)
        
        print(f"\n{sport} Training Complete:")
        print(f"  Accuracy:  {results['accuracy']:.1%}")
        print(f"  ROC-AUC:   {results['roc_auc']:.3f}")
        print(f"  Duration:  {results.get('duration', 0):.1f}s")
        print(f"  Saved to:  {results.get('model_dir', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error training {sport}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sport = sys.argv[1].upper()
    else:
        sport = 'NFL'  # Default
    
    success = train_sport(sport)
    sys.exit(0 if success else 1)
