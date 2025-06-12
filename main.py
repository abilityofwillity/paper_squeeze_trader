import streamlit as st

# THIS MUST BE FIRST - Configure page before any other Streamlit commands
st.set_page_config(page_title="Paper Squeeze Trader", layout="wide")

import json
import os
import random
from datetime import date, datetime
import time

# Try to import yfinance, fall back to mock data if not available
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    # Don't show warning here - will show later in the UI

# --- Configuration ---
DATA_DIR = "data"  # Local data directory
PORTFOLIO_FILE = os.path.join(DATA_DIR, "user_portfolio.json")
PICKS_FILE = os.path.join(DATA_DIR, "daily_picks.json")

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- Helper Functions ---
def safe_api_call(func, *args, **kwargs):
    """Safely call API functions with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def get_stock_price(ticker):
    """Get current stock price with fallback to mock data"""
    if not YFINANCE_AVAILABLE:
        # Mock prices for demo
        mock_prices = {"GME": 25.50, "AMC": 8.75, "BBBY": 0.85, "KOSS": 12.30}
        return mock_prices.get(ticker, 50.00)
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return round(hist['Close'][-1], 2)
        else:
            return 50.00  # Fallback price
    except Exception as e:
        st.warning(f"Could not fetch price for {ticker}: {str(e)}")
        return 50.00

def get_stock_data(ticker, period="2d"):
    """Get stock data with error handling"""
    if not YFINANCE_AVAILABLE:
        # Mock data
        return {
            'high': random.uniform(20, 100),
            'low': random.uniform(10, 80),
            'close': random.uniform(15, 90)
        }
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        if not hist.empty:
            return {
                'high': round(hist['High'][-1], 2),
                'low': round(hist['Low'][-1], 2),
                'close': round(hist['Close'][-1], 2)
            }
        else:
            return {'high': 50.0, 'low': 45.0, 'close': 47.5}
    except Exception as e:
        st.warning(f"Could not fetch data for {ticker}: {str(e)}")
        return {'high': 50.0, 'low': 45.0, 'close': 47.5}

# --- Squeeze Score Calculator Function ---
def squeeze_score(
    short_interest, borrow_rate, volume_ratio, social_score,
    gamma_exposure, options_volume, insider_activity,
    institutional_activity, macro_triggers
):
    """Calculate squeeze score based on weighted factors"""
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
    """Generate daily stock picks with squeeze scores"""
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
def load_daily_picks():
    """Load daily picks, generate new ones if needed"""
    today = date.today().isoformat()
    
    try:
        if os.path.exists(PICKS_FILE):
            with open(PICKS_FILE, "r") as f:
                data = json.load(f)
                # Check if picks are for today
                if data.get("date") == today:
                    return data["picks"]
    except Exception as e:
        st.warning(f"Error loading picks: {str(e)}")
    
    # Generate new picks for today
    daily_picks = generate_daily_picks()
    picks_data = {"date": today, "picks": daily_picks}
    
    try:
        with open(PICKS_FILE, "w") as f:
            json.dump(picks_data, f, indent=2)
    except Exception as e:
        st.warning(f"Error saving picks: {str(e)}")
    
    return daily_picks

# --- Portfolio Management ---
def load_portfolio():
    """Load user portfolio from file"""
    try:
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "r") as pf:
                return json.load(pf)
    except Exception as e:
        st.warning(f"Error loading portfolio: {str(e)}")
    
    # Default portfolio
    return {"balance": 1000.00, "history": [], "last_pick_date": None}

def save_portfolio(portfolio):
    """Save portfolio to file"""
    try:
        with open(PORTFOLIO_FILE, "w") as pf:
            json.dump(portfolio, pf, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving portfolio: {str(e)}")
        return False

def calculate_position_value(ticker, shares):
    """Calculate current position value"""
    current_price = get_stock_price(ticker)
    return current_price * shares

# --- Streamlit App UI ---
st.title("📈 Paper Squeeze Trader")
st.caption(f"Daily Picks for {date.today().strftime('%B %d, %Y')}")

# Show yfinance warning if needed
if not YLINANCE_AVAILABLE:
    st.warning("⚠️ yfinance not installed. Using mock data. Install with: pip install yfinance")

# Load data
daily_picks = load_daily_picks()
portfolio = load_portfolio()

st.markdown("Pick your favorite stock from today's top squeeze candidates:")

# Display picks with current prices
pick_options = []
for pick in daily_picks:
    current_price = get_stock_price(pick['ticker'])
    pick_options.append(f"{pick['ticker']} — Squeeze Score: {pick['squeeze_score']} — Current Price: ${current_price}")

selected = st.radio(
    "Which stock do you want to add to your fake portfolio?",
    pick_options
)

# --- Display Account Balance ---
st.markdown(f"### 💰 Account Balance: ${portfolio['balance']:.2f}")

# --- Investment Input ---
max_investment = min(portfolio["balance"], 1000.0)
investment_amount = st.number_input(
    "Enter the amount you want to invest today:", 
    min_value=1.0, 
    max_value=max_investment, 
    value=min(100.0, max_investment), 
    step=1.0
)

# --- Submit Pick ---
today = date.today().isoformat()
if st.button("Submit Pick"):
    if portfolio["last_pick_date"] == today:
        st.warning("You've already picked a stock today. Come back tomorrow!")
    elif investment_amount > portfolio["balance"]:
        st.error("Insufficient funds!")
    else:
        pick_ticker = selected.split(" —")[0]
        pick_score = next(p["squeeze_score"] for p in daily_picks if p["ticker"] == pick_ticker)
        
        # Get stock data
        stock_data = get_stock_data(pick_ticker)
        current_price = get_stock_price(pick_ticker)
        
        # Calculate shares purchased
        shares = investment_amount / current_price
        
        pick_record = {
            "date": today,
            "ticker": pick_ticker,
            "score": pick_score,
            "investment": investment_amount,
            "shares": round(shares, 4),
            "entry_price": current_price,
            "high": stock_data['high'],
            "low": stock_data['low'],
            "sold": False
        }

        portfolio["balance"] -= investment_amount
        portfolio["history"].append(pick_record)
        portfolio["last_pick_date"] = today
        
        if save_portfolio(portfolio):
            st.success(f"✅ You picked {pick_ticker}! Bought {shares:.4f} shares at ${current_price:.2f} each for ${investment_amount:.2f}")
            st.rerun()  # Forces page refresh with updated data
        else:
            st.error("Failed to save your pick. Please try again.")

# --- Sell Function ---
st.markdown("### 💼 Sell a Position")
open_positions = [i for i, e in enumerate(portfolio["history"]) if not e.get("sold")]

if open_positions:
    sell_index = st.selectbox(
        "Select a position to sell:", 
        open_positions, 
        format_func=lambda i: f"{portfolio['history'][i]['ticker']} - {portfolio['history'][i]['shares']:.4f} shares from {portfolio['history'][i]['date']} (${portfolio['history'][i]['investment']:.2f})"
    )
    
    if st.button("Sell Selected Position"):
        position = portfolio['history'][sell_index]
        current_price = get_stock_price(position['ticker'])
        
        # Calculate sale proceeds
        sale_proceeds = position['shares'] * current_price
        gain_loss = sale_proceeds - position['investment']
        
        # Update portfolio
        portfolio["balance"] += sale_proceeds
        portfolio["history"][sell_index]["sold"] = True
        portfolio["history"][sell_index]["exit_price"] = current_price
        portfolio["history"][sell_index]["sale_proceeds"] = round(sale_proceeds, 2)
        portfolio["history"][sell_index]["gain_loss"] = round(gain_loss, 2)
        portfolio["history"][sell_index]["sell_date"] = date.today().isoformat()
        
        if save_portfolio(portfolio):
            if gain_loss >= 0:
                st.success(f"🎉 Sold {position['ticker']} for ${sale_proceeds:.2f}! Profit: ${gain_loss:.2f}")
            else:
                st.info(f"📉 Sold {position['ticker']} for ${sale_proceeds:.2f}. Loss: ${abs(gain_loss):.2f}")
            st.rerun()  # Forces page refresh with updated data
        else:
            st.error("Failed to complete sale. Please try again.")
else:
    st.info("No open positions to sell.")

# --- Portfolio History ---
st.markdown("### 📊 Your Portfolio History")
if portfolio["history"]:
    total_invested = sum(pos['investment'] for pos in portfolio['history'])
    total_current_value = portfolio['balance']
    
    # Add current value of open positions
    for pos in portfolio['history']:
        if not pos.get('sold'):
            current_price = get_stock_price(pos['ticker'])
            total_current_value += pos['shares'] * current_price
    
    total_gain_loss = total_current_value - 1000.0  # Starting balance was $1000
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invested", f"${total_invested:.2f}")
    with col2:
        st.metric("Portfolio Value", f"${total_current_value:.2f}")
    with col3:
        st.metric("Total Gain/Loss", f"${total_gain_loss:.2f}", delta=f"{(total_gain_loss/1000)*100:.1f}%")
    
    st.divider()
    
    for entry in reversed(portfolio["history"]):
        status = "SOLD" if entry.get("sold") else "OPEN"
        
        with st.expander(f"{entry['date']} — {entry['ticker']} ({status}) — ${entry['investment']:.2f}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Squeeze Score:** {entry['score']}")
                st.write(f"**Shares:** {entry['shares']:.4f}")
                st.write(f"**Entry Price:** ${entry['entry_price']:.2f}")
                
            with col2:
                if entry.get("sold"):
                    st.write(f"**Exit Price:** ${entry['exit_price']:.2f}")
                    st.write(f"**Sale Proceeds:** ${entry['sale_proceeds']:.2f}")
                    gain_loss_color = "green" if entry['gain_loss'] >= 0 else "red"
                    st.markdown(f"**Gain/Loss:** <span style='color:{gain_loss_color}'>${entry['gain_loss']:.2f}</span>", unsafe_allow_html=True)
                else:
                    current_price = get_stock_price(entry['ticker'])
                    current_value = entry['shares'] * current_price
                    unrealized_gl = current_value - entry['investment']
                    st.write(f"**Current Price:** ${current_price:.2f}")
                    st.write(f"**Current Value:** ${current_value:.2f}")
                    gl_color = "green" if unrealized_gl >= 0 else "red"
                    st.markdown(f"**Unrealized G/L:** <span style='color:{gl_color}'>${unrealized_gl:.2f}</span>", unsafe_allow_html=True)
            
            # Daily high/low info
            if entry.get('high') and entry.get('low'):
                st.write(f"📈 **Day High:** ${entry['high']:.2f} | 📉 **Day Low:** ${entry['low']:.2f}")
                
                try:
                    max_profit = (entry['high'] - entry['low']) * entry['shares']
                    st.info(f"💡 **Max Daily Swing Value:** ${max_profit:.2f} (if timed perfectly)")
                except:
                    pass
else:
    st.write("No picks made yet. Your trade history will show here.")

# --- Monetization Placeholder ---
st.divider()
st.markdown("### 💸 Support the Project")
col1, col2 = st.columns([3, 1])
with col1:
    st.write("Enjoying the paper trading game? Help keep the squeeze data flowing!")
with col2:
    st.button("☕ Buy us a coffee")

# --- Footer ---
st.markdown("---")
st.caption("⚠️ This is a paper trading game for educational purposes only. Not financial advice.")
# 4. Updates all display components with new values
#
# This is the standard solution for indicator update issues in Streamlit apps.
