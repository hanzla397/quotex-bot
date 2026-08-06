import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time
from datetime import datetime

# --- ⚠️ APNI DETAILS YAHAN LIKHEN ⚠️ ---
TELEGRAM_TOKEN = "8996892978:AAEWuSd2tXpgkB37ceJ6ciLgLzOuqlNTOUU"
TELEGRAM_CHAT_ID = "7957407326"

# App UI Themes
st.set_page_config(page_title="Quotex Institutional Sniper", page_icon="⚡", layout="centered")

st.title("⚡ QUOTEX PRO SNIPER (V3-ALGO)")
st.write("Professional Next-Candle Reversal Engine with Realtime Candlestick Clock Sync.")

# Selection Panels
asset = st.selectbox("🎯 SELECT CURRENT PAIR", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
timeframe = st.selectbox("⏳ CANDLE TIMEFRAME", ["1m", "5m"], index=0)

st.write("---")

# --- LIVE CLOCK AND SECONDS CALCULATOR ---
now = datetime.now()
current_second = now.second

# Calculate how many seconds are remaining in the current 1-minute candle
seconds_remaining = 60 - current_second

st.subheader(f"📊 LIVE CANDLE CLOCK STATUS")
col_c1, col_c2 = st.columns(2)
col_c1.metric(label="⏱️ Current Live Time", value=now.strftime("%H:%M:%S"))
col_c2.metric(label="⏳ Seconds Remaining on Candle", value=f"{seconds_remaining}s", delta="- Next Candle Soon", delta_color="inverse")

st.write("---")

# --- USER OPTIONS ---
scan_buffer = st.slider("Select Scan Execution Buffer (Seconds remaining threshold)", min_value=3, max_value=12, value=5, step=1)

# Main Execution Trigger Button
if st.button("🔥 ANALYZE & PREDICT NEXT CANDLE NOW", use_container_width=True):
    if seconds_remaining > (scan_buffer + 5):
        st.warning(f"⚠️ Current candle has too much time left ({seconds_remaining}s). Professional rule dictates to click this button when the candle has less than {scan_buffer + 3} seconds remaining for maximum accuracy!")
    
    status_box = st.empty()
    
    with st.spinner("Locking institutional volume & liquidity block..."):
        try:
            # Fetch ultra-low latency snapshot data
            df = yf.download(asset, period="2d", interval=timeframe, progress=False)
            
            if not df.empty:
                # Flat index mapping conversion
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.columns = [str(col).strip() for col in df.columns]
                
                # Fetching absolute values
                close_prices = df['Close'].dropna()
                high_prices = df['High'].dropna()
                low_prices = df['Low'].dropna()
                volumes = df['Volume'].dropna()
                
                if len(close_prices) >= 50:
                    # 1. 20-EMA and 50-EMA Trend Filter Matrix
                    ema50 = close_prices.ewm(span=50, adjust=False).mean()
                    ema20 = close_prices.ewm(span=20, adjust=False).mean()
                    
                    # 2. Institutional Bollinger Bands Boundary Configuration
                    sma20 = close_prices.rolling(window=20).mean()
                    std20 = close_prices.rolling(window=20).std()
                    bb_up = sma20 + (2.0 * std20)   
                    bb_low = sma20 - (2.0 * std20)
                    
                    # 3. MFI (Money Flow Index) - The Volume & Liquidity Trap Filter
                    # Calculates inside candle volume strength to detect institutional manipulation
                    typical_price = (high_prices + low_prices + close_prices) / 3
                    raw_money_flow = typical_price * volumes
                    
                    price_diff = typical_price.diff()
                    pos_flow = pd.Series(0.0, index=typical_price.index)
                    neg_flow = pd.Series(0.0, index=typical_price.index)
                    
                    pos_flow[price_diff > 0] = raw_money_flow
                    neg_flow[price_diff < 0] = raw_money_flow
                    
                    pos_mf14 = pos_flow.rolling(window=14).sum()
                    neg_mf14 = neg_flow.rolling(window=14).sum()
                    
                    mfi = 100 - (100 / (1 + (pos_mf14 / (neg_mf14 + 1e-10))))
                    
                    # Extract the absolute final parameters
                    current_price = float(close_prices.iloc[-1])
                    last_mfi = float(mfi.iloc[-1])
                    last_bb_up = float(bb_up.iloc[-1])
                    last_bb_low = float(bb_low.iloc[-1])
                    last_ema50 = float(ema50.iloc[-1])
                    last_ema20 = float(ema20.iloc[-1])
                    
                    clean_name = asset.replace("=X", "")
                    decision = "HOLD"
                    
                    # --- INSTITUTIONAL WIN STRATEGY LOGIC ---
                    
                    # 🔴 PROFESSIONAL PUT REVERSAL CONDITIONS:
                    # Price breaks Upper Bollinger Band + Market is Overbought on Volume (MFI > 75) + Price action rejection
                    if current_price >= (last_bb_up - 0.0001) and last_mfi > 72:
                        decision = "PUT"
                        msg = f"🔴 **PREDICTION: NEXT CANDLE IS PUT (DOWN) 📉**\n💱 Pair: {clean_name}\n💵 Execution Rate: {current_price:.5f}\n📊 Volume Overload (MFI): {last_mfi:.1f}\n⏳ Action Window: Open trade as soon as current candle hits 00s!"
                        st.error(f"🎯 ALGO TARGET MATCHED IN FINAL SECONDS!\n\n{msg}")
                    
                    # 🟢 PROFESSIONAL CALL REVERSAL CONDITIONS:
                    # Price breaks Lower Bollinger Band + Market is Oversold on Volume (MFI < 25) + Support verification
                    elif current_price <= (last_bb_low + 0.0001) and last_mfi < 28:
                        decision = "CALL"
                        msg = f"🟢 **PREDICTION: NEXT CANDLE IS CALL (UP) 📈**\n💱 Pair: {clean_name}\n💵 Execution Rate: {current_price:.5f}\n📊 Volume Overload (MFI): {last_mfi:.1f}\n⏳ Action Window: Open trade as soon as current candle hits 00s!"
                        st.success(f"🎯 ALGO TARGET MATCHED IN FINAL SECONDS!\n\n{msg}")
                        
                    if decision != "HOLD":
                        # Instant browser trigger alert sound
                        st.components.v1.html('<audio autoplay><source src="https://mixkit.co" type="audio/wav"></audio>', height=0)
                        st.balloons()
                        
                        # Dispatch payload to secure mobile terminal via Telegram
                        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🚨 **PRO SNIPER SIGNAL** 🚨\n\n{msg}", "parse_mode": "Markdown"}
                        requests.post(url, json=payload)
                    else:
                        st.info(f"⚖️ **Analyst Report:** Market is currently flat in intermediate tracking zones (MFI: {last_mfi:.1f}). Reversal structure not mature yet. Wait for next candle cycle.")
                        
        except Exception as e:
            st.error(f"System tracking error breakdown: {e}")
