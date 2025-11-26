"""
TRAIN ALL 4 SPORTS LEAGUES
NHL, NFL, NBA, MLB - Complete model training
"""
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from src.unified_training_pipeline import UnifiedTrainingPipeline

def train_sport(sport_name, data_dir, models_dir):
    """Train models for a specific sport"""
    print("\n" + "=" * 80)
    print(f"TRAINING {sport_name} MODELS")
    print("=" * 80)
    
    try:
        start_time = time.time()
        
        pipeline = UnifiedTrainingPipeline(
            sport=sport_name,
            data_dir=data_dir,
            models_dir=models_dir,
            test_mode=False  # Full dataset
        )
        
        results = pipeline.run_full_pipeline(
            val_size=0.2,
            save_models=True
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n{sport_name} Training Complete:")
        print(f"  Accuracy:  {results['accuracy']:.1%}")
        print(f"  ROC-AUC:   {results['roc_auc']:.3f}")
        print(f"  Duration:  {elapsed:.1f}s")
        print(f"  Saved to:  {results.get('model_path', 'N/A')}")
        
        return True, results
        
    except FileNotFoundError as e:
        print(f"\n⚠️ {sport_name} data not found: {e}")
        print(f"   Skipping {sport_name}...")
        return False, None
    except Exception as e:
        print(f"\n❌ Error training {sport_name}: {e}")
        return False, None

def main():
    print("=" * 80)
    print("MULTI-SPORT MODEL TRAINING")
    print("=" * 80)
    print("\nTraining models for: NHL, NFL, NBA, MLB")
    print("Target: 55%+ accuracy for each sport\n")
    
    data_dir = Path('.')
    models_dir = Path('LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP')
    
    sports = ['NHL', 'NFL', 'NBA', 'MLB']
    results_summary = {}
    
    overall_start = time.time()
    
    for sport in sports:
        success, results = train_sport(sport, data_dir, models_dir)
        results_summary[sport] = {
            'success': success,
            'results': results
        }
    
    overall_elapsed = time.time() - overall_start
    
    # Print final summary
    print("\n\n" + "=" * 80)
    print("TRAINING COMPLETE - SUMMARY")
    print("=" * 80)
    print(f"Total Duration: {overall_elapsed:.1f} seconds ({overall_elapsed/60:.1f} minutes)")
    print()
    
    for sport, data in results_summary.items():
        if data['success']:
            res = data['results']
            status = "✅ SUCCESS" if res['accuracy'] >= 0.55 else "⚠️ BELOW TARGET"
            print(f"{sport:5s} - {status}")
            print(f"        Accuracy: {res['accuracy']:.1%} | ROC-AUC: {res['roc_auc']:.3f}")
        else:
            print(f"{sport:5s} - ❌ FAILED (data not available)")
    
    print("=" * 80)
    
    # Count successes
    successful = sum(1 for d in results_summary.values() if d['success'])
    print(f"\nTrained {successful}/{len(sports)} sports successfully")

if __name__ == "__main__":
    main()
