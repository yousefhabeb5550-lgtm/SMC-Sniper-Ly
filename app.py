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
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🇪🇺 [EUR/USD] {msg}"}, timeout=5)
    except: pass

st.set_page_config(page_title="EUR Sniper", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; text-align: center; }
    .main-card { background: #161b22; border-radius: 20px; padding: 35px; border: 1px solid #30363d; margin-top: 20px; }
    .price-val { font-size: 5rem; color: #58a6ff; font-weight: bold; font-family: monospace; }
    </style>
""", unsafe_allow_html=True)

try:
    # استخدام التيكر المباشر - الطريقة الأسرع لعام 2026
    ticker = yf.Ticker("EURUSD=X")
    # جلب بيانات كافية (آخر ساعتين)
    df = ticker.history(period="1d", interval="1m")
    
    if not df.empty:
        current_price = float(df['Close'].iloc[-1])
        # تحديد السيولة
        high_30 = float(df['High'].iloc[-30:-1].max())
        low_30 = float(df['Low'].iloc[-30:-1].min())
        
        # الشروط
        is_buy = df['Low'].iloc[-1] < low_30 and current_price > low_30
        is_sell = df['High'].iloc[-1] > high_30 and current_price < high_30

        st.markdown(f"""
            <div class="main-card">
                <h3 style="color:#8b949e">EURO / US DOLLAR</h3>
                <div class="price-val">{current_price:.5f}</div>
                <div style="display:flex; justify-content:space-around; margin-top:20px;">
                    <div><small style="color:#f85149">Top (BSL)</small><br><b>{high_30:.5f}</b></div>
                    <div><small style="color:#00ff88">Bottom (SSL)</small><br><b>{low_30:.5f}</b></div>
                </div>
                <hr style="border-color:#333">
                <h2 style="color:white">
                    {'🔴 SELL SIGNAL' if is_sell else '🟢 BUY SIGNAL' if is_buy else '🔍 SCANNING...'}
                </h2>
            </div>
        """, unsafe_allow_html=True)

        if is_buy: send_alert(f"✅ شراء يورو: {current_price:.5f}")
        if is_sell: send_alert(f"⚠️ بيع يورو: {current_price:.5f}")

    else:
        st.error("⚠️ لم نتمكن من جلب بيانات اليورو.. جاري إعادة المحاولة")

except Exception as e:
    st.warning("🔄 السيرفر يحاول الاتصال بالبيانات العالمية...")

time.sleep(15)
st.rerun()
