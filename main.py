
# Paper Squeeze Trader MVP - Web App

# Features:
# - $1,000 fake bankroll
# - 2 curated daily stock picks
# - Custom squeeze score
# - User picks 1 per day
# - Performance updates daily
# - Monetization-ready zones

import streamlit as st
import json
import os
import random
from datetime import date
import yfinance as yf

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
picks_file = "/mnt/data/daily_picks.json"
if not os.path.exists(picks_file):
    daily_picks = generate_daily_picks()
    with open(picks_file, "w") as f:
        json.dump(daily_picks, f, indent=2)
else:
    with open(picks_file, "r") as f:
        daily_picks = json.load(f)

# --- Streamlit App UI ---
st.set_page_config(page_title="Paper Squeeze Trader", layout="wide")
st.title("📈 Paper Squeeze Trader")
st.caption(f"Daily Picks for {date.today().strftime('%B %d, %Y')}")

st.markdown("Pick your favorite stock from today's top squeeze candidates:")
selected = st.radio(
    "Which stock do you want to add to your fake portfolio?",
    [f"{p['ticker']} — Squeeze Score: {p['squeeze_score']}" for p in daily_picks]
)

# --- Load Portfolio ---
PORTFOLIO_FILE = "/mnt/data/user_portfolio.json"
if os.path.exists(PORTFOLIO_FILE):
    with open(PORTFOLIO_FILE, "r") as pf:
        portfolio = json.load(pf)
else:
    portfolio = {"balance": 1000.00, "history": [], "last_pick_date": None}

# --- Display Account Balance ---
st.markdown(f"### 💰 Account Balance: ${portfolio['balance']:.2f}")

# --- Investment Input ---
investment_amount = st.number_input("Enter the amount you want to invest today:", min_value=1.0, max_value=portfolio["balance"], value=100.0, step=1.0)

# --- Submit Pick ---
today = date.today().isoformat()
if st.button("Submit Pick"):
    if portfolio["last_pick_date"] == today:
        st.warning("You've already picked a stock today.")
    else:
        pick_ticker = selected.split(" —")[0]
        pick_score = next(p["squeeze_score"] for p in daily_picks if p["ticker"] == pick_ticker)
        stock_data = yf.Ticker(pick_ticker).history(period="2d")
        high = round(stock_data['High'][-1], 2) if not stock_data.empty else 'N/A'
        low = round(stock_data['Low'][-1], 2) if not stock_data.empty else 'N/A'

        pick_record = {
            "date": today,
            "ticker": pick_ticker,
            "score": pick_score,
            "allocation": investment_amount,
            "high": high,
            "low": low
        }

        portfolio["balance"] -= investment_amount
        portfolio["history"].append(pick_record)
        portfolio["last_pick_date"] = today
        with open(PORTFOLIO_FILE, "w") as pf:
            json.dump(portfolio, pf, indent=2)
        st.success(f"✅ You picked {pick_ticker}. ${investment_amount:.2f} has been added to your paper position!")

# --- Sell Function ---
st.markdown("### 💼 Sell a Position")
open_positions = [i for i, e in enumerate(portfolio["history"]) if not e.get("sold")]
if open_positions:
    sell_index = st.selectbox("Select a position to sell:", open_positions, format_func=lambda i: f"{portfolio['history'][i]['ticker']} from {portfolio['history'][i]['date']} (${portfolio['history'][i]['allocation']})")
    if st.button("Sell Selected Position"):
        current_price = round(yf.Ticker(portfolio['history'][sell_index]['ticker']).history(period="1d")['Close'][-1], 2)
        allocation = portfolio['history'][sell_index]['allocation']
        gain = round(current_price - allocation, 2)
        portfolio["balance"] += current_price
        portfolio["history"][sell_index]["sold"] = True
        portfolio["history"][sell_index]["sell_price"] = current_price
        portfolio["history"][sell_index]["gain"] = gain
        with open(PORTFOLIO_FILE, "w") as pf:
            json.dump(portfolio, pf, indent=2)
        st.success(f"Sold {portfolio['history'][sell_index]['ticker']} for ${current_price:.2f}. Gain/Loss: ${gain:.2f}")
else:
    st.info("No open positions to sell.")

# --- Portfolio History ---
st.markdown("### 📊 Your Portfolio History")
if portfolio["history"]:
    for entry in reversed(portfolio["history"]):
        status = "SOLD" if entry.get("sold") else "OPEN"
        result = f"{entry['date']} — {entry['ticker']} ({status})
"
        result += f"Score: {entry['score']} | Allocation: ${entry['allocation']}
"

        if entry.get("sold"):
            result += f"💰 Sold at: ${entry['sell_price']} | Gain/Loss: ${entry['gain']}
"

        result += f"📈 High: ${entry.get('high', 'N/A')} | 📉 Low: ${entry.get('low', 'N/A')}
"

        if entry.get("high") != 'N/A' and entry.get("low") != 'N/A':
            try:
                low_buy = float(entry["low"])
                high_sell = float(entry["high"])
                max_profit = round(high_sell - low_buy, 2)
                result += f"💡 Max Potential Gain: ${max_profit} if bought at daily low and sold at high."
            except:
                pass

        st.info(result)
else:
    st.write("No picks made yet. Your trade history will show here.")

# --- Monetization Placeholder ---
st.divider()
st.markdown("### 💸 Support the Project")
col1, col2 = st.columns([3, 1])
with col1:
    st.write("Enjoying the game? Help keep the squeeze alive.")
with col2:
    st.button("☕ Buy us a coffee")
