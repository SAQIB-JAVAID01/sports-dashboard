"""Quick test of the unified training pipeline"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.unified_training_pipeline import UnifiedTrainingPipeline

def main():
    print("=" * 70)
    print("TESTING UNIFIED TRAINING PIPELINE - NHL (Test Mode)")
    print("=" * 70)
    print()
    
    # Initialize pipeline in test mode (small subset)
    pipeline = UnifiedTrainingPipeline(
        sport='NHL',
        data_dir=Path('.'),  # Root directory where NHL/NFL files are
        models_dir=Path('LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP'),
        test_mode=True  # Use only 500 recent games for quick testing
    )
    
    # Run full pipeline
    results = pipeline.run_full_pipeline(save_models=False)
    
    # Print summary
    print()
    print("=" * 70)
    print("TEST COMPLETE - QUICK SUMMARY")
    print("=" * 70)
    print(f"Accuracy:  {results['accuracy']:.1%}")
    print(f"ROC-AUC:   {results['roc_auc']:.3f}")
    print(f"Kelly ROI: {results['kelly_criterion_roi']:.2f}%")
    print(f"Duration:  {results['pipeline_duration_seconds']:.1f}s")
    print("=" * 70)
    
    if results['accuracy'] >= 0.55:
        print("\n✓ SUCCESS: Accuracy >= 55% (profitable threshold)")
    else:
        print(f"\n⚠ CAUTION: Accuracy {results['accuracy']:.1%} < 55% target")
        print("   (This is test mode with limited data - full training needed)")

if __name__ == "__main__":
    main()
