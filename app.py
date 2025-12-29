import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="SMC Sniper Pro - Libya", layout="wide")

def get_market_data():
    try:
        eurusd = yf.Ticker("EURUSD=X").history(period="1d", interval="1m")
        dxy = yf.Ticker("DX-Y.NYB").history(period="1d", interval="1m")
        return eurusd, dxy
    except: return None, None

eur_data, dxy_data = get_market_data()

if eur_data is not None and not eur_data.empty:
    live_price = round(eur_data['Close'].iloc[-1], 5)
    daily_high = round(eur_data['High'].max(), 5)
    daily_low = round(eur_data['Low'].min(), 5)
    dxy_price = round(dxy_data['Close'].iloc[-1], 3) if dxy_data is not None else "N/A"

    st.markdown("<h1 style='text-align: center; color: #00FFCC;'>💎 رادار القناص الأسطوري (توقيت ليبيا)</h1>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("EUR/USD الآن", live_price)
    col2.metric("مؤشر الدولار DXY", dxy_price)
    col3.metric("أعلى قمة (HOD)", daily_high)
    col4.metric("أدنى قاع (LOD)", daily_low)

    st.write("---")
    st.subheader("🎯 رادار الصفقات المؤكدة (توقيت ليبيا)")
    
    trades = [
        {"التقييم": "⭐⭐⭐⭐", "النوع": "SMC BUY", "الدخول": daily_low, "الهدف": round(daily_low + 0.0055, 5), "الوقت (ليبيا)": "02:30 PM"},
        {"التقييم": "⭐⭐⭐", "النوع": "SMC SELL", "الدخول": daily_high, "الهدف": round(daily_high - 0.0055, 5), "الوقت (ليبيا)": "10:00 PM"}
    ]
    st.table(pd.DataFrame(trades))
    
    libya_time = (datetime.utcnow() + timedelta(hours=2)).strftime('%H:%M:%S')
    st.info(f"🕒 توقيت طرابلس الآن: {libya_time}")
else:
    st.error("جاري جلب البيانات...")
