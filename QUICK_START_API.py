#!/usr/bin/env python3
"""
QUICK REFERENCE - API KEY SETUP
==============================

This script shows you the fastest way to get started.
Run this and follow the output!
"""

import os
import sys
from pathlib import Path


def main():
    print("\n" + "="*70)
    print("SPORTS PREDICTION PLATFORM - API SETUP QUICK REFERENCE")
    print("="*70)
    
    print("\n🚀 FASTEST WAY TO GET STARTED (4 MINUTES):\n")
    
    print("1️⃣  GET FREE API KEY (2 minutes)")
    print("   ┌─ Go to: https://www.api-sports.io/")
    print("   ├─ Click: Sign Up (free tier)")
    print("   ├─ Verify: Email")
    print("   └─ Copy: Your API Key from Dashboard\n")
    
    print("2️⃣  CONFIGURE KEY (30 seconds)")
    print("   Choose ONE option:\n")
    
    print("   A. INTERACTIVE (Recommended):")
    print("      $ python setup_api_key.py")
    print("      (Paste your key when prompted)\n")
    
    print("   B. COMMAND LINE (Fastest):")
    print("      $ python setup_api_key.py YOUR-API-KEY\n")
    
    print("   C. ENVIRONMENT VARIABLE:")
    print("      $ set APISPORTS_KEY=YOUR-API-KEY\n")
    
    print("3️⃣  VERIFY (1 minute)")
    print("   $ python setup_api_key.py")
    print("   Select option 2 (Check status)\n")
    
    print("   Expected output:")
    print("   ✅ API Key Found: xxxxxxxxx***xxxxx")
    print("   ✅ API Connection: WORKING\n")
    
    print("4️⃣  USE DASHBOARD (0 minutes)")
    print("   $ python -m streamlit run comprehensive_sports_dashboard.py --server.port 8505\n")
    print("   Then: Export tab → Fetch Live Games\n")
    
    print("="*70)
    print("THAT'S IT! YOU'RE DONE IN 4 MINUTES!")
    print("="*70)
    
    print("\n📚 DETAILED HELP:\n")
    print("   Setup Guide:        API_SETUP_GUIDE.md")
    print("   Code Examples:      API_SETUP_EXAMPLE.py")
    print("   Architecture:       API_INTEGRATION_SETUP.md")
    print("   Summary:            API_COMPLETE_SUMMARY.md\n")
    
    print("🆘 NEED HELP?\n")
    print("   $ python setup_api_key.py")
    print("   (Choose option 2 to check status)\n")
    
    print("✅ WHAT YOU GET:\n")
    print("   ✓ Real-time games for NFL (32 teams)")
    print("   ✓ Real-time games for NHL (33 teams)")
    print("   ✓ Real-time games for NBA (30 teams)")
    print("   ✓ Real-time games for MLB (30 teams)")
    print("   ✓ Live scores and statistics")
    print("   ✓ ML predictions on live data")
    print("   ✓ CSV/PDF export of live games\n")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
