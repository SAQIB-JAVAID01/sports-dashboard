# Sports-Project-main: Complete Codebase Inventory

**Generated**: November 26, 2025  
**Project**: Multi-Sport Predictive Analytics Platform (NFL, NBA, MLB, NHL)  
**Base Path**: `C:\Users\Admin\New Recordings\udemy\Data Analyst Bootcamp\Python\1-python basics\Sports-Project-mainRev8\Sports-Project-main`

---

## 📋 TABLE OF CONTENTS

1. [Python Source Files](#python-source-files)
2. [Model Files (.pkl)](#model-files-pkl)
3. [CSV Data Files](#csv-data-files)
4. [Configuration & Environment Files](#configuration--environment-files)
5. [Complete Directory Structure](#complete-directory-structure)

---

## 🐍 PYTHON SOURCE FILES

### **Active Source Files** (in `.history/Sports-Project-main/src/`)

These are the versioned source files tracked by VS Code's auto-save feature. The latest versions represent the current codebase state.

#### **1. `api_client_20251114092557.py`** ⭐ LATEST API CLIENT
- **Path**: `.history/Sports-Project-main/src/api_client_20251114092557.py`
- **Purpose**: Multi-sport API client for fetching live game data
- **Key Classes**:
  - `APIFootballClient` - Main client for api-sports.io integration
- **Features**:
  - Support for NFL, NBA, MLB, NHL
  - Async request handling (aiohttp)
  - Retry logic (3 attempts, exponential backoff)
  - Sport-specific endpoints and league IDs
  - Odds retention for betting integration
- **Size**: 707 lines
- **Previous Version**: `api_client_20251108145953.py`

#### **2. `prediction_20251121141743.py`** ⭐ LATEST PREDICTION SERVICE
- **Path**: `.history/Sports-Project-main/src/prediction_20251121141743.py`
- **Purpose**: Core prediction engine for Over/Under, Spread, and Winner predictions
- **Key Classes**:
  - `PredictionService` - Loads models and generates predictions
  - `OverUnderExplainer` - SHAP-based feature importance
- **Key Methods**:
  - `load_models()` - Load all pickled models from disk
  - `calculate_over_under_prediction()` - Bayesian ensemble + O/U classification
  - `calculate_spread_prediction()` - Regression-based spread projection
  - `calculate_winner_prediction()` - Dynamic blending for winner probability (Moneyline)
- **Features**:
  - Multi-sport handling (NFL, NBA, MLB, NHL)
  - Sport-specific score impact factors
  - NHL-specific pre-game & live models integration
  - SHAP explainability (with NumPy 2.0 compatibility patch)
  - Monte Carlo simulation support
- **Size**: 1,033 lines
- **Dependencies**: simulation.py, sport_config.py
- **Previous Versions**: 
  - `prediction_20251121124221.py`
  - `prediction_20251121123722.py`
  - `prediction_20251108171017.py`

### **Supporting Source Files** (referenced but not found in main directory)

These files are imported by the main scripts but their current versions may be in the `.history` directory or need to be created:

- **`simulation.py`** - `OverUnderSimulator` class for Monte Carlo probability blending
- **`sport_config.py`** - `TimeParser` class, `get_sport_config()` for time-aware predictions
- **`data_storage.py`** - Database operations for storing game predictions (referenced in notebooks)

---

## 🎯 MODEL FILES (.pkl)

### **Directory Structure**:
```
LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/
├── NHL_MODELS/
├── NBA_MODELS/
├── NFL_MODELS/
├── MLB_MODELS/
├── SPREAD_MODELS/
├── WINNER_MODELS/
└── FINAL_SUPER_ENRICHED_FIXED/
    ├── models/
    ├── feature_ready/
    │   ├── trained_models/
    │   ├── trained_models_v2/
    │   ├── trained_models_v3/
    │   ├── real_models_final/
    │   └── validation_reports/
    └── feature_ready_leakfree/
        └── models_leakfree/
```

### **1. Over/Under Ensemble Models** (Sport-Specific)

#### **NHL_MODELS/** (5 files)
- `xgboost.pkl` - XGBoost base learner
- `lightgbm.pkl` - LightGBM base learner
- `random_forest.pkl` - Random Forest base learner
- `meta_logistic.pkl` - Meta-learner for Bayesian ensemble
- `calibrator.pkl` - Probability calibrator

#### **NBA_MODELS/** (5 files)
- `xgboost.pkl`
- `lightgbm.pkl`
- `random_forest.pkl`
- `meta_logistic.pkl`
- `calibrator.pkl`

#### **NFL_MODELS/** (5 files)
- `xgboost.pkl`
- `lightgbm.pkl`
- `random_forest.pkl`
- `meta_logistic.pkl`
- `calibrator.pkl`

#### **MLB_MODELS/** (5 files)
- `xgboost.pkl`
- `lightgbm.pkl`
- `random_forest.pkl`
- `meta_logistic.pkl`
- `calibrator.pkl`

### **2. Spread Regression Models** (Unified across sports)

#### **SPREAD_MODELS/** (12 files)
Unified regression models for spread prediction (margin of victory):

- **NFL**:
  - `NFL_spread_xgb.pkl`
  - `NFL_spread_rf.pkl`
  - `NFL_spread_lgb.pkl`

- **NBA**:
  - `NBA_spread_xgb.pkl`
  - `NBA_spread_rf.pkl`
  - `NBA_spread_lgb.pkl`

- **MLB**:
  - `MLB_spread_xgb.pkl`
  - `MLB_spread_rf.pkl`
  - `MLB_spread_lgb.pkl`

- **NHL**:
  - `NHL_spread_xgb.pkl`
  - `NHL_spread_rf.pkl`
  - `NHL_spread_lgb.pkl`

### **3. Winner Classification Models**

#### **LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/WINNER_MODELS/** (6 files)
NFL-specific winner models:

- `NFL_winner_xgb.pkl` - XGBoost winner classifier
- `NFL_winner_lgb.pkl` - LightGBM winner classifier
- `NFL_winner_rf.pkl` - Random Forest winner classifier
- `NFL_winner_xgb_calibrator.pkl` - XGBoost probability calibrator
- `NFL_winner_lgb_calibrator.pkl` - LightGBM probability calibrator
- `NFL_winner_calibrator.pkl` - General calibrator

### **4. Feature-Ready Models** (Training & Testing)

#### **FINAL_SUPER_ENRICHED_FIXED/models/** (8 files)
Multi-sport models trained on enriched features:

- `xgb_american_football.pkl`
- `xgb_basketball.pkl`
- `xgb_baseball.pkl`
- `xgb_ice_hockey.pkl`
- `rf_american_football.pkl`
- `rf_basketball.pkl`
- `rf_baseball.pkl`
- `rf_ice_hockey.pkl`

#### **FINAL_SUPER_ENRICHED_FIXED/feature_ready/trained_models/** (4 files)
- `american_football_XGBoost_model.pkl`
- `ice_hockey_XGBoost_model.pkl`
- `basketball_XGBoost_model.pkl`
- `baseball_RandomForest_model.pkl`

#### **FINAL_SUPER_ENRICHED_FIXED/feature_ready/trained_models_v2/** (8 files)
Version 2 models with scalers:

- `american_football_XGBoost_model.pkl`
- `american_football_scaler.pkl`
- `ice_hockey_RandomForest_model.pkl`
- `ice_hockey_scaler.pkl`
- `basketball_RandomForest_model.pkl`
- `basketball_scaler.pkl`
- `baseball_XGBoost_model.pkl`
- `baseball_scaler.pkl`

#### **FINAL_SUPER_ENRICHED_FIXED/feature_ready/trained_models_v3/** (12 files)
Version 3 models with both XGB and RF variants plus scalers:

- `american_football_XGB_model.pkl`
- `american_football_XGBoost_model.pkl`
- `american_football_scaler.pkl`
- `baseball_XGB_model.pkl`
- `baseball_XGBoost_model.pkl`
- `baseball_scaler.pkl`
- `basketball_RF_model.pkl`
- `basketball_RandomForest_model.pkl`
- `basketball_scaler.pkl`
- `ice_hockey_RF_model.pkl`
- `ice_hockey_RandomForest_model.pkl`
- `ice_hockey_scaler.pkl`

#### **FINAL_SUPER_ENRICHED_FIXED/feature_ready/real_models_final/** (8 files)
Production models with scalers:

- `american_football_REAL.pkl`
- `american_football_scaler.pkl`
- `baseball_REAL.pkl`
- `baseball_scaler.pkl`
- `basketball_REAL.pkl`
- `basketball_scaler.pkl`
- `ice_hockey_REAL.pkl`
- `ice_hockey_scaler.pkl`

#### **FINAL_SUPER_ENRICHED_FIXED/feature_ready_leakfree/models_leakfree/** (12 files)
Data-leakage-free models for safe prediction:

- `american_football_XGB.pkl`
- `american_football_scaler.pkl`
- `american_football_features.pkl`
- `baseball_RF.pkl`
- `baseball_scaler.pkl`
- `baseball_features.pkl`
- `basketball_XGB.pkl`
- `basketball_scaler.pkl`
- `basketball_features.pkl`
- `ice_hockey_XGB.pkl`
- `ice_hockey_scaler.pkl`
- `ice_hockey_features.pkl`

### **5. Legacy NHL Models** (in `Others/`)

#### **Others/** (9 files)
Historical NHL-specific models:

- `nhl_prediction_model.pkl`
- `nhl_model.pkl`
- `nhl_model_final.pkl`
- `nhl_model_robust.pkl`
- `nhl_features.pkl`
- `nhl_features_final.pkl`
- `nhl_scaler.pkl`
- `nhl_scaler_final.pkl`
- `nhl_scaler_robust.pkl`

---

## 📊 CSV DATA FILES

### **1. Raw Game Data** (Root directory)

- **`mlb_games.csv`** - MLB game records (2015-2025)
- **`nfl_games.csv`** - NFL game records (2015-2025)
- **`nhl_finished_games.csv`** - NHL completed games
- **`nhl_finished_games_complete_features.csv`** - NHL with full feature engineering
- **`nhl_finished_games_complete_features_fixed.csv`** - Corrected NHL features
- **`nhl_dataset_snapshot.csv`** - NHL sample data
- **`nhl_debug_check_results.csv`** - NHL debugging output
- **`nhl_complete_features_FINAL_ATTEMPT.csv`** - Final NHL attempt

### **2. Datasets Folder** (`datasets/`)

League-specific metadata:

- **`NHL_leagues.csv`** - NHL league configuration
- **`NFL_leagues.csv`** - NFL league configuration
- **`NBA_leagues.csv`** - NBA league configuration
- **`MLB_leagues.csv`** - MLB league configuration

### **3. Feature-Engineered Data** (`FINAL_SUPER_ENRICHED_FIXED/`)

#### **Core Feature-Ready CSVs**:

- **`american_football_SUPER_FINAL_FIXED.csv`** - NFL enriched features (domain-aware)
- **`basketball_SUPER_FINAL_FIXED.csv`** - NBA enriched features
- **`baseball_SUPER_FINAL_FIXED.csv`** - MLB enriched features
- **`ice_hockey_SUPER_FINAL_FIXED.csv`** - NHL enriched features

#### **Feature-Ready Subdirectory** (`feature_ready/`):

- **`american_football_FEATURE_READY.csv`** - Processed NFL features
- **`basketball_FEATURE_READY.csv`** - Processed NBA features
- **`baseball_FEATURE_READY.csv`** - Processed MLB features
- **`ice_hockey_FEATURE_READY.csv`** - Processed NHL features

#### **Leak-Free Subdirectory** (`feature_ready_leakfree/`):

- **`american_football_SAFE.csv`** - No-leakage NFL features
- **`basketball_SAFE.csv`** - No-leakage NBA features
- **`baseball_SAFE.csv`** - No-leakage MLB features
- **`ice_hockey_SAFE.csv`** - No-leakage NHL features

### **4. Bayesian Model Results** (Hyperparameter Tuning)

- **`MLB_bayesian_results.csv`** - MLB model hyperparameter optimization
- **`NBA_bayesian_results.csv`** - NBA model hyperparameter optimization
- **`NFL_bayesian_results.csv`** - NFL model hyperparameter optimization
- **`NHL_bayesian_results.csv`** - NHL model hyperparameter optimization

### **5. AUC & Performance Results**

- **`ALL_FINAL_AUC_RESULTS.csv`** - Summary of all model AUC scores
  - Contains: Sport, Model Type, AUC Score
  - NBA: 0.884, NFL: 0.654, MLB: 0.623, NHL: 0.637

### **6. SHAP Feature Importance** (`LL9_5_SHAP/`)

#### **All-Sports Ranking**:
- **`ALL_SPORTS_TOP10_SHAP_FEATURES.csv`** - Top 10 features across all sports

#### **NFL SHAP Rankings**:
- `NFL_SHAP_feature_ranking.csv`
- `NFL_XGB_SHAP_feature_ranking.csv`
- `NFL_LGBM_SHAP_feature_ranking.csv`
- `NFL_RF_SHAP_feature_ranking.csv`

#### **NBA SHAP Rankings**:
- `NBA_SHAP_feature_ranking.csv`
- `NBA_XGB_SHAP_feature_ranking.csv`
- `NBA_LGBM_SHAP_feature_ranking.csv`
- `NBA_RF_SHAP_feature_ranking.csv`

#### **MLB SHAP Rankings**:
- `MLB_SHAP_feature_ranking.csv`
- `MLB_XGB_SHAP_feature_ranking.csv`
- `MLB_LGBM_SHAP_feature_ranking.csv`
- `MLB_RF_SHAP_feature_ranking.csv`

#### **NHL SHAP Rankings**:
- `NHL_SHAP_feature_ranking.csv`
- `NHL_XGB_SHAP_feature_ranking.csv`
- `NHL_LGBM_SHAP_feature_ranking.csv`
- `NHL_RF_SHAP_feature_ranking.csv`

### **7. Model Feature Importances** (`feature_ready/trained_models*` & `real_models_final/`)

#### **Trained Models v2**:
- `american_football_feature_importances.csv`
- `basketball_feature_importances.csv`
- `baseball_feature_importances.csv`
- `ice_hockey_feature_importances.csv`
- `model_training_summary_v2.csv`

#### **Trained Models v3**:
- `american_football_feature_importances.csv`
- `american_football_importances.csv`
- `basketball_feature_importances.csv`
- `basketball_importances.csv`
- `baseball_feature_importances.csv`
- `baseball_importances.csv`
- `ice_hockey_feature_importances.csv`
- `ice_hockey_importances.csv`
- `model_training_summary_v3.csv`
- `summary.csv`
- `evaluation_summary.csv`

#### **Leak-Free Models**:
- `american_football_importance.csv`
- `basketball_importance.csv`
- `baseball_importance.csv`
- `ice_hockey_importance.csv`
- `summary.csv`

### **8. Validation & Testing Reports**

#### **Holdout Validation** (`feature_ready/validation_reports/`):
- `american_football_holdout_report.csv`
- `basketball_holdout_report.csv`
- `baseball_holdout_report.csv`
- `ice_hockey_holdout_report.csv`
- `REAL_PERFORMANCE_SUMMARY.csv`

#### **Training Summaries**:
- `model_training_summary.csv` (v1)
- `model_training_summary_v2.csv`
- `model_training_summary_v3.csv`

#### **Models Directory Summary**:
- `model_training_summary.csv` (in `models/`)

### **9. NHL Dataset** (`NHL_Dataset/`)

Raw NHL play-by-play and game data:

- **`game.csv`** - Main game records
- **`game_teams_stats.csv`** - Per-game team statistics
- **`game_skater_stats.csv`** - Skater performance per game
- **`game_shifts.csv`** - Player shift data
- **`game_scratches.csv`** - Inactive player tracking
- **`game_plays_players.csv`** - Play-by-play player involvement
- **`game_plays.csv`** - Detailed play-by-play events
- **`game_penalties.csv`** - Penalty records
- **`game_officials.csv`** - Referee/official assignments
- **`game_goals.csv`** - Goal-scoring events
- **`game_goalie_stats.csv`** - Goaltender statistics
- **`player_info.csv`** - Player biographical data
- **`team_info.csv`** - Team metadata

---

## ⚙️ CONFIGURATION & ENVIRONMENT FILES

### **1. Environment Files** (`.history/Sports-Project-main/`)

Auto-saved versions of `.env` files with timestamps:

- `.env_20251103092419` - Initial configuration
- `.env_20251113104949` - Mid-update configuration
- `.env_20251113104950` - Latest configuration

**Note**: These likely contain:
- API keys for api-sports.io
- Database connection strings (sports_forecast.db reference)
- Model directory paths

### **2. Requirements File** (`requirements.txt`)

Python package dependencies:

```
aiohttp==3.9.5              # Async HTTP client for API requests
joblib==1.5.2               # Model serialization
lightgbm==4.6.0             # LightGBM ML library
matplotlib==3.10.7          # Plotting
numpy==2.3.4                # Numerical computing (with 2.0 compatibility)
pandas==2.3.3               # Data manipulation
PyQt6==6.10.0               # Desktop GUI framework
pyqt6_sip==13.10.2          # PyQt6 bindings
python-dotenv==1.2.1        # Environment variable loading
qasync==0.28.0              # Async support for PyQt6
requests==2.32.5            # HTTP client
scikit_learn==1.2.2         # Machine learning
shap==0.42.1                # SHAP explainability
xgboost==3.1.1              # XGBoost ML library
```

### **3. Documentation** (`.github/`)

- **`copilot-instructions.md`** - AI development guidelines and architecture overview

---

## 🗂️ COMPLETE DIRECTORY STRUCTURE

```
Sports-Project-main/
│
├── .github/
│   └── copilot-instructions.md ...................... Architecture & development guidelines
│
├── .history/
│   └── Sports-Project-main/
│       ├── .env_* (3 versions) ...................... Environment variables (versioned)
│       └── src/ .................................... Source file versions
│           ├── api_client_20251114092557.py ........ ⭐ Latest API client
│           ├── api_client_20251108145953.py ........ Previous API version
│           ├── prediction_20251121141743.py ........ ⭐ Latest prediction service
│           ├── prediction_20251121124221.py ........ Previous prediction version
│           ├── prediction_20251121123722.py
│           └── prediction_20251108171017.py
│
├── datasets/
│   ├── NHL_leagues.csv ............................. NHL league metadata
│   ├── NFL_leagues.csv ............................. NFL league metadata
│   ├── NBA_leagues.csv ............................. NBA league metadata
│   └── MLB_leagues.csv ............................. MLB league metadata
│
├── NHL_Dataset/ ..................................... Raw NHL play-by-play data
│   ├── game.csv
│   ├── game_teams_stats.csv
│   ├── game_skater_stats.csv
│   ├── game_shifts.csv
│   ├── game_scratches.csv
│   ├── game_plays_players.csv
│   ├── game_plays.csv
│   ├── game_penalties.csv
│   ├── game_officials.csv
│   ├── game_goals.csv
│   ├── game_goalie_stats.csv
│   ├── player_info.csv
│   └── team_info.csv
│
├── Others/ ........................................... Test notebooks & legacy models
│   ├── test.ipynb
│   ├── test1.ipynb
│   ├── sports_forecast.db ........................... SQLite database for game predictions
│   ├── store_csv_to_db/ ............................. Database storage utility
│   ├── nhl_prediction_model.pkl
│   ├── nhl_model.pkl
│   ├── nhl_model_final.pkl
│   ├── nhl_model_robust.pkl
│   ├── nhl_features.pkl
│   ├── nhl_features_final.pkl
│   ├── nhl_scaler.pkl
│   ├── nhl_scaler_final.pkl
│   └── nhl_scaler_robust.pkl
│
├── plots/ ............................................ Generated visualization outputs
│
├── SPREAD_MODELS/ .................................... Spread (margin) regression models
│   ├── NFL_spread_xgb.pkl
│   ├── NFL_spread_rf.pkl
│   ├── NFL_spread_lgb.pkl
│   ├── NBA_spread_xgb.pkl
│   ├── NBA_spread_rf.pkl
│   ├── NBA_spread_lgb.pkl
│   ├── MLB_spread_xgb.pkl
│   ├── MLB_spread_rf.pkl
│   ├── MLB_spread_lgb.pkl
│   ├── NHL_spread_xgb.pkl
│   ├── NHL_spread_rf.pkl
│   └── NHL_spread_lgb.pkl
│
├── LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/ .. Main model & feature directory
│   ├── ALL_FINAL_AUC_RESULTS.csv ................... Final AUC scores summary
│   ├── MLB_bayesian_results.csv ................... MLB hyperparameter tuning results
│   ├── NBA_bayesian_results.csv ................... NBA hyperparameter tuning results
│   ├── NFL_bayesian_results.csv ................... NFL hyperparameter tuning results
│   ├── NHL_bayesian_results.csv ................... NHL hyperparameter tuning results
│   │
│   ├── NHL_MODELS/ ................................. NHL Over/Under ensemble (5 models)
│   │   ├── xgboost.pkl
│   │   ├── lightgbm.pkl
│   │   ├── random_forest.pkl
│   │   ├── meta_logistic.pkl
│   │   └── calibrator.pkl
│   │
│   ├── NBA_MODELS/ ................................. NBA Over/Under ensemble (5 models)
│   │   ├── xgboost.pkl
│   │   ├── lightgbm.pkl
│   │   ├── random_forest.pkl
│   │   ├── meta_logistic.pkl
│   │   └── calibrator.pkl
│   │
│   ├── NFL_MODELS/ ................................. NFL Over/Under ensemble (5 models)
│   │   ├── xgboost.pkl
│   │   ├── lightgbm.pkl
│   │   ├── random_forest.pkl
│   │   ├── meta_logistic.pkl
│   │   ├── calibrator.pkl
│   │   └── ensemble_metadata.json ................. Ensemble configuration
│   │
│   ├── MLB_MODELS/ ................................. MLB Over/Under ensemble (5 models)
│   │   ├── xgboost.pkl
│   │   ├── lightgbm.pkl
│   │   ├── random_forest.pkl
│   │   ├── meta_logistic.pkl
│   │   ├── calibrator.pkl
│   │   └── ensemble_metadata.json
│   │
│   ├── SPREAD_MODELS/ .............................. (Link to ../SPREAD_MODELS)
│   │
│   ├── WINNER_MODELS/ .............................. NFL winner classification
│   │   ├── NFL_winner_xgb.pkl
│   │   ├── NFL_winner_lgb.pkl
│   │   ├── NFL_winner_rf.pkl
│   │   ├── NFL_winner_xgb_calibrator.pkl
│   │   ├── NFL_winner_lgb_calibrator.pkl
│   │   └── NFL_winner_calibrator.pkl
│   │
│   ├── FINAL_SUPER_ENRICHED_FIXED/ ............... Enriched feature datasets
│   │   ├── american_football_SUPER_FINAL_FIXED.csv ... NFL enriched features
│   │   ├── basketball_SUPER_FINAL_FIXED.csv ...... NBA enriched features
│   │   ├── baseball_SUPER_FINAL_FIXED.csv ........ MLB enriched features
│   │   ├── ice_hockey_SUPER_FINAL_FIXED.csv ...... NHL enriched features
│   │   │
│   │   ├── models/ ................................ Multi-sport models (8 files)
│   │   │   ├── xgb_american_football.pkl
│   │   │   ├── xgb_basketball.pkl
│   │   │   ├── xgb_baseball.pkl
│   │   │   ├── xgb_ice_hockey.pkl
│   │   │   ├── rf_american_football.pkl
│   │   │   ├── rf_basketball.pkl
│   │   │   ├── rf_baseball.pkl
│   │   │   ├── rf_ice_hockey.pkl
│   │   │   └── model_training_summary.csv
│   │   │
│   │   ├── feature_ready/ ......................... Processed features
│   │   │   ├── american_football_FEATURE_READY.csv
│   │   │   ├── basketball_FEATURE_READY.csv
│   │   │   ├── baseball_FEATURE_READY.csv
│   │   │   ├── ice_hockey_FEATURE_READY.csv
│   │   │   │
│   │   │   ├── trained_models/ .................. v1 Models (4 files)
│   │   │   │   ├── american_football_XGBoost_model.pkl
│   │   │   │   ├── ice_hockey_XGBoost_model.pkl
│   │   │   │   ├── basketball_XGBoost_model.pkl
│   │   │   │   └── baseball_RandomForest_model.pkl
│   │   │   │
│   │   │   ├── trained_models_v2/ .............. v2 Models (8 files)
│   │   │   │   ├── american_football_XGBoost_model.pkl
│   │   │   │   ├── american_football_scaler.pkl
│   │   │   │   ├── ice_hockey_RandomForest_model.pkl
│   │   │   │   ├── ice_hockey_scaler.pkl
│   │   │   │   ├── basketball_RandomForest_model.pkl
│   │   │   │   ├── basketball_scaler.pkl
│   │   │   │   ├── baseball_XGBoost_model.pkl
│   │   │   │   ├── baseball_scaler.pkl
│   │   │   │   └── model_training_summary_v2.csv
│   │   │   │
│   │   │   ├── trained_models_v3/ .............. v3 Models (12 files)
│   │   │   │   ├── american_football_XGB_model.pkl
│   │   │   │   ├── american_football_XGBoost_model.pkl
│   │   │   │   ├── american_football_scaler.pkl
│   │   │   │   ├── baseball_XGB_model.pkl
│   │   │   │   ├── baseball_XGBoost_model.pkl
│   │   │   │   ├── baseball_scaler.pkl
│   │   │   │   ├── basketball_RF_model.pkl
│   │   │   │   ├── basketball_RandomForest_model.pkl
│   │   │   │   ├── basketball_scaler.pkl
│   │   │   │   ├── ice_hockey_RF_model.pkl
│   │   │   │   ├── ice_hockey_RandomForest_model.pkl
│   │   │   │   ├── ice_hockey_scaler.pkl
│   │   │   │   ├── model_training_summary_v3.csv
│   │   │   │   ├── summary.csv
│   │   │   │   └── evaluation_summary.csv
│   │   │   │
│   │   │   ├── real_models_final/ .............. Production Models (8 files)
│   │   │   │   ├── american_football_REAL.pkl
│   │   │   │   ├── american_football_scaler.pkl
│   │   │   │   ├── baseball_REAL.pkl
│   │   │   │   ├── baseball_scaler.pkl
│   │   │   │   ├── basketball_REAL.pkl
│   │   │   │   ├── basketball_scaler.pkl
│   │   │   │   ├── ice_hockey_REAL.pkl
│   │   │   │   └── ice_hockey_scaler.pkl
│   │   │   │
│   │   │   └── validation_reports/ ............. Holdout validation (6 files)
│   │   │       ├── american_football_holdout_report.csv
│   │   │       ├── basketball_holdout_report.csv
│   │   │       ├── baseball_holdout_report.csv
│   │   │       ├── ice_hockey_holdout_report.csv
│   │   │       └── REAL_PERFORMANCE_SUMMARY.csv
│   │   │
│   │   └── feature_ready_leakfree/ ............. No-leakage models & features
│   │       ├── american_football_SAFE.csv
│   │       ├── basketball_SAFE.csv
│   │       ├── baseball_SAFE.csv
│   │       ├── ice_hockey_SAFE.csv
│   │       │
│   │       └── models_leakfree/ ................. Leakage-free models (12 files)
│   │           ├── american_football_XGB.pkl
│   │           ├── american_football_scaler.pkl
│   │           ├── american_football_features.pkl
│   │           ├── baseball_RF.pkl
│   │           ├── baseball_scaler.pkl
│   │           ├── baseball_features.pkl
│   │           ├── basketball_XGB.pkl
│   │           ├── basketball_scaler.pkl
│   │           ├── basketball_features.pkl
│   │           ├── ice_hockey_XGB.pkl
│   │           ├── ice_hockey_scaler.pkl
│   │           ├── ice_hockey_features.pkl
│   │           ├── american_football_importance.csv
│   │           ├── basketball_importance.csv
│   │           ├── baseball_importance.csv
│   │           ├── ice_hockey_importance.csv
│   │           └── summary.csv
│   │
│   └── LL9_5_SHAP/ ................................. SHAP feature importance rankings
│       ├── ALL_SPORTS_TOP10_SHAP_FEATURES.csv
│       ├── NFL_SHAP_feature_ranking.csv
│       ├── NFL_XGB_SHAP_feature_ranking.csv
│       ├── NFL_LGBM_SHAP_feature_ranking.csv
│       ├── NFL_RF_SHAP_feature_ranking.csv
│       ├── NBA_SHAP_feature_ranking.csv
│       ├── NBA_XGB_SHAP_feature_ranking.csv
│       ├── NBA_LGBM_SHAP_feature_ranking.csv
│       ├── NBA_RF_SHAP_feature_ranking.csv
│       ├── MLB_SHAP_feature_ranking.csv
│       ├── MLB_XGB_SHAP_feature_ranking.csv
│       ├── MLB_LGBM_SHAP_feature_ranking.csv
│       ├── MLB_RF_SHAP_feature_ranking.csv
│       ├── NHL_SHAP_feature_ranking.csv
│       ├── NHL_XGB_SHAP_feature_ranking.csv
│       ├── NHL_LGBM_SHAP_feature_ranking.csv
│       └── NHL_RF_SHAP_feature_ranking.csv
│
├── mlb_games.csv .................................... MLB raw game data
├── nfl_games.csv .................................... NFL raw game data
├── nhl_finished_games.csv ........................... NHL completed games
├── nhl_finished_games_complete_features.csv ........ NHL with features
├── nhl_finished_games_complete_features_fixed.csv .. NHL corrected
├── nhl_dataset_snapshot.csv ......................... NHL sample data
├── nhl_debug_check_results.csv ..................... NHL debug output
├── nhl_complete_features_FINAL_ATTEMPT.csv ........ Final NHL attempt
│
├── requirements.txt .................................. Python dependencies
├── DATA_ANALYSIS_REPORT.txt ......................... Data quality & statistics report
└── CODEBASE_INVENTORY.md ............................ This file!
```

---

## 📈 SUMMARY STATISTICS

| Category | Count |
|----------|-------|
| **Python Source Files** (versioned in .history) | 6 |
| **Model Files (.pkl)** | 111+ |
| **CSV Data Files** | 87+ |
| **Total Games Analyzed** | 52,420 |
| **NHL Dataset Tables** | 13 |
| **Sports Covered** | 4 (NFL, NBA, MLB, NHL) |
| **Models per Sport (O/U)** | 5 (base + ensemble) |
| **SHAP Ranking Files** | 16 |
| **Bayesian Tuning Results** | 4 |

---

## 🔑 KEY OBSERVATIONS

### **Active Source Code**
- All Python source files are **versioned in `.history/Sports-Project-main/src/`** 
- **Latest files** (with timestamps):
  - `api_client_20251114092557.py` (API integration)
  - `prediction_20251121141743.py` (Prediction engine)
- Supporting modules referenced but need to be located:
  - `simulation.py` (Monte Carlo blending)
  - `sport_config.py` (Time-aware configuration)
  - `data_storage.py` (Database operations)

### **Model Architecture**
- **Bayesian Ensemble** for Over/Under (5 models: XGB, LGBM, RF, meta-learner, calibrator)
- **Unified Spread Regression** across all sports (3 models per sport)
- **Sport-Specific Winner Classification** (NFL only, with calibrators)
- **Feature-Ready Models** with multiple versions for optimization

### **Data Quality**
- **Total games analyzed**: 52,420 across 4 sports
- **Data imbalance issues noted**:
  - NBA: 100% UNDER, 0% OVER (potential weighting issue)
  - NFL/MLB: Over-heavy imbalance
  - NHL: Balanced (54.5% OVER, 45.5% UNDER)
- **Data leakage prevention**: Separate `feature_ready_leakfree/` for safe predictions

### **Model Performance (AUC)**
- **NBA**: 0.884 (best)
- **NFL**: 0.654
- **NHL**: 0.637
- **MLB**: 0.623

### **SHAP Explainability**
- **16 feature ranking files** (per model type + overall rankings)
- **Top 10 features** across all sports available

### **Environment & Dependencies**
- Python 3.10+ (using PyQt6, modern async with qasync)
- Machine Learning: scikit-learn, XGBoost 3.1.1, LightGBM 4.6.0
- Explainability: SHAP 0.42.1 (with NumPy 2.0 compatibility patch)
- Async: aiohttp 3.9.5 for API requests, qasync for GUI

---

## 🚀 QUICK START PATHS

### **To Load Models & Make Predictions**
1. Navigate to `.history/Sports-Project-main/src/`
2. Use `prediction_20251121141743.py` → `PredictionService.load_models()`
3. Call `calculate_over_under_prediction()`, `calculate_spread_prediction()`, or `calculate_winner_prediction()`

### **To Fetch Live Data**
1. Use `.history/Sports-Project-main/src/api_client_20251114092557.py`
2. Initialize `APIFootballClient(api_key, sport)`
3. Call `fetch_games()` for latest games

### **To Understand Feature Engineering**
1. Check `FINAL_SUPER_ENRICHED_FIXED/*_SUPER_FINAL_FIXED.csv` for enriched features
2. Reference `LL9_5_SHAP/` for SHAP feature importance rankings

### **To Validate Model Performance**
1. See `ALL_FINAL_AUC_RESULTS.csv` for AUC scores
2. Check `feature_ready/validation_reports/` for holdout test results
3. Review `*_bayesian_results.csv` for hyperparameter tuning details

---

**Last Updated**: November 26, 2025  
**Codebase State**: Pre-game models active, multi-sport ensemble with SHAP explainability
