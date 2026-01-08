import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time
from datetime import datetime
import pytz

# --- إعدادات التليجرام ---
TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
CHAT_ID = "8541033784"

def send_alert(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": f"🦅 [V12 - PRO SNIPER]\n{msg}"}, timeout=5)
    except: pass

# --- دوال التحليل المتقدمة ---
def get_session():
    now = datetime.now(pytz.utc).hour
    if 8 <= now < 16: return "LONDON 🇬🇧", "#00ff88"
    if 13 <= now < 21: return "NEW YORK 🇺🇸", "#58a6ff"
    return "ASIAN 🇯🇵", "#ffbd45"

def detect_fvg(df):
    """اكتشاف فجوة القيمة العادلة في آخر 3 شموع"""
    if len(df) < 3: return None
    # FVG صاعد (Bullish)
    if df['Low'].iloc[-1] > df['High'].iloc[-3]:
        return "BULLISH FVG"
    # FVG هابط (Bearish)
    if df['High'].iloc[-1] < df['Low'].iloc[-3]:
        return "BEARISH FVG"
    return None

st.set_page_config(page_title="V12 Ultimate Sniper", layout="wide")

# --- واجهة المستخدم الاحترافية ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0b0e14; color: white; }}
    .metric-card {{ background: #161b22; border-radius: 12px; padding: 15px; border: 1px solid #30363d; text-align: center; }}
    .fvg-box {{ background: #1d2d3d; border: 1px dashed #58a6ff; padding: 10px; border-radius: 8px; margin-top: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    st.header("🛠️ أدوات القناص")
    if st.button("🚀 اختبار النظام"):
        send_alert("✅ النظام يعمل بكامل طاقته V12")
    
    st.markdown("---")
    session_name, session_color = get_session()
    st.subheader("🌐 الجلسة الحالية")
    st.markdown(f"<h2 style='color:{session_color}'>{session_name}</h2>", unsafe_allow_html=True)

# --- معالجة البيانات ---
try:
    # جلب اليورو والدولار للمقارنة (قوة العملة)
    ticker = yf.Ticker("EURUSD=X")
    df = ticker.history(period="1d", interval="1m")
    
    if not df.empty:
        current_price = float(df['Close'].iloc[-1])
        vol_current = int(df['Volume'].iloc[-1])
        high_30 = float(df['High'].iloc[-30:-1].max())
        low_30 = float(df['Low'].iloc[-30:-1].min())
        
        # اكتشاف الـ FVG
        fvg_status = detect_fvg(df)
        
        # منطق SMC (سحب السيولة + ارتداد)
        is_buy_sweep = df['Low'].iloc[-1] < low_30 and current_price > low_30
        is_sell_sweep = df['High'].iloc[-1] > high_30 and current_price < high_30

        # عرض الشاشة الرئيسية
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'><small>BSL (SELL ZONE)</small><h2 style='color:#f85149'>{high_30:.5f}</h2></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><small>LIVE EUR/USD</small><h1 style='color:#58a6ff; font-size:3.5rem;'>{current_price:.5f}</h1></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><small>SSL (BUY ZONE)</small><h2 style='color:#00ff88'>{low_30:.5f}</h2></div>", unsafe_allow_html=True)

        # منطقة القوة المضافة (FVG & Volume)
        st.markdown(f"""
            <div style="display: flex; justify-content: space-around; margin-top: 20px;">
                <div class="metric-card" style="width: 48%;">
                    <b>🔍 فجوة القيمة العادلة (FVG)</b><br>
                    <span style="color:#58a6ff">{fvg_status if fvg_status else "No FVG Detected"}</span>
                </div>
                <div class="metric-card" style="width: 48%;">
                    <b>📊 حجم التداول اللحظي</b><br>
                    <span style="color:#00ff88">{vol_current} عقد</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # التنبيهات الذكية
        if is_buy_sweep:
            msg = f"🟢 BUY SIGNAL\nPrice: {current_price:.5f}\nFVG: {fvg_status}\nVol: {vol_current}"
            send_alert(msg)
            st.balloons()
            st.success(f"🚨 فرصة شراء قوية رصدت في جلسة {session_name}")
            
        if is_sell_sweep:
            msg = f"🔴 SELL SIGNAL\nPrice: {current_price:.5f}\nFVG: {fvg_status}\nVol: {vol_current}"
            send_alert(msg)
            st.snow()
            st.error(f"🚨 فرصة بيع قوية رصدت في جلسة {session_name}")

except:
    st.info("🔄 جاري مزامنة رادار السيولة مع البورصة العالمية...")

time.sleep(15)
st.rerun()
