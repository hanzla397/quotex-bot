import streamlit as st
import pandas as pd
import yfinance as yf
import time

# App Configuration
st.set_page_config(page_title="Quotex AI Signals", page_icon="🎯", layout="centered")

st.title("🎯 Quotex Live Signal Generator")
st.write("Click the button below to scan the market for instant accurate signals.")

# Input fields for user so you can change details anytime inside the app
st.subheader("🛠️ Connection Settings")
telegram_token = st.text_input("8996892978:AAEWuSd2tXpgkB37ceJ6ciLgLzOuqlNTOUU", type="123456", help="BotFather se mila hua token")
telegram_chat_id = st.text_input("7957407326", help="userinfobot se mili hui ID")

asset = st.selectbox("Select Asset Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
timeframe = st.selectbox("Select Timeframe", ["1m", "5m", "15m"], index=1)

# Scan Button
if st.button("🚀 SCAN MARKET FOR SIGNALS"):
    if not telegram_token or not telegram_chat_id:
        st.warning("⚠️ Please enter your Telegram Token and Chat ID first!")
    else:
        with st.spinner("Analyzing market indicators (RSI + Bollinger Bands)..."):
            try:
                # Data Fetching
                df = yf.download(asset, period="2d", interval=timeframe, progress=False)
                if df.empty:
                    st.error("Could not fetch market data. Try again.")
                else:
                    df.columns = [col if isinstance(col, tuple) else col for col in df.columns]
                    close_prices = df['Close']
                    
                    # Technical Math Calculations
                    ema50 = close_prices.ewm(span=50, adjust=False).mean()
                    sma20 = close_prices.rolling(window=20).mean()
                    std20 = close_prices.rolling(window=20).std()
                    bb_up = sma20 + (2 * std20)
                    bb_low = sma20 - (2 * std20)
                    
                    delta = close_prices.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / (loss + 1e-10)
                    rsi = 100 - (100 / (1 + rs))
                    
                    # Current Live Values
                    current_price = float(close_prices.iloc[-1])
                    last_rsi = float(rsi.iloc[-1])
                    last_bb_up = float(bb_up.iloc[-1])
                    last_bb_low = float(bb_low.iloc[-1])
                    last_ema = float(ema50.iloc[-1])
                    
                    clean_name = asset.replace("=X", "")
                    
                    # Signal Logic Evaluation
                    signal_found = False
                    
                    # 🔴 PUT SIGNAL
                    if current_price < last_ema and current_price >= last_bb_up and last_rsi > 65:
                        msg = f"🔴 PUT (DOWN)\nAsset: {clean_name}\nPrice: {current_price:.5f}\nExpiry: {timeframe}"
                        st.error(f"🔥 SIGNAL FOUND!\n\n{msg}")
                        signal_found = True
                    
                    # 🟢 CALL SIGNAL
                    elif current_price > last_ema and current_price <= last_bb_low and last_rsi < 35:
                        msg = f"🟢 CALL (UP)\nAsset: {clean_name}\nPrice: {current_price:.5f}\nExpiry: {timeframe}"
                        st.success(f"🔥 SIGNAL FOUND!\n\n{msg}")
                        signal_found = True
                        
                    if signal_found:
                        # Telegram Notification Sending
                        url = f"https://telegram.org{telegram_token}/sendMessage"
                        payload = {"chat_id": telegram_chat_id, "text": f"🎯 **QUOTEX APP SIGNAL** 🎯\n\n{msg}", "parse_mode": "Markdown"}
                        import requests
                        requests.post(url, json=payload)
                        st.balloons()
                    else:
                        st.info("⚖️ Market is stable right now. No high-accuracy entry found. Try another asset or wait for the next candle.")
                        
            except Exception as e:
                st.error(f"Error analyzing data: {e}")
