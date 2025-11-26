# Sports-Project Quick Reference Guide

## 📍 Key File Locations

### **Active Python Source Code** (Latest Versions)
```
.history/Sports-Project-main/src/
├── api_client_20251114092557.py ⭐ API client for live data
├── prediction_20251121141743.py ⭐ Main prediction engine
└── [4 older versions of each]
```

### **Model Directories**
```
LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/
├── NHL_MODELS/       (5 base models + ensemble)
├── NBA_MODELS/       (5 base models + ensemble)
├── NFL_MODELS/       (5 base models + ensemble)
├── MLB_MODELS/       (5 base models + ensemble)
├── SPREAD_MODELS/    (12 unified spread models: 3 per sport)
├── WINNER_MODELS/    (6 NFL winner classification models)
└── FINAL_SUPER_ENRICHED_FIXED/
    ├── [4 enriched feature CSVs]
    ├── models/                 (8 multi-sport models)
    ├── feature_ready/          (v1, v2, v3 model versions + validation)
    └── feature_ready_leakfree/ (data-leakage-free models)
```

### **Data Files**
```
Root:
├── mlb_games.csv                    (MLB raw data)
├── nfl_games.csv                    (NFL raw data)
├── nhl_*.csv                        (NHL variants with/without features)
└── datasets/
    ├── MLB_leagues.csv
    ├── NBA_leagues.csv
    ├── NFL_leagues.csv
    └── NHL_leagues.csv

NHL_Dataset/ (13 CSV files: detailed play-by-play data)

LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/
├── FINAL_SUPER_ENRICHED_FIXED/
│   ├── *_SUPER_FINAL_FIXED.csv      (Enriched features)
│   ├── feature_ready/
│   │   ├── *_FEATURE_READY.csv
│   │   └── validation_reports/      (Holdout test results)
│   └── feature_ready_leakfree/
│       └── *_SAFE.csv               (No-leakage versions)
├── LL9_5_SHAP/                      (16 SHAP importance files)
└── *_bayesian_results.csv           (4 files: hyperparameter tuning)
```

## 🎯 Important Files by Purpose

### **To Fetch Live Game Data**
→ `.history/Sports-Project-main/src/api_client_20251114092557.py`
- Class: `APIFootballClient`
- Method: `fetch_games()` (async)
- Supports: NFL, NBA, MLB, NHL

### **To Make Predictions**
→ `.history/Sports-Project-main/src/prediction_20251121141743.py`
- Class: `PredictionService`
- Methods:
  - `load_models()` - Load all models
  - `calculate_over_under_prediction()`
  - `calculate_spread_prediction()`
  - `calculate_winner_prediction()`
  - `calculate_shap_values()` - Feature importance

### **To Understand Model Performance**
→ `ALL_FINAL_AUC_RESULTS.csv` - Final scores
→ `feature_ready/validation_reports/*.csv` - Holdout results
→ `*_bayesian_results.csv` - Hyperparameter tuning

### **To See Feature Importance**
→ `LL9_5_SHAP/` directory
- `ALL_SPORTS_TOP10_SHAP_FEATURES.csv` - Top features across all sports
- `{SPORT}_SHAP_feature_ranking.csv` - Per-sport rankings
- `{SPORT}_{MODEL}_SHAP_feature_ranking.csv` - Per-model rankings

### **To Use the Safest Models** (No Data Leakage)
→ `feature_ready_leakfree/models_leakfree/`
- Files: `*_XGB.pkl`, `*_RF.pkl`, `*_scaler.pkl`, `*_features.pkl`

### **For Production/Real Predictions**
→ `feature_ready/real_models_final/`
- Files: `*_REAL.pkl` (production models) + `*_scaler.pkl`

## 📊 Model Types & Locations

| Type | Location | Count | Files per Sport |
|------|----------|-------|-----------------|
| **Over/Under** | `{SPORT}_MODELS/` | 5 per sport | xgb, lgbm, rf, meta, calibrator |
| **Spread** | `SPREAD_MODELS/` | 3 per sport | xgb, rf, lgbm |
| **Winner** | `WINNER_MODELS/` | 6 (NFL only) | xgb, lgbm, rf + calibrators |
| **Feature-Ready v1** | `feature_ready/trained_models/` | 4 total | Mixed models |
| **Feature-Ready v2** | `feature_ready/trained_models_v2/` | 8 total | 4 models + scalers |
| **Feature-Ready v3** | `feature_ready/trained_models_v3/` | 12 total | Standardized XGB/RF + scalers |
| **Production** | `feature_ready/real_models_final/` | 8 total | 4 models + scalers |
| **Leak-Free** | `feature_ready_leakfree/models_leakfree/` | 12 total | XGB/RF + scalers + features |

## 🗂️ File Naming Conventions

```
{SPORT}_{MODEL_TYPE}.pkl
  - SPORT: NFL, NBA, MLB, NHL (uppercase)
  - MODEL_TYPE: xgb, lgbm (lightgbm), rf (random_forest)

{SPORT}_spread_{MODEL}.pkl
  - For unified spread regression models

{SPORT}_{PREDICTION_TYPE}_{MODEL}.pkl
  - PREDICTION_TYPE: winner (classification), over_under (classification)

*_SUPER_FINAL_FIXED.csv
  - Indicates enriched, domain-aware features (training ready)

*_FEATURE_READY.csv
  - Processed & normalized for model input

*_SAFE.csv
  - No data leakage variants

*_SHAP_feature_ranking.csv
  - SHAP-based feature importance rankings
```

## 🔑 Model Performance (AUC Scores)

| Sport | AUC Score | Notes |
|-------|-----------|-------|
| **NBA** | 0.884 | Best performer |
| **NFL** | 0.654 | Heavy OVER imbalance |
| **NHL** | 0.637 | Balanced class distribution |
| **MLB** | 0.623 | Heavy OVER imbalance |

⚠️ **Known Issues**:
- NBA: 100% UNDER (0% OVER) - possible weighting needed
- NFL/MLB: Over-heavy class imbalance
- NHL: Balanced (54.5% OVER, 45.5% UNDER)

## 🔧 Dependencies & Versions

```
Python ML Stack:
- scikit-learn==1.2.2
- xgboost==3.1.1
- lightgbm==4.6.0
- numpy==2.3.4 (with SHAP 2.0 compatibility patch)
- pandas==2.3.3

Explainability:
- shap==0.42.1

API & Async:
- aiohttp==3.9.5 (async HTTP requests)
- requests==2.32.5 (fallback sync requests)

GUI:
- PyQt6==6.10.0
- qasync==0.28.0 (async PyQt6 support)

Utilities:
- joblib==1.5.2 (model serialization)
- python-dotenv==1.2.1 (environment variables)
- matplotlib==3.10.7 (plotting)
```

## 🚀 Common Usage Patterns

### **Initialize API Client**
```python
from src.api_client import APIFootballClient

client = APIFootballClient(api_key="YOUR_KEY", sport="NFL")
games = client.fetch_games()
```

### **Load Models & Predict**
```python
from src.prediction import PredictionService

service = PredictionService()
service.load_models()

ou_pred = service.calculate_over_under_prediction(game_data)
spread_pred = service.calculate_spread_prediction(game_data)
winner_pred = service.calculate_winner_prediction(game_data)
```

### **Get SHAP Explanations**
```python
shap_values = service.calculate_shap_values(game_data, sport="NFL")
```

## 📁 Supporting Files to Locate

These are **imported by the main scripts but need verification**:

- `simulation.py` - Contains `OverUnderSimulator` class (Monte Carlo blending)
- `sport_config.py` - Contains `TimeParser` and `get_sport_config()` (time-aware logic)
- `data_storage.py` - Database operations for prediction storage
- `.env` file - API keys, configuration (see `.history/` for versions)

## 🎓 Architecture Overview

```
API Data (APIFootballClient)
        ↓
   Game Features
        ↓
Bayesian Ensemble (Base Models)
        ↓
   Probability Calibration
        ↓
Over/Under, Spread, Winner Predictions
        ↓
   SHAP Explainability (Feature Importance)
        ↓
   Monte Carlo Simulation (Score Projection)
        ↓
   Output: Confidence-Adjusted Predictions
```

## 🔍 Data Quality Summary

- **Total Games Analyzed**: 52,420 (all 4 sports)
- **Time Period**: 2015-2025
- **NHL Duplicates**: 1 in raw, 4 in MLB (cleaned in feature prep)
- **Missing Values**: See `DATA_ANALYSIS_REPORT.txt`
- **Feature Engineering**: Domain-aware, no temporal leakage

---

**Last Updated**: November 26, 2025
