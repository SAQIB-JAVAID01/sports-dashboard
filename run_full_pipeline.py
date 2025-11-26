#!/usr/bin/env python
"""
Run full 6-phase pipeline on nhl_finished_games.csv and export results
"""
import os
import traceback
from pathlib import Path

from src.main_prediction_pipeline import SportsPredictionPipeline
import pandas as pd

OUTPUT_DIR = Path('./results')
OUTPUT_DIR.mkdir(exist_ok=True)

try:
    pipeline = SportsPredictionPipeline(sport='NHL')
    print('Initialized pipeline')

    # Load raw data from NHL CSV
    data_path = 'nhl_finished_games.csv'
    df_raw = pd.read_csv(data_path)
    print(f'Loaded {len(df_raw):,} games from {data_path}')
    print(f'Columns: {df_raw.columns.tolist()}')
    
    # Normalize column names from NHL CSV
    # NHL CSV has: season, game_id, date, home_team, away_team, home_score, away_score
    rename_map = {
        'date': 'game_date',
        'home_team': 'home_team_name',
        'away_team': 'away_team_name',
    }
    df_raw = df_raw.rename(columns=rename_map)
    
    # Convert date to datetime
    df_raw['game_date'] = pd.to_datetime(df_raw['game_date'], errors='coerce')
    df_raw = df_raw.sort_values('game_date').reset_index(drop=True)
    
    # Store raw data
    pipeline.raw_data = df_raw.copy()
    
    # Convert match-level rows into team-level rows
    # Each game becomes two rows: one for home team, one for away team
    team_rows = []
    for idx, row in df_raw.iterrows():
        home_team = row['home_team_name']
        away_team = row['away_team_name']
        home_score = row['home_score']
        away_score = row['away_score']
        game_date = row['game_date']
        season = row['season']
        game_id = row['game_id']
        
        # Home team row
        team_rows.append({
            'game_id': game_id,
            'game_date': game_date,
            'season': season,
            'team_id': home_team,
            'opponent_id': away_team,
            'team_won': 1 if home_score > away_score else 0,
            'actual_outcome': 1 if home_score > away_score else 0,
            'points_scored': home_score,
            'points_allowed': away_score,
            'odds_decimal': 2.0
        })
        
        # Away team row
        team_rows.append({
            'game_id': game_id,
            'game_date': game_date,
            'season': season,
            'team_id': away_team,
            'opponent_id': home_team,
            'team_won': 1 if away_score > home_score else 0,
            'actual_outcome': 1 if away_score > home_score else 0,
            'points_scored': away_score,
            'points_allowed': home_score,
            'odds_decimal': 2.0
        })
    
    df_for_engineering = pd.DataFrame(team_rows)
    df_for_engineering = df_for_engineering.sort_values('game_date').reset_index(drop=True)
    
    print(f'Converted to team-level: {len(df_for_engineering):,} rows')
    print(f'Sample columns: {df_for_engineering.columns.tolist()}')
    print(f'Data types:\n{df_for_engineering.dtypes}')

    # Data integrity check (use raw data)
    ok = pipeline.validate_data_integrity(df_raw)
    if not ok:
        print('Warning: Data integrity checks flagged issues; proceeding cautiously')

    # Feature engineering (use the team-level dataframe expected by feature engineer)
    X_eng, feature_names = pipeline.engineer_features(df_for_engineering)
    # X_eng expected to include actual_outcome and odds_decimal
    print(f'Engineered features: {len(feature_names)}')

    # Detect leakage
    leakage_ok = pipeline.detect_leakage(X_eng)
    if not leakage_ok:
        print('Data leakage detected; aborting pipeline')
        raise SystemExit(1)

    # Prepare X and y
    if 'actual_outcome' in X_eng.columns:
        y = X_eng['actual_outcome']
        X = X_eng.drop(columns=['actual_outcome'])
    else:
        # fallback to raw
        y = df_raw['home_score'] > df_raw['away_score']
        X = X_eng
    
    # Remove non-numeric columns (game_date, team_id, etc.)
    non_numeric_cols = X.select_dtypes(include=['object', 'datetime64']).columns.tolist()
    if non_numeric_cols:
        print(f'Dropping non-numeric columns: {non_numeric_cols}')
        X = X.drop(columns=non_numeric_cols)

    # Perform time-series cross-validation (use fewer splits for a quicker run)
    print('Running time-series cross-validation (quick mode: 3 splits)...')
    try:
        pipeline.ts_validator.n_splits = 3
    except Exception:
        pass
    cv_results = pipeline.perform_time_series_cv(X, y, split_method='walk_forward')
    print('CV results summary:')
    print(cv_results)

    # Train final model on first 80% and validate on last 20% by date
    df_sorted = X_eng.copy()
    # prefer 'game_date' if present (normalized earlier)
    if 'game_date' in df_sorted.columns:
        df_sorted['game_date'] = pd.to_datetime(df_sorted['game_date'])
        df_sorted = df_sorted.sort_values('game_date')
    split_idx = int(len(df_sorted) * 0.8)
    train_df = df_sorted.iloc[:split_idx]
    test_df = df_sorted.iloc[split_idx:]

    y_train = train_df['actual_outcome']
    X_train = train_df.drop(columns=['actual_outcome'])
    y_val = test_df['actual_outcome']
    X_val = test_df.drop(columns=['actual_outcome'])
    
    # Remove non-numeric columns from X_train and X_val
    non_numeric_cols = X_train.select_dtypes(include=['object', 'datetime64', 'datetime64[ns, UTC]']).columns.tolist()
    if non_numeric_cols:
        print(f'Removing non-numeric columns from train/val: {non_numeric_cols}')
        X_train = X_train.drop(columns=non_numeric_cols, errors='ignore')
        X_val = X_val.drop(columns=non_numeric_cols, errors='ignore')
    
    # Also remove game_id if it exists (not a predictive feature)
    if 'game_id' in X_train.columns:
        X_train = X_train.drop(columns=['game_id'])
        X_val = X_val.drop(columns=['game_id'])
    
    # Final check - show remaining columns and their types
    print(f'X_train shape after cleanup: {X_train.shape}')
    print(f'X_train columns: {X_train.columns.tolist()}')
    print(f'X_train dtypes:\n{X_train.dtypes}')

    print('Training final ensemble model...')
    pipeline.train_final_model(X_train, y_train, X_val, y_val)

    # Predict on validation/test set
    preds = pipeline.ensemble.predict_ensemble(X_val)

    # Validate predictions (use fewer permutations for speed)
    print('Validating predictions (quick mode: 100 permutations)...')
    pipeline.validator.calculate_brier_score(y_val.values, preds)
    pipeline.validator.calculate_log_loss(y_val.values, preds)
    pipeline.validator.calculate_roc_auc(y_val.values, preds)
    pipeline.validator.calibration_analysis(y_val.values, preds)
    perm_p = pipeline.validator.permutation_test(y_val.values, preds, n_permutations=100)
    pipeline.validator.metrics['permutation_p_value'] = perm_p
    metrics = pipeline.validator.metrics
    print('Validation metrics:')
    print(metrics)

    # Backtest
    print('Running backtest...')
    backtest_results = pipeline.backtest_strategy(test_df, preds)
    print('Backtest results:')
    print(backtest_results)

    # Export predictions and report
    pred_file = pipeline.export_predictions(test_df, preds, output_dir=str(OUTPUT_DIR))
    report_file = pipeline.export_report(output_dir=str(OUTPUT_DIR))

    print('\nAll done!')
    print(f'  Predictions saved: {pred_file}')
    print(f'  Report saved: {report_file}')

except Exception as e:
    print('ERROR: Exception during pipeline run')
    traceback.print_exc()
    raise
