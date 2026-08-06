import streamlit as st
import pandas as pd
import yfinance as yf
import alpaca_trade_api as tradeapi
import requests
import time
from datetime import datetime
import zoneinfo
import plotly.graph_objects as go

# --- ⚠️ SECURE BROKER & ALERTS CREDENTIALS ⚠️ ---
# Get free Paper Trading API keys by opening an account at app.alpaca.markets
ALPACA_API_KEY = "YOUR_ALPACA_API_KEY_ID"
ALPACA_SECRET_KEY = "YOUR_ALPACA_SECRET_KEY"
ALPACA_BASE_URL = "https://alpaca.markets" # Secure Demo Trading Environment

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

# Initialize Broker API Connection Connection
try:
    broker = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, api_version='v2')
    account_info = broker.get_account()
    broker_connected = True
except Exception as conn_error:
    broker_connected = False

# App Shell Layout Setup
st.set_page_config(page_title="Pro Algorithmic Engine V7", page_icon="⚙️", layout="wide")
st.title("⚙️ PRO INSTITUTIONAL AUTOMATED EXECUTION ENGINE")
st.write("Live Realtime Market Scanner integrated with automated server-side order routing execution panels.")

if not broker_connected:
    st.error(f"❌ Broker Authentication Failed! Please verify your API Key and Secret. Details: {conn_error}")
else:
    st.success(f"✅ Securely connected to Broker Account No: {account_info.account_number} | Available Paper Buying Power: ${float(account_info.cash):,.2f}")

# --- BOT INTERFACE CONFIGURATION CONTROL PANEL ---
st.sidebar.header("🕹️ Strategy Parameters")
asset = st.sidebar.selectbox("🎯 SELECT ASSET", ["AAPL", "MSFT", "EURUSD=X", "GBPUSD=X"])
timeframe = st.sidebar.selectbox("⏳ CANDLE INTERACTION TIMEFRAME", ["1m", "5m"], index=0)
trade_qty = st.sidebar.number_input("📦 TRANSACTION VOLUME (Units/Shares)", min_value=1, value=1, step=1)
scan_buffer = st.sidebar.slider("Execution Buffer Threshold (Seconds remaining to fire trade)", min_value=2, max_value=10, value=5, step=1)

# Activate/Deactivate Auto-Pilot System Switch Toggle
bot_active = st.sidebar.toggle("🚀 ACTIVATE AUTO-PILOT DIRECT BROKER MODE", value=False)

st.write("---")
clock_place = st.empty()
log_place = st.empty()

# --- CONTINUOUS LIVE RUNNING CLOCK AND STRATEGY CONTROLLER ---
# Using Pakistan Standard Time (PKT) for timezone compliance
pk_tz = zoneinfo.ZoneInfo("Asia/Karachi")
now_pk = datetime.now(pk_tz)
current_second = now_pk.second
seconds_remaining = 60 - current_second

with clock_place.container():
    st.subheader("📊 LIVE SYSTEM TRACKING ENGINE")
    c_clk1, c_clk2 = st.columns(2)
    c_clk1.metric("⏱️ Islamabad Live System Time", now_pk.strftime("%H:%M:%S"))
    c_clk2.metric("⏳ Candle Closing Clock Remaining", f"{seconds_remaining}s", delta="- Core Sync Active")

# 3. AUTOMATED TRADING LOGIC TRIGGER
if bot_active and current_second == (60 - scan_buffer):
    with log_place.container():
        st.toast("⚡ Scanning candle structure for breakout patterns...")
        try:
            # Download low-latency market candles
            df = yf.download(asset, period="2d", interval=timeframe, progress=False)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.columns = [str(col).strip() for col in df.columns]
                
                close_prices = df['Close'].dropna()
                
                if len(close_prices) >= 30:
                    # Professional Technical Matrix (Moving Average Convergence Strategy)
                    sma_fast = close_prices.rolling(window=10).mean()
                    sma_slow = close_prices.rolling(window=30).mean()
                    
                    last_price = float(close_prices.iloc[-1])
                    last_fast = float(sma_fast.iloc[-1])
                    last_slow = float(sma_slow.iloc[-1])
                    
                    # Fetching existing positions from broker database to prevent spamming
                    try:
                        open_position = broker.get_position(asset)
                        current_units = int(open_position.qty)
                    except Exception:
                        current_units = 0
                        
                    # 🟢 AUTOMATIC BUY ORDER ROUTING
                    if last_fast > last_slow and current_units == 0:
                        st.success(f"🚀 Bullish Momentum Confirmed! Placing Automatic Market BUY Order for {trade_qty} units...")
                        broker.submit_order(symbol=asset, qty=trade_qty, side='buy', type='market', time_in_force='gtc')
                        
                        # Direct Notification to your Mobile Telegram App
                        msg = f"🚀 **AUTO-TRADER PRO: BUY ORDER EXECUTED**\n🎯 Asset: {asset}\n💵 Executed Price: {last_price:.5f}\n📦 Volume: {trade_qty} Units"
                        requests.post(f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                        st.balloons()
                        
                    # 🔴 AUTOMATIC SELL ORDER ROUTING (Liquidation Reversal)
                    elif last_fast < last_slow and current_units > 0:
                        st.error(f"📉 Bearish Trend Change Confirmed! Liquidating {current_units} open units...")
                        broker.submit_order(symbol=asset, qty=current_units, side='sell', type='market', time_in_force='gtc')
                        
                        msg = f"📉 **AUTO-TRADER PRO: LIQUIDATION SELL EXECUTED**\n🎯 Asset: {asset}\n💵 Executed Price: {last_price:.5f}\n📦 Units Closed: {current_units}"
                        requests.post(f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                    else:
                        st.info("⚖️ System Equilibrium Status: Market tracking conditions stable. Standing by without trade entry.")
        except Exception as runtime_err:
            st.error(f"Execution System Exception: {runtime_err}")
    time.sleep(2) # Enforces safety cooldown loop parameters

# --- LIVE INTERACTIVE GRAPHICAL CHART MONITOR ---
st.subheader(f"📈 Realtime Technical Chart Matrix ({asset})")
try:
    chart_df = yf.download(asset, period="1d", interval=timeframe, progress=False)
    if not chart_df.empty:
        if isinstance(chart_df.columns, pd.MultiIndex):
            chart_df.columns = chart_df.columns.get_level_values(0)
        fig = go.Figure(data=[go.Candlestick(
            x=chart_df.index, open=chart_df['Open'], high=chart_df['High'], low=chart_df['Low'], close=chart_df['Close'], name='Live Candlesticks'
        )])
        fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
except Exception:
    st.info("Compiling live graphical stream layouts...")

# Infinite loop sleep optimization interval to prevent interface tearing and maintain precise time tracking
time.sleep(1)
st.rerun()
