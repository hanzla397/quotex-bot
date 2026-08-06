import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time
from datetime import datetime
import zoneinfo

# --- ⚠️ APNI DETAILS YAHAN LIKHEN ⚠️ ---
TELEGRAM_TOKEN = "8996892978:AAEWuSd2tXpgkB37ceJ6ciLgLzOuqlNTOUU"
TELEGRAM_CHAT_ID = "7957407326"

# App UI Themes
st.set_page_config(page_title="Quotex Islamabad Sniper V4", page_icon="⚡", layout="centered")

st.title("⚡ QUOTEX ISLAMABAD AUTO-SNIPER V4")
st.write("Live Realtime Countdown Tracker & Next-Candle Precision Predictor (Zero Clicks Required).")

# --- CUSTOM CONTROLS PANEL ---
st.subheader("🕹️ Bot Configuration Controls")
col_ctrl1, col_ctrl2 = st.columns(2)

with col_ctrl1:
    asset = st.selectbox("🎯 SELECT CURRENT PAIR", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
    timeframe = st.selectbox("⏳ SELECT CANDLE TIMEFRAME", ["1m", "5m", "15m"], index=0)

with col_ctrl2:
    trade_expiry = st.selectbox("⏳ SELECT TRADE EXPIRY TIME", ["1 Min", "2 Min", "3 Min", "5 Min"], index=0)
    scan_buffer = st.slider("Select Trigger Buffer (Seconds remaining to scan)", min_value=3, max_value=12, value=5, step=1)

st.write("---")

# Placeholders for live looping updates without screen tearing
clock_place = st.empty()
signal_place = st.empty()

# --- AUTOMATIC LIVE RUNNING LOOP ---
while True:
    # 1. Fetch Precise Islamabad Local Time
    pk_tz = zoneinfo.ZoneInfo("Asia/Karachi")
    now_pk = datetime.now(pk_tz)
    current_second = now_pk.second
    
    # Calculate exact remaining seconds based on chosen candle timeframe
    timeframe_minutes = int(timeframe.replace("m", ""))
    total_candle_seconds = timeframe_minutes * 60
    passed_seconds = (now_pk.minute % timeframe_minutes) * 60 + current_second
    seconds_remaining = total_candle_seconds - passed_seconds
    
    # Render Live Clock and Countdown Dashboard (Updates every single second)
    with clock_place.container():
        st.subheader(f"📊 ISLAMABAD REALTIME TRACKING")
        col_c1, col_c2 = st.columns(2)
        col_c1.metric(label="⏱️ Islamabad Live Clock", value=now_pk.strftime("%H:%M:%S"))
        col_c2.metric(label="⏳ Current Candle Time Remaining", value=f"{seconds_remaining}s", delta="- Next Candle Clock Sync", delta_color="inverse")
    
    # 2. Automated Trigger System (Executes calculations when buffer threshold is breached)
    if seconds_remaining == scan_buffer:
        with signal_place.container():
            st.toast("⚡ Target scanning window hit! Extracting volume momentum...")
            
            try:
                # Fetch fresh snapshot financial metrics
                df = yf.download(asset, period="2d", interval=timeframe, progress=False)
                
                if not df.empty:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df.columns = [str(col).strip() for col in df.columns]
                    
                    close_prices = df['Close'].dropna()
                    high_prices = df['High'].dropna()
                    low_prices = df['Low'].dropna()
                    volumes = df['Volume'].dropna()
                    
                    if len(close_prices) >= 50:
                        # Institutional Overlays Mapping
                        ema50 = close_prices.ewm(span=50, adjust=False).mean()
                        sma20 = close_prices.rolling(window=20).mean()
                        std20 = close_prices.rolling(window=20).std()
                        bb_up = sma20 + (1.9 * std20)   
                        bb_low = sma20 - (1.9 * std20)
                        
                        # MFI Liquidity Traps Engine
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
                        
                        current_price = float(close_prices.iloc[-1])
                        last_mfi = float(mfi.iloc[-1])
                        last_bb_up = float(bb_up.iloc[-1])
                        last_bb_low = float(bb_low.iloc[-1])
                        
                        clean_name = asset.replace("=X", "")
                        decision = "HOLD"
                        
                        # --- PREDICTION STRATEGY ---
                        # 🔴 EXACT NEXT CANDLE DOWN DIRECTION (PUT)
                        if current_price >= (last_bb_up - 0.00015) or last_mfi > 68:
                            decision = "PUT"
                            msg = f"🔴 **PREDICTION: NEXT CANDLE IS PUT (DOWN) 📉**\n💱 Pair: {clean_name}\n💵 Execution Rate: {current_price:.5f}\n⏳ Trade Expiry: {trade_expiry}\n📊 Status: Open Trade exactly when countdown hits 0s!"
                            st.error(f"🎯 ALGO EXECUTION REVERSAL TARGET TARGETED!\n\n{msg}")
                        
                        # 🟢 EXACT NEXT CANDLE UP DIRECTION (CALL)
                        elif current_price <= (last_bb_low + 0.00015) or last_mfi < 32:
                            decision = "CALL"
                            msg = f"🟢 **PREDICTION: NEXT CANDLE IS CALL (UP) 📈**\n💱 Pair: {clean_name}\n💵 Execution Rate: {current_price:.5f}\n⏳ Trade Expiry: {trade_expiry}\n📊 Status: Open Trade exactly when countdown hits 0s!"
                            st.success(f"🎯 ALGO EXECUTION REVERSAL TARGET TARGETED!\n\n{msg}")
                            
                        if decision != "HOLD":
                            # Loud Sound popup trigger alert in browser
                            st.components.v1.html('<audio autoplay><source src="https://mixkit.co" type="audio/wav"></audio>', height=0)
                            st.balloons()
                            
                            # Forward Instant Signal Payload directly to Mobile App
                            url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                            payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"🚨 **ISLAMABAD AUTO SNIPER** 🚨\n\n{msg}", "parse_mode": "Markdown"}
                            requests.post(url, json=payload)
                        else:
                            st.info(f"⚖️ **Current Candle Report:** Consolidation zone detected (MFI: {last_mfi:.1f}). No safe breakout for next candle. Waiting for next interval loop...")
                            
            except Exception as e:
                pass
                
        # 2-second sleep cooldown parameter so it doesn't trigger loop within the same target second block
        time.sleep(2)
        
    # Microscopic refresh interval timing keeping system clock accurate and tightly bound
    time.sleep(0.8)
