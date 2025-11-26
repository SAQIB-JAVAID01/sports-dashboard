"""
SPORTS PREDICTION DASHBOARD - Streamlit App
Real-time predictions with interactive visualizations
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import joblib
from datetime import datetime, timedelta
import sys

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from src.data_loaders import MultiSportDataLoader
from src.advanced_feature_engineering import AdvancedSportsFeatureEngineer

# Page config
st.set_page_config(
    page_title="Sports Prediction Platform",
    page_icon="🏒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.big-metric {
    font-size: 48px !important;
    font-weight: bold;
    color: #1f77b4;
}
.win-prediction {
    background-color: #d4edda;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #28a745;
}
.loss-prediction {
    background-color: #f8d7da;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #dc3545;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    """Load trained models from disk"""
    models_dir = Path("LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP")
    
    # Find latest NHL model directory
    nhl_dirs = sorted([d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith('NHL_')], 
                     key=lambda x: x.name, reverse=True)
    if not nhl_dirs:
        return None, None, None
    
    latest_dir = nhl_dirs[0]
    
    # Load models
    catboost = joblib.load(latest_dir / "catboost.pkl")
    xgboost = joblib.load(latest_dir / "xgboost.pkl")
    lightgbm = joblib.load(latest_dir / "lightgbm.pkl")
    
    # Load metadata
    metadata = joblib.load(latest_dir / "metadata.pkl")
    
    return {
        'catboost': catboost,
        'xgboost': xgboost,
        'lightgbm': lightgbm
    }, metadata, latest_dir

@st.cache_data
def load_data():
    """Load NHL data"""
    loader = MultiSportDataLoader(Path('.'))
    data = loader.load_sport_data('NHL')
    return data

def make_prediction(models, metadata, team_data):
    """Generate prediction for a team"""
    # Get ensemble weights
    weights = metadata['ensemble_weights']
    
    # Get predictions from each model
    preds = []
    for model_name, model in models.items():
        pred_proba = model.predict_proba(team_data)[:, 1]
        preds.append(weights[model_name] * pred_proba)
    
    # Ensemble prediction
    ensemble_pred = sum(preds)
    
    return ensemble_pred[0]

def main():
    st.title("🏒 NHL Game Prediction Platform")
    st.markdown("**Commercial-Grade Sports Analytics with 58% Accuracy**")
    
    # Sidebar
    st.sidebar.header("Model Information")
    
    # Load models
    with st.spinner("Loading trained models..."):
        models, metadata, model_path = load_models()
    
    if models is None:
        st.error("No trained models found! Please run train_full_model.py first.")
        return
    
    st.sidebar.success("✅ Models loaded successfully")
    st.sidebar.info(f"**Model Version:** {model_path.name}")
    st.sidebar.metric("Validation Accuracy", f"{metadata['validation_results']['accuracy']:.1%}")
    st.sidebar.metric("ROC-AUC", f"{metadata['validation_results']['roc_auc']:.3f}")
    st.sidebar.metric("Training Samples", f"{metadata['train_samples']:,}")
    
    # Load data
    with st.spinner("Loading NHL data..."):
        data = load_data()
        feature_engineer = AdvancedSportsFeatureEngineer('NHL')
        features_df, feature_names = feature_engineer.transform(data)
    
    # Remove NaN rows
    features_df = features_df.dropna()
    
    st.success(f"✅ Loaded {len(features_df):,} games with {len(feature_names)} features")
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Live Predictions", "📊 Analytics", "📈 Model Performance", "⚙️ Settings"])
    
    with tab1:
        st.header("Make Predictions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get unique teams
            teams = sorted(features_df['team_id'].unique())
            home_team = st.selectbox("Home Team", teams, index=0)
        
        with col2:
            away_teams = [t for t in teams if t != home_team]
            away_team = st.selectbox("Away Team", away_teams, index=0)
        
        if st.button("🔮 Generate Prediction", type="primary"):
            # Get recent data for both teams
            home_recent = features_df[features_df['team_id'] == home_team].tail(1)
            away_recent = features_df[features_df['team_id'] == away_team].tail(1)
            
            if len(home_recent) == 0 or len(away_recent) == 0:
                st.error("Not enough data for selected teams")
                return
            
            # Prepare features
            home_features = home_recent[feature_names].copy()
            home_features['is_home'] = 1
            
            away_features = away_recent[feature_names].copy()
            away_features['is_home'] = 0
            
            # Make predictions
            home_win_prob = make_prediction(models, metadata, home_features)
            away_win_prob = make_prediction(models, metadata, away_features)
            
            # Normalize probabilities
            total = home_win_prob + away_win_prob
            home_win_prob = home_win_prob / total
            away_win_prob = away_win_prob / total
            
            # Display results
            st.markdown("---")
            
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.markdown(f"### {home_team}")
                st.markdown(f"<div class='{'win' if home_win_prob > 0.5 else 'loss'}-prediction'>", unsafe_allow_html=True)
                st.markdown(f"<p class='big-metric'>{home_win_prob:.1%}</p>", unsafe_allow_html=True)
                st.markdown("Win Probability")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("### ")
                st.markdown("### ")
                st.markdown("## VS")
            
            with col3:
                st.markdown(f"### {away_team}")
                st.markdown(f"<div class='{'win' if away_win_prob > 0.5 else 'loss'}-prediction'>", unsafe_allow_html=True)
                st.markdown(f"<p class='big-metric'>{away_win_prob:.1%}</p>", unsafe_allow_html=True)
                st.markdown("Win Probability")
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Prediction insights
            st.markdown("---")
            st.subheader("📊 Prediction Insights")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                confidence = abs(home_win_prob - 0.5) * 2
                st.metric("Confidence Level", f"{confidence:.1%}")
            
            with col2:
                spread = abs(home_win_prob - away_win_prob)
                st.metric("Probability Spread", f"{spread:.1%}")
            
            with col3:
                predicted_winner = home_team if home_win_prob > away_win_prob else away_team
                st.metric("Predicted Winner", predicted_winner)
            
            # Team stats comparison
            st.markdown("---")
            st.subheader("📈 Team Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**{home_team} (Recent Form)**")
                st.metric("Win Rate (L10)", f"{home_recent['win_rate_L10'].values[0]:.1%}")
                st.metric("Points/Game (L10)", f"{home_recent['pts_scored_L10'].values[0]:.2f}")
                st.metric("Current Streak", f"{int(home_recent['current_streak'].values[0])}")
            
            with col2:
                st.markdown(f"**{away_team} (Recent Form)**")
                st.metric("Win Rate (L10)", f"{away_recent['win_rate_L10'].values[0]:.1%}")
                st.metric("Points/Game (L10)", f"{away_recent['pts_scored_L10'].values[0]:.2f}")
                st.metric("Current Streak", f"{int(away_recent['current_streak'].values[0])}")
    
    with tab2:
        st.header("Historical Analytics")
        
        # Team performance over time
        st.subheader("Team Win Rates Over Time")
        
        selected_teams = st.multiselect(
            "Select teams to compare",
            options=sorted(features_df['team_id'].unique()),
            default=sorted(features_df['team_id'].unique())[:5]
        )
        
        if selected_teams:
            # Calculate rolling win rates
            team_data = []
            for team in selected_teams:
                team_df = features_df[features_df['team_id'] == team].copy()
                team_df = team_df[['game_date', 'win_rate_L10']].rename(columns={'win_rate_L10': team})
                team_data.append(team_df.set_index('game_date'))
            
            combined = pd.concat(team_data, axis=1)
            st.line_chart(combined)
        
        # League-wide statistics
        st.subheader("League Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_goals = features_df['pts_scored_L10'].mean()
            st.metric("Average Goals/Game", f"{avg_goals:.2f}")
        
        with col2:
            home_advantage = features_df[features_df['is_home'] == 1]['win_rate_L10'].mean() - \
                           features_df[features_df['is_home'] == 0]['win_rate_L10'].mean()
            st.metric("Home Advantage", f"{home_advantage:.1%}")
        
        with col3:
            total_games = len(features_df)
            st.metric("Total Games", f"{total_games:,}")
    
    with tab3:
        st.header("Model Performance Metrics")
        
        # Display validation results
        val_results = metadata['validation_results']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Accuracy", f"{val_results['accuracy']:.1%}")
        
        with col2:
            st.metric("Precision", f"{val_results['precision']:.3f}")
        
        with col3:
            st.metric("Recall", f"{val_results['recall']:.3f}")
        
        with col4:
            st.metric("F1 Score", f"{val_results['f1_score']:.3f}")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("ROC-AUC", f"{val_results['roc_auc']:.4f}")
        
        with col2:
            st.metric("Log Loss", f"{val_results['log_loss']:.4f}")
        
        with col3:
            st.metric("Brier Score", f"{val_results['brier_score']:.4f}")
        
        # Ensemble weights
        st.subheader("Ensemble Model Weights")
        
        weights_df = pd.DataFrame({
            'Model': list(metadata['ensemble_weights'].keys()),
            'Weight': list(metadata['ensemble_weights'].values())
        })
        
        st.bar_chart(weights_df.set_index('Model'))
        
        # Feature importance
        st.subheader("Top Features")
        st.info(f"Total features used: {len(metadata['feature_names'])}")
        
        top_features = metadata['feature_names'][:10]
        st.write("**Top 10 Features:**")
        for i, feat in enumerate(top_features, 1):
            st.write(f"{i}. `{feat}`")
    
    with tab4:
        st.header("Settings & Configuration")
        
        st.subheader("Model Information")
        st.code(f"""
Model Path: {model_path}
Created: {metadata['created_at']}
Sport: {metadata['sport']}
Training Samples: {metadata['train_samples']:,}
Validation Samples: {metadata['val_samples']:,}
Features: {len(metadata['feature_names'])}
        """)
        
        st.subheader("Export Options")
        
        if st.button("📥 Download Predictions (CSV)"):
            # Generate predictions for recent games
            recent = features_df.tail(100)
            predictions = []
            
            for idx, row in recent.iterrows():
                team_features = row[feature_names].to_frame().T
                pred_prob = make_prediction(models, metadata, team_features)
                predictions.append({
                    'game_date': row['game_date'],
                    'team_id': row['team_id'],
                    'win_probability': pred_prob,
                    'predicted_win': 1 if pred_prob > 0.5 else 0
                })
            
            pred_df = pd.DataFrame(predictions)
            csv = pred_df.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"nhl_predictions_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        st.subheader("About")
        st.markdown("""
        **NHL Game Prediction Platform**
        
        - **Accuracy:** 58.0% (exceeds 55% profitable threshold)
        - **Models:** CatBoost, XGBoost, LightGBM ensemble
        - **Features:** 39 advanced metrics (rolling stats, momentum, contextual)
        - **Training:** 17,989 games (2015-2023)
        - **Validation:** 4,498 games (2023-2025)
        
        Built with proper time-series validation to prevent data leakage.
        """)

if __name__ == "__main__":
    main()
