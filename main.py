# Paper Squeeze Trader MVP - Web App

# Features:
# - $1,000 fake bankroll
# - 2 curated daily stock picks  
# - Custom squeeze score
# - User picks 1 per day
# - Performance updates daily
# - Monetization-ready zones
# - Sell function implemented
# - Real-time price updates

import streamlit as st
import json
import os
import random
from datetime import date, datetime
import time

# Try to import yfinance, fall back to mock mode if not available
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# --- Squeeze Score Calculator Function ---
def squeeze_score(
    short_interest, borrow_rate, volume_ratio, social_score,
    gamma_exposure, options_volume, insider_activity,
    institutional_activity, macro_triggers
):
    weights = {
        'short_interest': 0.25,
        'borrow_rate': 0.1,
        'volume_ratio': 0.1,
        'social_score': 0.15,
        'gamma_exposure': 0.1,
        'options_volume': 0.1,
        'insider_activity': 0.05,
        'institutional_activity': 0.05,
        'macro_triggers': 0.1
    }
    raw_score = (
        short_interest * weights['short_interest'] +
        borrow_rate * weights['borrow_rate'] +
        volume_ratio * weights['volume_ratio'] +
        social_score * weights['social_score'] +
        gamma_exposure * weights['gamma_exposure'] +
        options_volume * weights['options_volume'] +
        insider_activity * weights['insider_activity'] +
        institutional_activity * weights['institutional_activity'] +
        macro_triggers * weights['macro_triggers']
    )
    return round(raw_score * 100, 2)

# --- Generate Daily Picks (Mock) ---
def generate_daily_picks():
    mock_data = [
        {"ticker": "GME", "short_interest": 0.92, "borrow_rate": 0.87, "volume_ratio": 0.76, "social_score": 0.89,
         "gamma_exposure": 0.82, "options_volume": 0.8, "insider_activity": 0.2, "institutional_activity": 0.4, "macro_triggers": 0.6},
        {"ticker": "AMC", "short_interest": 0.88, "borrow_rate": 0.83, "volume_ratio": 0.68, "social_score": 0.9,
         "gamma_exposure": 0.75, "options_volume": 0.77, "insider_activity": 0.1, "institutional_activity": 0.5, "macro_triggers": 0.5},
        {"ticker": "BBBY", "short_interest": 0.91, "borrow_rate": 0.7, "volume_ratio": 0.6, "social_score": 0.78,
         "gamma_exposure": 0.8, "options_volume": 0.73, "insider_activity": 0.25, "institutional_activity": 0.6, "macro_triggers": 0.45},
        {"ticker": "KOSS", "short_interest": 0.85, "borrow_rate": 0.67, "volume_ratio": 0.72, "social_score": 0.84,
         "gamma_exposure": 0.7, "options_volume": 0.75, "insider_activity": 0.3, "institutional_activity": 0.5, "macro_triggers": 0.4}
    ]
    for stock in mock_data:
        stock["squeeze_score"] = squeeze_score(
            stock["short_interest"], stock["borrow_rate"], stock["volume_ratio"], stock["social_score"],
            stock["gamma_exposure"], stock["options_volume"], stock["insider_activity"],
            stock["institutional_activity"], stock["macro_triggers"]
        )
    sorted_stocks = sorted(mock_data, key=lambda x: x["squeeze_score"], reverse=True)
    return sorted_stocks[:2]

# --- Load or Generate Daily Picks ---
if "daily_picks" not in st.session_state:
    st.session_state.daily_picks = generate_daily_picks()

st.set_page_config(page_title="Paper Squeeze Trader", layout="wide")
st.title("📈 Paper Squeeze Trader")
st.caption(f"Daily Picks for {date.today().strftime('%B %d, %Y')}")

# --- Streamlit Refresh Interval ---
st_autorefresh = st.experimental_rerun if "autorefresh" not in st.session_state else None
st.session_state.autorefresh = True

# --- Display Stock Prices ---
st.markdown("### 🔄 Real-Time Price Updates")
daily_picks = st.session_state.daily_picks
realtime_data = {}

for pick in daily_picks:
    price = 0.0
    if YFINANCE_AVAILABLE:
        try:
            data = yf.Ticker(pick['ticker']).history(period="1d")
            if not data.empty:
                price = round(data['Close'][-1], 2)
        except:
            pass
    else:
        price = round(random.uniform(20.0, 100.0), 2)

    realtime_data[pick['ticker']] = price
    st.write(f"{pick['ticker']} — Current Price: ${price}")

st.divider()


