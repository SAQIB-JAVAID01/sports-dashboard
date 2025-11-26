# Streamlit Cloud Deployment Guide

## Quick Deploy to Streamlit Cloud

### Step 1: Prepare Repository

1. Push your code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit - Sports Prediction Dashboard"
git remote add origin https://github.com/YOUR_USERNAME/sports-prediction-dashboard.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository
5. Set main file path: `comprehensive_sports_dashboard.py`
6. Click "Deploy"

### Step 3: Configuration

The app will automatically use settings from:
- `.streamlit/config.toml` - Theme and server settings
- `requirements.txt` - Python dependencies

### Files Required for Deployment

```
├── comprehensive_sports_dashboard.py  # Main app (REQUIRED)
├── ml_prediction_integration.py       # ML module
├── requirements.txt                   # Dependencies (REQUIRED)
├── .streamlit/
│   └── config.toml                    # Theme settings
├── datasets/                          # Data files
│   ├── MLB_leagues.csv
│   ├── NBA_leagues.csv
│   ├── NFL_leagues.csv
│   └── NHL_leagues.csv
└── src/                               # Source modules
    ├── __init__.py
    └── pdf_export.py
```

### Environment Variables (Optional)

Set these in Streamlit Cloud dashboard under "Advanced settings":

```toml
# .streamlit/secrets.toml (set in dashboard, not in code)
[general]
environment = "production"

[features]
enable_live_data = true
```

### Resource Limits

Streamlit Community Cloud provides:
- 1 GB memory
- Shared CPU
- Apps sleep after inactivity

For production workloads, consider Streamlit Cloud Teams or self-hosting.

### Troubleshooting

**App crashes on startup:**
- Check `requirements.txt` has all dependencies
- Reduce initial data loading
- Check memory usage

**Models not loading:**
- Ensure model files are included in repo
- Check file paths are relative, not absolute

**Slow performance:**
- Add caching with `@st.cache_data`
- Reduce data file sizes
- Optimize model loading

### Custom Domain (Optional)

1. Go to app settings in Streamlit Cloud
2. Add custom domain
3. Configure DNS CNAME record
4. Wait for SSL certificate

### Monitoring

View app metrics in Streamlit Cloud dashboard:
- Viewer count
- Error logs
- Resource usage

## Local Testing Before Deploy

```bash
# Test with production settings
streamlit run comprehensive_sports_dashboard.py --server.port 8501

# Check all imports work
python -c "import comprehensive_sports_dashboard"
```

## Support

- Streamlit Docs: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
- GitHub Issues: Open issue in your repository
