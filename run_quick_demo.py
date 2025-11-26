#!/usr/bin/env python
"""
Quick demo: Load NHL data, train ensemble, validate, backtest, and generate report
(Skips complex CV to get quick results)
"""
import os
import traceback
from pathlib import Path
import pandas as pd
import numpy as np

from src.main_prediction_pipeline import SportsPredictionPipeline

OUTPUT_DIR = Path('./results')
OUTPUT_DIR.mkdir(exist_ok=True)

try:
    print('=' * 80)
    print('QUICK DEMO: Sports Prediction Pipeline')
    print('=' * 80)
    
    pipeline = SportsPredictionPipeline(sport='NHL')
    print('\n✓ Initialized pipeline')

    # Load raw data
    data_path = 'nhl_finished_games.csv'
    df_raw = pd.read_csv(data_path)
    print(f'✓ Loaded {len(df_raw):,} games from {data_path}')

    # Convert to team-level rows
    team_rows = []
    for _, r in df_raw.iterrows():
        # home team row
        team_rows.append({
            'team_id': r.get('home_team'),
            'opponent_id': r.get('away_team'),
            'team_won': int(r.get('home_score', 0) > r.get('away_score', 0)),
            'actual_outcome': int(r.get('home_score', 0) > r.get('away_score', 0)),
            'points_scored': r.get('home_score', 0),
            'points_allowed': r.get('away_score', 0),
            'game_date': r.get('date'),
            'season': r.get('season'),
            'odds_decimal': 2.0
        })
        # away team row
        team_rows.append({
            'team_id': r.get('away_team'),
            'opponent_id': r.get('home_team'),
            'team_won': int(r.get('away_score', 0) > r.get('home_score', 0)),
            'actual_outcome': int(r.get('away_score', 0) > r.get('home_score', 0)),
            'points_scored': r.get('away_score', 0),
            'points_allowed': r.get('home_score', 0),
            'game_date': r.get('date'),
            'season': r.get('season'),
            'odds_decimal': 2.0
        })

    df_team = pd.DataFrame(team_rows)
    df_team['home_team_id'] = df_team['team_id']
    df_team['away_team_id'] = df_team['team_id']
    df_team['game_date'] = pd.to_datetime(df_team['game_date'])
    df_team = df_team.sort_values('game_date').reset_index(drop=True)
    
    print(f'✓ Converted to {len(df_team):,} team-level rows')

    # Take a sample to avoid NaN issues from rolling stats
    # Use last 500 games only to have enough rolling history
    df_sample = df_team.tail(500).reset_index(drop=True)
    
    print(f'✓ Using last 500 games for quick demo')

    # Prepare X, y
    y = df_sample['actual_outcome'].values
    X = df_sample[['points_scored', 'points_allowed']].copy()
    X = X.astype(float)
    X = (X - X.mean()) / (X.std() + 1e-6)  # normalize
    
    print(f'✓ Prepared {X.shape[0]} samples with {X.shape[1]} features')

    # Split: 80/20
    split_idx = int(len(X) * 0.8)
    X_train = X[:split_idx]
    y_train = y[:split_idx]
    X_val = X[split_idx:]
    y_val = y[split_idx:]
    
    print(f'✓ Train: {len(X_train)} samples, Val: {len(X_val)} samples')

    # Train ensemble
    print('\nTraining ensemble model...')
    try:
        pipeline.ensemble.train_individual_models(X_train, pd.Series(y_train))
        print('✓ Ensemble trained')
    except Exception as e:
        print(f'⚠ Ensemble training warning: {e}')
        # Use simple fallback: logistic regression
        from sklearn.linear_model import LogisticRegression
        lr = LogisticRegression(max_iter=1000)
        lr.fit(X_train, y_train)
        pipeline.ensemble.lr_model = lr
        print('✓ Fallback model (LogisticRegression) trained')

    # Predict
    try:
        preds = pipeline.ensemble.predict_ensemble(X_val)
    except Exception as e:
        print(f'⚠ Ensemble prediction fallback: {e}')
        preds = pipeline.ensemble.lr_model.predict_proba(X_val)[:, 1]
    
    print(f'✓ Generated {len(preds)} predictions')

    # Validate
    print('\nValidating predictions...')
    pipeline.validator.calculate_brier_score(y_val, preds)
    pipeline.validator.calculate_log_loss(y_val, preds)
    pipeline.validator.calculate_roc_auc(y_val, preds)
    pipeline.validator.calibration_analysis(y_val, preds)
    p_value = pipeline.validator.permutation_test(y_val, preds, n_permutations=50)
    pipeline.validator.metrics['permutation_p_value'] = p_value
    
    metrics = pipeline.validator.metrics
    print('✓ Validation metrics:')
    for key, val in metrics.items():
        if isinstance(val, float):
            print(f'  {key}: {val:.4f}')

    # Backtest
    print('\nRunning backtest...')
    df_val = df_sample.iloc[split_idx:].reset_index(drop=True)
    df_val['predicted_prob'] = preds
    try:
        backtest_results = pipeline.backtester.backtest_bets(df_val, preds)
        print('✓ Backtest complete')
        print(f'  Final bankroll: ${pipeline.backtester.bankroll:.2f}')
        print(f'  Total profit: ${pipeline.backtester.total_pnl:.2f}')
    except Exception as e:
        print(f'⚠ Backtest error: {e}')
        backtest_results = {}

    # Generate report
    print('\nGenerating report...')
    report = pipeline.generate_full_report()
    report_file = OUTPUT_DIR / f'NHL_report_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(report_file, 'w') as f:
        f.write(report)
    print(f'✓ Report saved to {report_file}')

    # Export predictions
    print('\nExporting predictions...')
    pred_df = df_val[['team_id', 'opponent_id', 'game_date', 'actual_outcome', 'odds_decimal']].copy()
    pred_df['predicted_prob'] = preds
    pred_df['confidence'] = np.abs(preds - 0.5) * 2
    pred_file = OUTPUT_DIR / f'NHL_predictions_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv'
    pred_df.to_csv(pred_file, index=False)
    print(f'✓ Predictions exported to {pred_file}')

    print('\n' + '=' * 80)
    print('✅ QUICK DEMO COMPLETE')
    print('=' * 80)
    print(f'\nResults saved to: {OUTPUT_DIR}')
    print(f'  - Report: {report_file.name}')
    print(f'  - Predictions: {pred_file.name}')

except Exception as e:
    print(f'\n❌ ERROR: {e}')
    traceback.print_exc()
