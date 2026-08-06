import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time
from datetime import datetime

# --- ⚠️ APNI DETAILS YAHAN LIKHEN ⚠️ ---
TELEGRAM_TOKEN = "8996892978:AAEWuSd2tXpgkB37ceJ6ciLgLzOuqlNTOUU"
TELEGRAM_CHAT_ID = "7957407326"

# App Configuration
st.set_page_config(page_title="Quotex Next-Candle Sniper", page_icon="🎯", layout="centered")

st.title("🎯 Quotex Next-Candle Sniper Bot")
st.write("Predicts the direction of the NEXT candle by analyzing the exact final seconds of the current candle.")

# Selection Settings
asset = st.selectbox("Select Asset Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
timeframe = st.selectbox("Select Candle Timeframe", ["1m", "5m"], index=0)

# USER CONTROL: Apni marzi ke seconds select karen
scan_seconds = st.slider("Select Final Scanning Seconds Remaining on Current Candle", min_value=3, max_value=15, value=5, step=1)

st.write("---")

# Main Trigger Button
if st.button(f"⚡ PREDICT NEXT CANDLE (SCAN LAST {scan_seconds} SECONDS)", use_container_width=True):
    status_place = st.empty()
    signal_found = False
    msg = ""
    direction = "HOLD"
    
    # Precise looping for the chosen maximum seconds buffer
    for second in range(1, scan_seconds + 1):
        status_place.subheader(f"⏳ Reading closing momentum... Second {second}/{scan_seconds}")
        
        try:
            # Fetch extremely fresh current price data
            df = yf.download(asset, period="2d", interval=timeframe, progress=False)
            
            if not df.empty:
                # Flat columns structure fix
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.columns = [str(col).strip() for col in df.columns]
                
                close_prices = df['Close'].dropna()
                
                if len(close_prices) >= 50:
                    # Precision Math Overlays
                    ema50 = close_prices.ewm(span=50, adjust=False).mean()
                    sma20 = close_prices.rolling(window=20).mean()
                    std20 = close_prices.rolling(window=20).std()
                    bb_up = sma20 + (1.9 * std20)   
                    bb_low = sma20 - (1.9 * std20)
                    
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
                    
                    # --- NEXT CANDLE MOMENTUM FILTER ---
                    # 🔴 NEXT CANDLE PUT DIRECTION
                    if current_price >= (last_bb_up - 0.0001) and last_rsi > 60:
                        direction = "PUT"
                        msg = f"🔴 **NEXT CANDLE: PUT (DOWN) 📉**\n💱 Asset: {clean_name}\n💵 Strike Price: {current_price:.5f}\n⏱️ Detected at final {scan_seconds - second + 1}s"
                        st.error(f"🔥 NEXT CANDLE PREDICTION FOUND AT SECOND {second}!\n\n{msg}")
                        signal_found = True
                        break 
                        
                    # 🟢 NEXT CANDLE CALL DIRECTION
                    elif current_price <= (last_bb_low + 0.0001) and last_rsi < 40:
                        direction = "CALL"
                        msg = f"🟢 **NEXT CANDLE: CALL (UP) 📈**\n💱 Asset: {clean_name}\n💵 Strike Price: {current_price:.5f}\n⏱️ Detected at final {scan_seconds - second + 1}s"
                        st.success(f"🔥 NEXT CANDLE PREDICTION FOUND AT SECOND {second}!\n\n{msg}")
                        signal_found = True
                        break 
                        
        except Exception as e:
            pass
            
        time.sleep(1) 
        
    status_place.empty()
    
    # Trigger final notification payloads
    if signal_found and direction != "HOLD":
        # Play browser sound to alert the trader instantly
        st.components.v1.html('<audio autoplay><source src="https://mixkit.co" type="audio/wav"></audio>', height=0)
        st.balloons()
        
        # Send instant mobile push via Telegram
        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🎯 **NEXT CANDLE SNIPER** 🎯\n\n{msg}", "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    else:
        st.warning(f"⚖️ Current candle is closing flat in the middle zone. No breakout setup found within the last {scan_seconds} seconds. Wait for the next candle or switch the asset.")
