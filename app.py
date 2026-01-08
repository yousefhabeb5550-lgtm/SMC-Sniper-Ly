import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# إعدادات التليجرام
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_alert(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🦍 [V10 - DUAL RADAR]\n{msg}"}, timeout=5)
    except: pass

st.set_page_config(page_title="GBP Dual Sniper", layout="centered")

try:
    ticker = yf.Ticker("GBPUSD=X")
    df = ticker.history(period="1d", interval="1m")
    
    if not df.empty and len(df) > 30:
        current_price = float(df['Close'].iloc[-1])
        # تحديد سيولة القيعان (للشراء) وسيولة القمم (للبيع)
        ssl_level = float(df['Low'].iloc[-30:-1].min())
        bsl_level = float(df['High'].iloc[-30:-1].max())
        
        # --- رادار الشراء (Buy Logic) ---
        buy_setup = df['Low'].iloc[-1] < ssl_level and current_price > ssl_level
        
        # --- رادار البيع (Sell Logic) ---
        sell_setup = df['High'].iloc[-1] > bsl_level and current_price < bsl_level

        st.markdown(f"""
            <div style="background:#161b22; padding:30px; border-radius:15px; text-align:center; border: 2px solid #30363d;">
                <h1 style="color:#58a6ff;">{current_price:.5f}</h1>
                <p style="color:#f85149;">BSL (Top): {bsl_level:.5f}</p>
                <p style="color:#00ff88;">SSL (Bottom): {ssl_level:.5f}</p>
                <hr>
                <h2 style="color:white;">
                    {'🚨 SELL SIGNAL!' if sell_setup else '🚨 BUY SIGNAL!' if buy_setup else '⌛ SCANNING BOTH WAYS'}
                </h2>
            </div>
        """, unsafe_allow_html=True)

        if buy_setup:
            send_alert(f"🟢 BUY OPPORTUNITY\nPrice: {current_price:.5f}\nTP: {current_price + 0.0030:.5f}")
            st.balloons()
        
        if sell_setup:
            send_alert(f"🔴 SELL OPPORTUNITY\nPrice: {current_price:.5f}\nTP: {current_price - 0.0030:.5f}")
            st.snow()

except:
    st.info("Searching for liquidity...")

time.sleep(15)
st.rerun()
