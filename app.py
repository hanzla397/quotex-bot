import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import time
from datetime import datetime
import zoneinfo
from sklearn.ensemble import RandomForestClassifier

# --- ⚠️ APNI DETAILS YAHAN LIKHEN ⚠️ ---
TELEGRAM_TOKEN = "8996892978:AAEWuSd2tXpgkB37ceJ6ciLgLzOuqlNTOUU"
TELEGRAM_CHAT_ID = "7957407326"

# App UI Themes
st.set_page_config(page_title="Quotex AI Sniper V5", page_icon="🧠", layout="centered")

st.title("🧠 QUOTEX ISLAMABAD MACHINE LEARNING SNIPER (V5)")
st.write("Artificial Intelligence predicting the exact direction of the NEXT candle based on live market training data.")

# --- CUSTOM CONTROLS PANEL ---
st.subheader("🕹️ AI Configuration Controls")
col_ctrl1, col_ctrl2 = st.columns(2)

with col_ctrl1:
    asset = st.selectbox("🎯 SELECT CURRENT PAIR", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
    timeframe = st.selectbox("⏳ SELECT CANDLE TIMEFRAME", ["1m", "5m"], index=0)

with col_ctrl2:
    trade_expiry = st.selectbox("⏳ SELECT TRADE EXPIRY TIME", ["1 Min", "2 Min", "3 Min", "5 Min"], index=0)
    scan_buffer = st.slider("Select Trigger Buffer (Seconds remaining to scan)", min_value=3, max_value=12, value=5, step=1)

st.write("---")

# Placeholders for live looping updates
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
        col_c2.metric(label="⏳ Current Candle Time Remaining", value=f"{seconds_remaining}s", delta="- AI Prediction Engine Sync", delta_color="inverse")
    
    # 2. Automated AI Trigger System (Executes when buffer threshold is hit)
    if seconds_remaining == scan_buffer:
        with signal_place.container():
            st.toast("🧠 AI is training on live market data patterns...")
            
            try:
                # Fetch maximum historical candles for AI Training (5 Days data)
                df = yf.download(asset, period="5d", interval=timeframe, progress=False)
                
                if not df.empty:
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                    df.columns = [str(col).strip() for col in df.columns]
                    
                    df = df.dropna()
                    
                    # --- AI FEATURE ENGINEERING ---
                    # AI model ko sikhane ke liye features generate karna
                    df['Return'] = df['Close'].pct_change()
                    df['Body'] = df['Close'] - df['Open']
                    df['High_Low'] = df['High'] - df['Low']
                    
                    # Target: Agli candle UP gayi (1) ya DOWN gayi (0)
                    df['Target'] = np.where(df['Close'].shift(-1) > df['Close'], 1, 0)
                    
                    df = df.dropna()
                    
                    # Training Features Matrix
                    features = ['Return', 'Body', 'High_Low']
                    X = df[features]
                    y = df['Target']
                    
                    # Split into train data (leave the last candle for live prediction)
                    X_train = X.iloc[:-1]
                    y_train = y.iloc[:-1]
                    X_live = X.iloc[[-1]] # Exact current live candle features
                    
                    # --- MACHINE LEARNING MODEL TRAINING ---
                    # Random Forest AI Classifier with 100 decision trees
                    model = RandomForestClassifier(n_estimators=100, random_state=42)
                    model.fit(X_train, y_train)
                    
                    # Predict Next Candle Direction and Probability Score
                    prediction = model.predict(X_live)[0]
                    probabilities = model.predict_proba(X_live)[0]
                    ai_accuracy_score = float(probabilities[prediction] * 100)
                    
                    current_price = float(df['Close'].iloc[-1])
                    clean_name = asset.replace("=X", "")
                    
                    # --- AI DECISION DISPATCHER ---
                    # Trigger trade only if AI is highly confident (Accuracy > 60%)
                    if ai_accuracy_score >= 60.0:
                        if prediction == 1:
                            # AI Predicts UP (CALL)
                            msg = f"🟢 **AI PREDICTION: NEXT CANDLE IS CALL (UP) 📈**\n💱 Pair: {clean_name}\n💵 Entry Price: {current_price:.5f}\n🧠 AI Confidence Score: {ai_accuracy_score:.1f}%\n⏳ Trade Expiry: {trade_expiry}\n⚠️ Action: Enter trade exactly at 00s!"
                            st.success(f"🎯 AI TARGET MATCHED WITH HIGH CONFIDENCE!\n\n{msg}")
                            
                            # Browser Sound
                            st.components.v1.html('<audio autoplay><source src="https://mixkit.co" type="audio/wav"></audio>', height=0)
                            st.balloons()
                            
                            # Telegram Alert
                            requests.post(f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": f"🧠 **AI PRO SNIPER SIGNAL** 🟢\n\n{msg}", "parse_mode": "Markdown"})
                        else:
                            # AI Predicts DOWN (PUT)
                            msg = f"🔴 **AI PREDICTION: NEXT CANDLE IS PUT (DOWN) 📉**\n💱 Pair: {clean_name}\n💵 Entry Price: {current_price:.5f}\n🧠 AI Confidence Score: {ai_accuracy_score:.1f}%\n⏳ Trade Expiry: {trade_expiry}\n⚠️ Action: Enter trade exactly at 00s!"
                            st.error(f"🎯 AI TARGET MATCHED WITH HIGH CONFIDENCE!\n\n{msg}")
                            
                            st.components.v1.html('<audio autoplay><source src="https://mixkit.co" type="audio/wav"></audio>', height=0)
                            st.balloons()
                            
                            requests.post(f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": f"🧠 **AI PRO SNIPER SIGNAL** 🔴\n\n{msg}", "parse_mode": "Markdown"} )
                    else:
                        st.info(f"⚖️ **AI Analysis Report:** Market trend is uncertain. AI Confidence is low ({ai_accuracy_score:.1f}%). No trade suggested for the next candle.")
                        
            except Exception as e:
                pass
                
        # 2-second sleep cooldown
        time.sleep(2)
        
    # Microscopic refresh interval timing
    time.sleep(0.8)
