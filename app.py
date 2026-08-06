import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time
import plotly.graph_objects as go
from datetime import datetime
import zoneinfo

# --- ⚠️ SECURE TELEGRAM CREDENTIALS ⚠️ ---
TELEGRAM_TOKEN = "8996892978:AAEWuSd2tXpgkB37ceJ6ciLgLzOuqlNTOUU"
TELEGRAM_CHAT_ID = "7957407326"

# --- CYBERPUNK ULTRA-PREMIUM DARK THEME CSS ---
st.set_page_config(page_title="NEON SNIPER V7", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #090A0F 0%, #121520 100%) !important;
        color: #E2E8F0 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        font-family: 'Courier New', Courier, monospace !important;
    }
    h1, h2, h3 {
        color: #00FFCC !important;
        text-shadow: 0 0 10px rgba(0, 255, 204, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ NEON SNIPER ENGINE — ULTRA V7")
st.write("Professional Institutional Next-Candle Analytics Network | Sync: Islamabad Terminal")

# Session States for Stats
if 'total_trades' not in st.session_state: st.session_state.total_trades = 0
if 'wins' not in st.session_state: st.session_state.wins = 0
if 'losses' not in st.session_state: st.session_state.losses = 0

# --- PREMIUM DATA METRICS BOARD ---
st.write("### 📊 Live Performance Matrix")
c_st1, c_st2, c_st3, c_st4 = st.columns(4)
with c_st1: st.metric("Verified Signals", st.session_state.total_trades)
with c_st2: st.markdown(f"<div style='color:#00FF66; font-size:1.2rem; font-weight:bold;'>✅ Wins: {st.session_state.wins}</div>", unsafe_allow_html=True)
with c_st3: st.markdown(f"<div style='color:#FF3366; font-size:1.2rem; font-weight:bold;'>❌ Losses: {st.session_state.losses}</div>", unsafe_allow_html=True)
with c_st4:
    win_rate = (st.session_state.wins / st.session_state.total_trades * 100) if st.session_state.total_trades > 0 else 0.0
    st.metric("Live Accuracy", f"{win_rate:.1f}%")

st.write("---")

# --- CUSTOM SELECTION CONTROLS PANEL ---
col_in1, col_in2, col_in3 = st.columns(3)
with col_in1:
    asset = st.selectbox("🎯 SELECT CURRENT PAIR", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
with col_in2:
    timeframe = st.selectbox("⏳ CANDLE TIMEFRAME", ["1m", "5m", "15m"], index=0)
with col_in3:
    trade_expiry = st.selectbox("⏳ SELECT TRADE EXPIRY TIME", ["1 Min", "2 Min", "3 Min", "5 Min"], index=0)

st.write("---")

# --- REALTIME AUTOMATIC TICKING ENGINE ---
pk_tz = zoneinfo.ZoneInfo("Asia/Karachi")
now_pk = datetime.now(pk_tz)
current_second = now_pk.second

timeframe_min = int(timeframe.replace("m", ""))
total_sec = timeframe_min * 60
passed_sec = (now_pk.minute % timeframe_min) * 60 + current_second
seconds_remaining = total_sec - passed_sec

col_clk1, col_clk2 = st.columns(2)
with col_clk1:
    st.markdown(f"<div style='background:rgba(0,255,252,0.05); padding:15px; border-left:4px solid #00FFCC; border-radius:4px;'>🕒 <b>Islamabad Clock:</b> <span style='font-family:monospace; font-size:1.5rem; color:#00FFCC;'>{now_pk.strftime('%H:%M:%S')}</span></div>", unsafe_allow_html=True)
with col_clk2:
    border_color = "#FF3366" if seconds_remaining <= 10 else "#00FFCC"
    st.markdown(f"<div style='background:rgba(255,51,102,0.05); padding:15px; border-left:4px solid {border_color}; border-radius:4px;'>⏳ <b>Candle Time Remaining:</b> <span style='font-family:monospace; font-size:1.5rem; color:{border_color};'>{seconds_remaining}s</span></div>", unsafe_allow_html=True)

st.write("---")

signal_place = st.empty()

# --- 5-SECOND ULTRASONIC SCAN TRIGGER ---
if seconds_remaining == 5:
    with signal_place.container():
        st.toast("⚡ Firing 5-second ultra precision analysis array...")
        try:
            df = yf.download(asset, period="2d", interval=timeframe, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.columns = [str(col).strip() for col in df.columns]
                
                close_prices = df['Close'].dropna()
                high_prices = df['High'].dropna()
                low_prices = df['Low'].dropna()
                volumes = df['Volume'].dropna()
                
                if len(close_prices) >= 40:
                    sma20 = close_prices.rolling(window=20).mean()
                    std20 = close_prices.rolling(window=20).std()
                    bb_up = sma20 + (2.35 * std20)    
                    bb_low = sma20 - (2.35 * std20)
                    
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
                    
                    entry_price = float(close_prices.iloc[-1])
                    last_mfi = float(mfi.iloc[-1])
                    last_bb_up = float(bb_up.iloc[-1])
                    last_bb_low = float(bb_low.iloc[-1])
                    
                    clean_name = asset.replace("=X", "")
                    direction = "HOLD"
                    
                    if entry_price >= last_bb_up and last_mfi >= 76.0:
                        direction = "PUT"
                    elif entry_price <= last_bb_low and last_mfi <= 24.0:
                        direction = "CALL"
                        
                    if direction != "HOLD":
                        st.session_state.total_trades += 1
                        st.components.v1.html('<audio autoplay><source src="https://mixkit.co" type="audio/wav"></audio>', height=0)
                        st.balloons()
                        
                        if direction == "PUT":
                            msg = f"🔴 **SIGNAL: CHOOSE PUT (DOWN) 📉**\nPair: {clean_name} | Entry: {entry_price:.5f} | Expiry: {trade_expiry}"
                            st.error(msg)
                        else:
                            msg = f"🟢 **SIGNAL: CHOOSE CALL (UP) 📈**\nPair: {clean_name} | Entry: {entry_price:.5f} | Expiry: {trade_expiry}"
                            st.success(msg)
                            
                        # Telegram Alert Route
                        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
                        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": f"💎 **ELITE SNIPER ALERT** 💎\n\n{msg}", "parse_mode": "Markdown"})
                        
                        # --- AUTO AUDIT SYSTEM ---
                        wait_period = timeframe_min * 60
                        time.sleep(wait_period)
                        
                        check_df = yf.download(asset, period="2d", interval=timeframe, progress=False)
                        if isinstance(check_df.columns, pd.MultiIndex): 
                            check_df.columns = check_df.columns.get_level_values(0)
                        closing_p = float(check_df['Close'].dropna().iloc[-1])
                        
                        if (direction == "CALL" and closing_p > entry_price) or (direction == "PUT" and closing_p < entry_price):
                            st.session_state.wins += 1
                        else:
                            st.session_state.losses += 1
                        st.rerun()
                    else:
                        st.info("⚖️ Candle Audit: Volatility stable. Criteria not met. Waiting...")
        except Exception:
            pass
    time.sleep(2)

# --- NEON LIVE GRAPH INTEGRATION ---
st.write("### 📈 Live Candlestick Radar")
try:
    g_df = yf.download(asset, period="1d", interval=timeframe, progress=False)
    if not g_df.empty:
        if isinstance(g_df.columns, pd.MultiIndex): 
            g_df.columns = g_df.columns.get_level_values(0)
        fig = go.Figure(data=[go.Candlestick(
            x=g_df.index, open=g_df['Open'], high=g_df['High'], low=g_df['Low'], close=g_df['Close'], name='Market'
        )])
        fig.update_layout(template="plotly_dark", height=380, xaxis_rangeslider_visible=False, 
                          plot_bgcolor='#090A0F', paper_bgcolor='#090A0F',
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
except Exception:
    pass

time.sleep(1)
st.rerun()
