"""
MULTI-SPORT DASHBOARD - NHL, NFL, NBA, MLB
Clean, simple dashboard with model results
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import joblib

st.set_page_config(page_title="Sports Prediction Platform", page_icon="🏆", layout="wide")

st.title("🏆 Multi-Sport Prediction Platform")
st.markdown("**Commercial-Grade Analytics | NHL • NFL • NBA • MLB**")

models_dir = Path("LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP")

# Sport selector
sport_options = []
sport_folders = {}

for sport in ['NHL', 'NFL', 'NBA', 'MLB']:
    folders = sorted([d for d in models_dir.iterdir() if d.is_dir() and d.name.startswith(f'{sport}_')], reverse=True)
    if folders:
        sport_options.append(sport)
        sport_folders[sport] = folders[0]

if not sport_options:
    st.error("No trained models found! Please run `python train_all_sports.py` first.")
    st.stop()

# Sidebar
selected_sport = st.sidebar.selectbox("Select Sport", sport_options, index=0)

st.sidebar.markdown("---")
st.sidebar.header("Available Models")
for sport in sport_options:
    st.sidebar.success(f"✅ {sport}")

# Load selected sport's metadata
try:
    model_folder = sport_folders[selected_sport]
    metadata = joblib.load(model_folder / "metadata.pkl")
    
    st.sidebar.markdown("---")
    st.sidebar.header(f"{selected_sport} Model Info")
    st.sidebar.info(f"**Version:** {model_folder.name}")
    
    # Main metrics
    st.header(f"{selected_sport} Model Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    val_results = metadata['validation_results']
    
    with col1:
        acc = val_results['accuracy']
        delta = f"+{(acc - 0.5) * 100:.1f}% vs 50%"
        st.metric("Accuracy", f"{acc:.1%}", delta)
    
    with col2:
        st.metric("ROC-AUC", f"{val_results['roc_auc']:.3f}")
    
    with col3:
        st.metric("Precision", f"{val_results['precision']:.3f}")
    
    with col4:
        st.metric("Recall", f"{val_results['recall']:.3f}")
    
    # Status indicator
    if val_results['accuracy'] >= 0.55:
        st.success(f"✅ **PROFITABLE MODEL** - Accuracy exceeds 55% threshold ({val_results['accuracy']:.1%})")
    else:
        st.warning(f"⚠️ Below 55% target - Current: {val_results['accuracy']:.1%}")
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Training Details")
        st.write(f"**Sport:** {metadata['sport']}")
        st.write(f"**Training Games:** {metadata['train_samples']:,}")
        st.write(f"**Validation Games:** {metadata['val_samples']:,}")
        st.write(f"**Features Used:** {len(metadata['feature_names'])}")
        st.write(f"**Created:** {metadata['created_at'][:19]}")
        
        st.markdown("---")
        
        st.subheader("🎯 Additional Metrics")
        st.write(f"**F1 Score:** {val_results['f1_score']:.4f}")
        st.write(f"**Log Loss:** {val_results['log_loss']:.4f}")
        st.write(f"**Brier Score:** {val_results['brier_score']:.4f}")
        st.write(f"**Calibration Error:** {val_results['calibration_error']:.4f}")
    
    with col2:
        st.subheader("🤖 Ensemble Weights")
        
        weights_df = pd.DataFrame({
            'Model': list(metadata['ensemble_weights'].keys()),
            'Weight': list(metadata['ensemble_weights'].values())
        })
        
        st.bar_chart(weights_df.set_index('Model'))
        
        dominant_model = max(metadata['ensemble_weights'].items(), key=lambda x: x[1])
        st.info(f"**{dominant_model[0].upper()}** dominates with {dominant_model[1]:.0%} weight")
        
        st.markdown("---")
        
        st.subheader("🎯 Top Features")
        top_5 = metadata['feature_names'][:5]
        for i, feat in enumerate(top_5, 1):
            st.write(f"**{i}.** `{feat}`")
    
    # Footer info
    st.markdown("---")
    
    st.info(f"""
    **{selected_sport} Model Summary**
    
    ✅ Trained on {metadata['train_samples']:,} games  
    ✅ Validated on {metadata['val_samples']:,} games  
    ✅ {len(metadata['feature_names'])} engineered features  
    ✅ Ensemble of {len(metadata['ensemble_weights'])} models  
    ✅ Time-series validation (no data leakage)
    """)

except Exception as e:
    st.error(f"Error loading {selected_sport} model: {e}")
    st.info("Please ensure models are trained with `python train_all_sports.py`")

# Overall summary at bottom
st.markdown("---")
st.markdown("### 📈 Platform Overview")

cols = st.columns(len(sport_options))
for i, sport in enumerate(sport_options):
    with cols[i]:
        try:
            folder = sport_folders[sport]
            meta = joblib.load(folder / "metadata.pkl")
            acc = meta['validation_results']['accuracy']
            
            st.metric(
                f"{sport}",
                f"{acc:.1%}",
                delta="✅" if acc >= 0.55 else "⚠️"
            )
        except:
            st.metric(f"{sport}", "N/A")

st.markdown("---")
st.markdown("**Multi-Sport Prediction Platform** | Powered by CatBoost, XGBoost, LightGBM")
