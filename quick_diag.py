"""Quick diagnostic - check actual training"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from src.unified_training_pipeline import UnifiedTrainingPipeline

pipeline = UnifiedTrainingPipeline('NHL', Path('.'), Path('LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP'), test_mode=True)
pipeline.load_data()
pipeline.engineer_features()
pipeline.preprocess_data()
pipeline.prepare_train_val_split()

print(f"\nFeatures: {len(pipeline.feature_names)}")
print(f"First 10: {pipeline.feature_names[:10]}")

print(f"\nTrain: {len(pipeline.X_train)} samples")
print(f"Val: {len(pipeline.X_val)} samples")

# Check a sample
print(f"\nFirst training sample:")
print(pipeline.X_train.iloc[0][:5])
print(f"Target: {pipeline.y_train.iloc[0]}")

# Check variance
print(f"\nFeature variance in training set:")
for col in pipeline.feature_names[:5]:
    var = pipeline.X_train[col].var()
    print(f"  {col}: {var:.4f}")

# Quick model test
from xgboost import XGBClassifier
model = XGBClassifier(n_estimators=10, max_depth=3, random_state=42)
model.fit(pipeline.X_train, pipeline.y_train)

train_pred = model.predict(pipeline.X_train)
val_pred = model.predict(pipeline.X_val)

train_acc = (train_pred == pipeline.y_train).mean()
val_acc = (val_pred == pipeline.y_val).mean()

print(f"\nQuick XGBoost test:")
print(f"Train accuracy: {train_acc:.1%}")
print(f"Val accuracy: {val_acc:.1%}")

# Feature importance
importances = model.feature_importances_
top_features = sorted(zip(pipeline.feature_names, importances), key=lambda x: x[1], reverse=True)[:5]
print(f"\nTop 5 features:")
for feat, imp in top_features:
    print(f"  {feat}: {imp:.4f}")
