# AI Agent Instructions for Sports Forecasting Project

## Project Overview
Multi-sport predictive analytics platform forecasting Over/Under, Spread, and Winner outcomes for **NFL, NBA, MLB, NHL**. Uses ensemble ML models (XGBoost, LightGBM, Random Forest) with SHAP explainability. Models trained on 10 years of historical game data with domain-aware features.

## Architecture

### Data Pipeline
1. **Raw Data**: `{mlb,nfl,nhl}_games.csv`, `NHL_Dataset/` (26K+ games, 2015-2025)
2. **Feature Engineering**: `FINAL_SUPER_ENRICHED_FIXED/` - domain-aware features per sport
   - Train/test splits: `READY_FOR_TRAINING/{sport}_X_train.csv`, etc.
   - Feature engineering preserves temporal integrity (no data leakage)
3. **Model Training**: `LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP/`
   - **O/U Models**: Per-sport Bayesian ensembles in `{MLB,NBA,NFL,NHL}_MODELS/`
   - **Spread Models**: `SPREAD_MODELS/` - unified regression across sports
   - **Winner Models**: `WINNER_MODELS/` - classification + NHL-specific Kaggle models
4. **Explainability**: `LL9_5_SHAP/` - feature rankings per model (SHAP values)

### Core ML Patterns
- **Bayesian Ensemble**: Combines multiple base models using posterior probabilities
- **Monte Carlo Blending**: OverUnderSimulator (simulation.py) for probabilistic score projections
- **Sport-Specific Weights**: NHL uses custom pre-game/live models; others use unified logic
- **Feature Consistency**: All models trained on identical feature engineering (critical!)

## Critical Developer Workflows

### Environment Setup
```powershell
# Activate virtual environment
env310\Scripts\Activate.ps1

# Install dependencies (PyQt6, scikit-learn, XGBoost, SHAP, etc.)
pip install -r requirements.txt
```

### Model Loading & Inference
**File**: `src/prediction.py` (700+ lines, multi-sport handling)
- `PredictionService.load_models()` - loads all pickled models from disk
- `calculate_over_under_prediction()` - Bayesian ensemble + O/U classification
- `calculate_spread_prediction()` - regression-based spread projection
- `calculate_winner_prediction()` - dynamic blending (sport-specific score impact factor)
- **SHAP Integration**: `OverUnderExplainer` provides feature importance

### Data Fetching
**File**: `.history/Sports-Project-main/src/api_client_20251114092557.py`
- `APIFootballClient` - multi-sport API client (api-sports.io)
- Sport endpoints: NFL, NBA, MLB, NHL with league IDs preserved
- Async support (aiohttp) for batch requests
- Retry logic (3 attempts, exponential backoff)

### Jupyter Notebooks
Located in `Others/`: `test.ipynb`, `test1.ipynb`
- Analysis, EDA, model prototyping
- Stored models also available as `.pkl` files for testing

## Project-Specific Conventions

### File Organization
- **Historical Versions**: `.history/` tracks model/API client evolution (version dating: `_20251114092557`)
- **Training Data**: Separate from raw CSVs; feature-ready files in `feature_ready/` subdirectories
- **Results**: All AUC scores in `ALL_FINAL_AUC_RESULTS.csv` (NBA: 0.884, NFL: 0.654, MLB: 0.623, NHL: 0.637)

### Naming Conventions
- Sports: uppercase (`NFL`, `NBA`, `MLB`, `NHL`)
- Models: `{SPORT}_{MODEL_TYPE}_SHAP_feature_ranking.csv` (e.g., `NHL_LGBM_SHAP_feature_ranking.csv`)
- Datasets: `*_SUPER_FINAL_FIXED.csv` indicates enriched, cleaned features

### Critical Configuration
**Paths are absolute from `PROJECT_ROOT`** (src/prediction.py, lines 45-65):
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
NFL_MODEL_DIR = MODEL_DIR / "NFL_MODELS"  # ← Sport-specific
SPREAD_MODEL_DIR = MODEL_DIR / "SPREAD_MODELS"  # ← Shared spread models
WINNER_MODEL_DIR = MODEL_DIR / "WINNER_MODELS"  # ← Unified winner models
NHL_PREGAME_MODEL_PATH = WINNER_MODEL_DIR / "nhl_pre_game_win_model.pkl"  # ← Hockey custom
```

## Integration Points & Data Flow

### API → Model Pipeline
1. `APIFootballClient.fetch_games()` → raw game data
2. Feature engineering (domain logic per sport)
3. Load pickled models from `FINAL_SUPER_ENRICHED_FIXED/`
4. Run inference: `PredictionService.calculate_*_prediction()`
5. Optionally generate SHAP values for explainability

### Multi-Sport Handling
- **Unified Logic**: NFL, NBA, MLB share ensemble approach
- **Hockey Exception**: NHL pre-game & live models are Kaggle-trained with custom features
- **Time-Aware**: `TimeParser` in `sport_config.py` handles live game state

### Known Issues & Workarounds
- **SHAP + NumPy 2.0**: Compatibility patch in prediction.py (lines 19-27) restores `np.obj2sctype`
- **Data Imbalance**: 
  - NBA: 100% UNDER (0% OVER) - may need weighting
  - NFL/MLB: Over-heavy imbalance - flagged in analysis report
  - NHL: Balanced (54.5% OVER, 45.5% UNDER)
- **NHL Duplicates**: 1 duplicate in raw data, 4 in MLB - cleaned in feature preparation

## Testing & Validation

### Data Quality Checks (DATA_ANALYSIS_REPORT.txt)
- Missing values, duplicates, date ranges, class distribution
- All 4 sports: 52,420 total games analyzed

### Model Validation
- Cross-validation results stored in `{SPORT}_bayesian_results.csv`
- SHAP feature ranking CSVs per model type (XGB, LGBM, RF)
- AUC scores in `ALL_FINAL_AUC_RESULTS.csv`

## Key Dependencies
- **ML**: scikit-learn 1.2.2, XGBoost 3.1.1, LightGBM 4.6.0
- **Explainability**: SHAP 0.42.1
- **UI**: PyQt6 6.10.0 + qasync 0.28.0 (async GUI)
- **API**: aiohttp 3.9.5 (async requests)
- **Data**: pandas 2.3.3, numpy 2.3.4

---

**Last Updated**: November 2025 | **Codebase State**: Pre-game models active, NHL-specific Kaggle models integrated
