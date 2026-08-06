import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time

# --- ⚠️ APNI DETAILS YAHAN LIKHEN ⚠️ ---
TELEGRAM_TOKEN = "8996892978:AAEWuSd2tXpgkB37ceJ6ciLgLzOuqlNTOUU"
TELEGRAM_CHAT_ID = "7957407326"

# App Configuration
st.set_page_config(page_title="Quotex Fast Trigger Bot", page_icon="⚡", layout="centered")

st.title("⚡ Quotex Ultra-Fast Reversal Trigger Bot")
st.write("Click the button below. The bot will scan the market every second and give an instant signal the MOMENT an entry is found (Max 10 seconds search).")

# Selection Settings
asset = st.selectbox("Select Asset Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
timeframe = st.selectbox("Select Strategy Level", ["1m", "5m"], index=0)

st.write("---")

# Main Trigger Button
if st.button("⚡ FIND INSTANT SIGNAL (MAX 10s SEARCH)", use_container_width=True):
    status_place = st.empty()
    signal_found = False
    msg = ""
    direction = "HOLD"
    
    # Loop runs for maximum 10 seconds, checking every 1 second
    for second in range(1, 11):
        status_place.subheader(f"🔍 Searching live candles... Second {second}/10")
        
        try:
            # Fetch very fresh data
            df = yf.download(asset, period="2d", interval=timeframe, progress=False)
            
            if not df.empty:
                # Flat columns formatting
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df.columns = [str(col).strip() for col in df.columns]
                
                close_prices = df['Close'].dropna()
                
                if len(close_prices) >= 50:
                    # Mathematical Indicators
                    ema50 = close_prices.ewm(span=50, adjust=False).mean()
                    sma20 = close_prices.rolling(window=20).mean()
                    std20 = close_prices.rolling(window=20).std()
                    bb_up = sma20 + (1.9 * std20)   # High precision boundaries
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
                    
                    # --- CRITICAL REVERSAL CHECK (Instant Detection) ---
                    # 🔴 PUT SIGNAL (Price touches upper band & RSI is high)
                    if current_price >= (last_bb_up - 0.0001) and last_rsi > 60:
                        direction = "PUT"
                        msg = f"🔴 **PUT (DOWN) 📉**\n💱 Asset: {clean_name}\nPrice: {current_price:.5f}\nTime: {time.strftime('%H:%M:%S')}"
                        st.error(f"🔥 INSTANT SIGNAL FOUND AT SECOND {second}!\n\n{msg}")
                        signal_found = True
                        break # Stop searching immediately and return signal
                        
                    # 🟢 CALL SIGNAL (Price touches lower band & RSI is low)
                    elif current_price <= (last_bb_low + 0.0001) and last_rsi < 40:
                        direction = "CALL"
                        msg = f"🟢 **CALL (UP) 📈**\n💱 Asset: {clean_name}\nPrice: {current_price:.5f}\nTime: {time.strftime('%H:%M:%S')}"
                        st.success(f"🔥 INSTANT SIGNAL FOUND AT SECOND {second}!\n\n{msg}")
                        signal_found = True
                        break # Stop searching immediately and return signal
                        
        except Exception as e:
            # Skip any network glitch and retry next second
            pass
            
        time.sleep(1) # Wait 1 second before checking again
        
    # Clear the searching text
    status_place.empty()
    
    # Final Action Execution
    if signal_found and direction != "HOLD":
        # Play loud sound in browser instantly
        st.components.v1.html('<audio autoplay><source src="https://mixkit.co" type="audio/wav"></audio>', height=0)
        st.balloons()
        
        # Send instant message to Telegram Mobile app
        url = f"https://telegram.org{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"⚡ **FAST TRIGGER SIGNAL** ⚡\n\n{msg}", "parse_mode": "Markdown"}
        requests.post(url, json=payload)
    else:
        st.warning("⚖️ Market is in the middle zone right now. No high-accuracy breakout found within 10 seconds. Try changing the asset pair or trigger again.")
