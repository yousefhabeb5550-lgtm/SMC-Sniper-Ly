import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# إعدادات التليجرام (اليورو)
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_alert(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🇪🇺 [EUR/USD RADAR]\n{msg}"}, timeout=5)
    except: pass

st.set_page_config(page_title="EUR/USD Sniper", layout="centered")

# الواجهة
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: white; text-align: center; }
    .status-card { background: #161b22; border-radius: 15px; padding: 25px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

try:
    # جلب اليورو حصراً
    data = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
    
    if not data.empty and len(data) > 30:
        current_price = float(data['Close'].iloc[-1])
        # تحديد السيولة من القمم والقيعان
        top_liquidity = float(data['High'].iloc[-30:-1].max())
        bottom_liquidity = float(data['Low'].iloc[-30:-1].min())
        
        # --- منطق البيع (القمم) ---
        is_sell = data['High'].iloc[-1] > top_liquidity and current_price < top_liquidity
        
        # --- منطق الشراء (القيعان) ---
        is_buy = data['Low'].iloc[-1] < bottom_liquidity and current_price > bottom_liquidity

        st.markdown(f"""
            <div class="status-card">
                <h2 style="color:#8b949e;">EUR / USD LIVE</h2>
                <h1 style="color:#58a6ff;">{current_price:.5f}</h1>
                <p style="color:#f85149;">Top Liquidity (Sell Zone): {top_liquidity:.5f}</p>
                <p style="color:#00ff88;">Bottom Liquidity (Buy Zone): {bottom_liquidity:.5f}</p>
                <hr style="border-color:#333">
                <h3 style="color:white;">
                    {'🔴 إشارة بيع مؤكدة' if is_sell else '🟢 إشارة شراء مؤكدة' if is_buy else '🔍 جاري مراقبة السيولة من الطرفين...'}
                </h3>
            </div>
        """, unsafe_allow_html=True)

        if is_buy:
            send_alert(f"✅ فرصة شراء (اليورو)\nسعر: {current_price:.5f}")
            st.balloons()
            
        if is_sell:
            send_alert(f"⚠️ فرصة بيع (اليورو)\nسعر: {current_price:.5f}")
            st.snow()

except:
    st.info("جاري سحب بيانات اليورو...")

time.sleep(15)
st.rerun()
