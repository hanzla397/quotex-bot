import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time

# --- ⚠️ APNI DETAILS YAHAN LIKHEN ⚠️ ---
TELEGRAM_TOKEN = "8996892978:AAEWuSd2tXpgkB37ceJ6ciLgLzOuqlNTOUU"
TELEGRAM_CHAT_ID = "7957407326"

# App Configuration
st.set_page_config(page_title="Quotex AI Signals", page_icon="🎯", layout="centered")
st.title("🎯 Quotex Live Signal Generator")
st.write("Click the button below to scan the market for instant accurate signals.")

asset = st.selectbox("Select Asset Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
timeframe = st.selectbox("Select Timeframe", ["1m", "5m", "15m"], index=1)

if st.button("🚀 SCAN MARKET FOR SIGNALS"):
    with st.spinner("Analyzing market indicators (RSI + Bollinger Bands)..."):
        try:
            # 1. Market Data Fetching
            df = yf.download(asset, period="2d", interval=timeframe, progress=False)
            
            if df.empty:
                st.error("Could not fetch market data. Please click SCAN again.")
            else:
                # 🔥 CRITICAL FIX: Multi-Index columns ko flat single-level mein convert karna
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                # Double-check columns are cleaned up properly
                df.columns = [str(col).strip() for col in df.columns]
                
                if 'Close' not in df.columns:
                    st.error("Format Error: Could not parse Close prices. Try clicking SCAN again.")
                else:
                    close_prices = df['Close'].dropna()
                    
                    if len(close_prices) < 50:
                        st.warning("⚠️ Market data loading, please click SCAN again in 5 seconds.")
                    else:
                        # Math Calculations
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
                        
                        current_price = float(close_prices.iloc[-1])
                        last_rsi = float(rsi.iloc[-1])
                        last_bb_up = float(bb_up.iloc[-1])
                        last_bb_low = float(bb_low.iloc[-1])
                        last_ema = float(ema50.iloc[-1])
                        
                        clean_name = asset.replace("=X", "")
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
                            url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🎯 **QUOTEX APP SIGNAL** 🎯\n\n{msg}", "parse_mode": "Markdown"}
                            requests.post(url, json=payload)
                            st.balloons()
                        else:
                            st.info(f"⚖️ Market for {clean_name} is stable right now (RSI: {last_rsi:.1f}). No safe breakout found. Click SCAN again after some time.")
                            
        except Exception as e:
            st.error(f"Engine Error: {e}")
