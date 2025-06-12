# After the "Submit Pick" button success block, add st.rerun():
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
            st.rerun()  # ADD THIS LINE - Forces page refresh with updated data
        else:
            st.error("Failed to save your pick. Please try again.")

# And after the "Sell Selected Position" button success block:
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
        st.rerun()  # ADD THIS LINE - Forces page refresh with updated data
    else:
        st.error("Failed to complete sale. Please try again.")

# Alternative approach: Use st.empty() containers for dynamic updates
# If you want real-time updates without full page refresh, you could use:

# At the top, create placeholders:
# balance_placeholder = st.empty()
# portfolio_stats_placeholder = st.empty()

# Then update them after transactions:
# balance_placeholder.markdown(f"### 💰 Account Balance: ${portfolio['balance']:.2f}")
# with portfolio_stats_placeholder.container():
#     # Update portfolio statistics here

# SUMMARY: What gets updated when st.rerun() is added:
# 
# ✅ Account Balance: st.markdown(f"### 💰 Account Balance: ${portfolio['balance']:.2f}")
# ✅ Portfolio Metrics:
#    - st.metric("Total Invested", f"${total_invested:.2f}")
#    - st.metric("Portfolio Value", f"${total_current_value:.2f}")  
#    - st.metric("Total Gain/Loss", f"${total_gain_loss:.2f}", delta=f"{(total_gain_loss/1000)*100:.1f}%")
# ✅ Position Details in expandable sections:
#    - Current prices for open positions
#    - Current values and unrealized gains/losses
#    - Updated portfolio history with new entries
# ✅ Sell dropdown options (will include new positions)
#
# The st.rerun() forces Streamlit to re-execute the entire script, which:
# 1. Reloads portfolio data from the saved JSON file
# 2. Recalculates all metrics with fresh data
# 3. Fetches current stock prices again
# 4. Updates all display components with new values
#
# This is the standard solution for indicator update issues in Streamlit apps.
