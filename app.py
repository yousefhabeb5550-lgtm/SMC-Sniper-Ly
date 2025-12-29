import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta

# إعدادات الصفحة والتنسيق الجمالي
st.set_page_config(page_title="SMC Sniper Elite", layout="wide")
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .stMetric { background: #161b22; border-radius: 10px; padding: 10px; border: 1px solid #30363d; }
    .small-font { font-size:14px !important; }
    </style>
    """, unsafe_allow_html=True)

def get_data():
    eurusd = yf.Ticker("EURUSD=X").history(period="2d", interval="1m")
    dxy = yf.Ticker("DX-Y.NYB").history(period="2d", interval="1m")
    # جلب أخبار مبسطة (محاكاة أو عبر RSS لاحقاً)
    return eurusd, dxy

df, dxy_df = get_data()

if not df.empty:
    # 1. تحليل الزخم RSI
    df['RSI'] = ta.rsi(df['Close'], length=14)
    current_rsi = round(df['RSI'].iloc[-1], 2)
    
    # 2. حجم السيولة (حركة ديناميكية)
    volume_speed = "عالية 🔥" if df['Volume'].iloc[-1] > df['Volume'].mean() else "هادئة ❄️"
    
    # 3. حساب النقاط SL و TP
    live_price = df['Close'].iloc[-1]
    daily_low = df['Low'].min()
    daily_high = df['High'].max()
    
    sl_pips = 12 # نقاط وقف الخسارة
    tp_pips = 45 # نقاط الهدف
    
    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة (SMC Elite)</h2>", unsafe_allow_html=True)
    
    # صف المؤشرات العلوية
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("EUR/USD", round(live_price, 5))
    c2.metric("زخم السوق (RSI)", f"{current_rsi}%", delta=f"{current_rsi-50:.1f}")
    c3.metric("السيولة حالياً", volume_speed)
    c4.metric("DXY", round(dxy_df['Close'].iloc[-1], 3))

    # قسم الأخبار الاقتصادية (مربع جانبي)
    st.sidebar.markdown("### 📰 أخبار اقتصادية هامة")
    st.sidebar.warning("⏳ انتظار تقرير التضخم الأمريكي (بعد 4 ساعات)")
    st.sidebar.info("🇪🇺 خطاب رئيس البنك المركزي الأوروبي اليوم")

    # جدول الصفقات المطور
    st.write("### 🎯 التوصيات الذكية")
    
    # منطق قوة الفرصة
    power = "قوية جداً ✅" if (current_rsi < 35 or current_rsi > 65) else "ضعيفة (تذبذب) ⚠️"
    
    trade_data = {
        "الفرصة": ["SMC BUY 🟢", "SMC SELL 🔴"],
        "السبب": ["ارتداد من LOD + FVG صاعد", "كسر هيكل BOS عند القمة"],
        "الدخول": [round(daily_low, 5), round(daily_high, 5)],
        "SL (نقاط)": [f"{sl_pips} Pips", f"{sl_pips} Pips"],
        "TP (نقاط)": [f"{tp_pips} Pips", f"{tp_pips} Pips"],
        "القوة": [power, "تحت المراقبة 👀"],
        "نصيحة الذكاء": ["انتظر تأكيد RSI تحت 30", "لا تدخل قبل قمة DXY"]
    }
    
    st.table(pd.DataFrame(trade_data))
    
    # تحديثrequirements.txt بإضافة pandas_ta
    
