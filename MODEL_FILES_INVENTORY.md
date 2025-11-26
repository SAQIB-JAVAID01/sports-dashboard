# Complete Model Files Inventory (.pkl)

**Total Models**: 111 pickle files  
**Generated**: November 26, 2025

---

## 📦 MODEL HIERARCHY

### **Level 1: Over/Under Ensemble Models** (20 files)
Bayesian ensemble for over/under predictions per sport.

#### **NFL_MODELS/** (5 files)
```
NFL_MODELS/
├── xgboost.pkl                    (XGBoost base learner)
├── lightgbm.pkl                   (LightGBM base learner)
├── random_forest.pkl              (Random Forest base learner)
├── meta_logistic.pkl              (Meta-learner - combines base models)
└── calibrator.pkl                 (Probability calibration)
```

#### **NBA_MODELS/** (5 files)
```
NBA_MODELS/
├── xgboost.pkl
├── lightgbm.pkl
├── random_forest.pkl
├── meta_logistic.pkl
└── calibrator.pkl
```

#### **MLB_MODELS/** (5 files)
```
MLB_MODELS/
├── xgboost.pkl
├── lightgbm.pkl
├── random_forest.pkl
├── meta_logistic.pkl
└── calibrator.pkl
```

#### **NHL_MODELS/** (5 files)
```
NHL_MODELS/
├── xgboost.pkl
├── lightgbm.pkl
├── random_forest.pkl
├── meta_logistic.pkl
└── calibrator.pkl
```

---

### **Level 2: Unified Spread Models** (12 files)
Regression models for predicting betting spread (margin of victory).

#### **SPREAD_MODELS/** (12 files)
```
SPREAD_MODELS/
├── [NFL] (3 files)
│   ├── NFL_spread_xgb.pkl
│   ├── NFL_spread_rf.pkl
│   └── NFL_spread_lgb.pkl
├── [NBA] (3 files)
│   ├── NBA_spread_xgb.pkl
│   ├── NBA_spread_rf.pkl
│   └── NBA_spread_lgb.pkl
├── [MLB] (3 files)
│   ├── MLB_spread_xgb.pkl
│   ├── MLB_spread_rf.pkl
│   └── MLB_spread_lgb.pkl
└── [NHL] (3 files)
    ├── NHL_spread_xgb.pkl
    ├── NHL_spread_rf.pkl
    └── NHL_spread_lgb.pkl
```

---

### **Level 3: Winner Classification Models** (6 files)
Classification models for predicting game winners.

#### **WINNER_MODELS/** (6 files)
NFL-specific models only:
```
WINNER_MODELS/
├── [NFL Classifiers] (3 files)
│   ├── NFL_winner_xgb.pkl
│   ├── NFL_winner_lgb.pkl
│   └── NFL_winner_rf.pkl
└── [NFL Probability Calibrators] (3 files)
    ├── NFL_winner_xgb_calibrator.pkl
    ├── NFL_winner_lgb_calibrator.pkl
    └── NFL_winner_calibrator.pkl
```

---

### **Level 4: Feature-Ready Models (v1)** (4 files)
Initial trained models on enriched features.

#### **feature_ready/trained_models/** (4 files)
```
trained_models/
├── american_football_XGBoost_model.pkl    (NFL XGBoost)
├── ice_hockey_XGBoost_model.pkl           (NHL XGBoost)
├── basketball_XGBoost_model.pkl           (NBA XGBoost)
└── baseball_RandomForest_model.pkl        (MLB Random Forest)
```

---

### **Level 5: Feature-Ready Models (v2)** (8 files)
Improved version with proper feature scaling.

#### **feature_ready/trained_models_v2/** (8 files)
```
trained_models_v2/
├── [NFL] (2 files)
│   ├── american_football_XGBoost_model.pkl
│   └── american_football_scaler.pkl
├── [NHL] (2 files)
│   ├── ice_hockey_RandomForest_model.pkl
│   └── ice_hockey_scaler.pkl
├── [NBA] (2 files)
│   ├── basketball_RandomForest_model.pkl
│   └── basketball_scaler.pkl
└── [MLB] (2 files)
    ├── baseball_XGBoost_model.pkl
    └── baseball_scaler.pkl
```

---

### **Level 6: Feature-Ready Models (v3)** (12 files)
Latest standardized version with XGB & RF variants.

#### **feature_ready/trained_models_v3/** (12 files)
```
trained_models_v3/
├── [NFL] (3 files)
│   ├── american_football_XGB_model.pkl
│   ├── american_football_XGBoost_model.pkl
│   └── american_football_scaler.pkl
├── [MLB] (3 files)
│   ├── baseball_XGB_model.pkl
│   ├── baseball_XGBoost_model.pkl
│   └── baseball_scaler.pkl
├── [NBA] (3 files)
│   ├── basketball_RF_model.pkl
│   ├── basketball_RandomForest_model.pkl
│   └── basketball_scaler.pkl
└── [NHL] (3 files)
    ├── ice_hockey_RF_model.pkl
    ├── ice_hockey_RandomForest_model.pkl
    └── ice_hockey_scaler.pkl
```

---

### **Level 7: Production Models** (8 files)
Final production-ready models for real predictions.

#### **feature_ready/real_models_final/** (8 files)
```
real_models_final/
├── [NFL] (2 files)
│   ├── american_football_REAL.pkl
│   └── american_football_scaler.pkl
├── [MLB] (2 files)
│   ├── baseball_REAL.pkl
│   └── baseball_scaler.pkl
├── [NBA] (2 files)
│   ├── basketball_REAL.pkl
│   └── basketball_scaler.pkl
└── [NHL] (2 files)
    ├── ice_hockey_REAL.pkl
    └── ice_hockey_scaler.pkl
```

---

### **Level 8: Data-Leakage-Free Models** (12 files)
Certified models without temporal or data leakage for safe predictions.

#### **feature_ready_leakfree/models_leakfree/** (12 files)
```
models_leakfree/
├── [NFL] (3 files)
│   ├── american_football_XGB.pkl
│   ├── american_football_scaler.pkl
│   └── american_football_features.pkl
├── [MLB] (3 files)
│   ├── baseball_RF.pkl
│   ├── baseball_scaler.pkl
│   └── baseball_features.pkl
├── [NBA] (3 files)
│   ├── basketball_XGB.pkl
│   ├── basketball_scaler.pkl
│   └── basketball_features.pkl
└── [NHL] (3 files)
    ├── ice_hockey_XGB.pkl
    ├── ice_hockey_scaler.pkl
    └── ice_hockey_features.pkl
```

---

### **Level 9: Multi-Sport Models** (8 files)
Models trained on unified features across sports.

#### **models/** (8 files)
```
models/
├── [XGBoost Models] (4 files)
│   ├── xgb_american_football.pkl
│   ├── xgb_basketball.pkl
│   ├── xgb_baseball.pkl
│   └── xgb_ice_hockey.pkl
└── [Random Forest Models] (4 files)
    ├── rf_american_football.pkl
    ├── rf_basketball.pkl
    ├── rf_baseball.pkl
    └── rf_ice_hockey.pkl
```

---

### **Level 10: Legacy NHL Models** (9 files)
Historical NHL-specific models from earlier experiments.

#### **Others/** (9 files)
```
Others/
├── [Prediction Models] (4 files)
│   ├── nhl_prediction_model.pkl
│   ├── nhl_model.pkl
│   ├── nhl_model_final.pkl
│   └── nhl_model_robust.pkl
├── [Feature Extractors] (2 files)
│   ├── nhl_features.pkl
│   └── nhl_features_final.pkl
└── [Scalers] (3 files)
    ├── nhl_scaler.pkl
    ├── nhl_scaler_final.pkl
    └── nhl_scaler_robust.pkl
```

---

## 🎯 USAGE BY SCENARIO

### **Scenario 1: Quick Production Prediction**
Use **Level 7 (real_models_final/)**
- Files needed: `{SPORT}_REAL.pkl` + `{SPORT}_scaler.pkl`
- Fastest, pre-optimized, proven performance

### **Scenario 2: Safe Prediction (No Leakage)**
Use **Level 8 (models_leakfree/)**
- Files needed: `{SPORT}_*.pkl` (XGB or RF) + scaler + features
- Best for research/validation
- Certified data-leakage-free

### **Scenario 3: Over/Under Probability**
Use **Level 1 ({SPORT}_MODELS/)**
- Files needed: All 5 files per sport
- Provides Bayesian ensemble with calibration
- Most sophisticated approach

### **Scenario 4: Spread Prediction**
Use **Level 2 (SPREAD_MODELS/)**
- Files needed: Pick one model per sport (xgb/rf/lgb)
- Regression for margin of victory
- Can combine multiple models for ensemble

### **Scenario 5: Winner Prediction (NFL Only)**
Use **Level 3 (WINNER_MODELS/)**
- Files needed: NFL winner classifiers + calibrators
- Classification approach for game winners
- NFL-specific only

### **Scenario 6: Unified Multi-Sport**
Use **Level 9 (models/)**
- Files needed: XGB or RF models (uniform architecture)
- Single model type across all sports
- Good for simplified systems

### **Scenario 7: Latest Research/Development**
Use **Level 6 (trained_models_v3/)**
- Files needed: v3 models + scalers
- Most recent standardized versions
- Good for new feature experimentation

---

## 📊 MODEL FILE STATISTICS

| Level | Name | Files | Purpose | Status |
|-------|------|-------|---------|--------|
| 1 | O/U Ensemble | 20 | Classification (OVER/UNDER) | ✅ Active |
| 2 | Spread Unified | 12 | Regression (Margin) | ✅ Active |
| 3 | Winner NFL | 6 | Classification (Winner) | ✅ Active (NFL only) |
| 4 | Feature-Ready v1 | 4 | Baseline models | ⚠️ Legacy |
| 5 | Feature-Ready v2 | 8 | Improved models | ⚠️ Legacy |
| 6 | Feature-Ready v3 | 12 | Latest research | ✅ Active |
| 7 | Production | 8 | Real deployment | ✅ Production |
| 8 | Leak-Free | 12 | Validation safe | ✅ Active |
| 9 | Multi-Sport | 8 | Unified approach | ⚠️ Research |
| 10 | NHL Legacy | 9 | Historical | 🗂️ Archive |
| **TOTAL** | | **111** | | |

---

## 🔗 MODEL DEPENDENCIES

### **Scaler Files** (Required for use)
- **Location**: Same directory as models
- **Naming**: `{SPORT}_scaler.pkl`
- **Purpose**: Inverse transformation for prediction
- **Usage**: Load scaler with model

### **Feature Specification Files**
- **Location**: `models_leakfree/`
- **Naming**: `{SPORT}_features.pkl`
- **Purpose**: Feature names and order
- **Usage**: Ensure input data matches expected features

### **Ensemble Metadata**
- **Location**: `{SPORT}_MODELS/`
- **File**: `ensemble_metadata.json` (4 files total)
- **Purpose**: Ensemble configuration & weights
- **Sports**: NFL, NBA, MLB, NHL

---

## 🎯 MODEL SELECTION FLOWCHART

```
Need to make a prediction?
│
├─→ NFL Winner? ──→ Use WINNER_MODELS/ (6 files)
│
├─→ Any sport, margin of victory? ──→ Use SPREAD_MODELS/ (12 files)
│
├─→ Any sport, Over/Under probability?
│   ├─→ High accuracy needed? ──→ Use Level 1: {SPORT}_MODELS/ (20 files, Bayesian)
│   ├─→ Production deployment? ──→ Use Level 7: real_models_final/ (8 files)
│   └─→ Research/validation? ──→ Use Level 8: models_leakfree/ (12 files)
│
└─→ Single model per sport? ──→ Use Level 9: models/ (8 files, XGB/RF)
```

---

## ⚠️ IMPORTANT NOTES

1. **Always load scalers** with their corresponding models
2. **Data leakage check**: Use `models_leakfree/` for validation
3. **Probability calibration**: Level 1 models include calibrators
4. **Feature order matters**: Use `{SPORT}_features.pkl` for correct column ordering
5. **Sport consistency**: Use same sport models for same sport data
6. **Version alignment**: Don't mix models from different levels (e.g., v2 model with v3 scaler)

---

**Last Updated**: November 26, 2025
