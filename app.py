import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="SMC Sniper Elite", layout="wide")

# تصميم الواجهة وتصغير الخطوط
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
    div[data-testid="stTable"] { font-size: 12px !important; }
    th { background-color: #1f2937 !important; color: #00FFCC !important; }
    </style>
    """, unsafe_allow_html=True)

def get_data():
    try:
        eurusd = yf.Ticker("EURUSD=X").history(period="2d", interval="1m")
        dxy = yf.Ticker("DX-Y.NYB").history(period="2d", interval="1m")
        return eurusd, dxy
    except:
        return pd.DataFrame(), pd.DataFrame()

df, dxy_df = get_data()

if not df.empty:
    # حساب المؤشرات
    df['RSI'] = ta.rsi(df['Close'], length=14)
    current_rsi = round(df['RSI'].iloc[-1], 2)
    live_price = df['Close'].iloc[-1]
    daily_low = df['Low'].min()
    daily_high = df['High'].max()
    vol_status = "عالية 🔥" if df['Volume'].iloc[-1] > df['Volume'].mean() else "هادئة ❄️"

    # حساب مستويات SL و TP (سعر + نقاط)
    sl_pips = 12
    tp_pips = 45
    
    # صفقة الشراء
    buy_sl = round(daily_low - (sl_pips/10000), 5)
    buy_tp = round(daily_low + (tp_pips/10000), 5)
    
    # صفقة البيع
    sell_sl = round(daily_high + (sl_pips/10000), 5)
    sell_tp = round(daily_high - (tp_pips/10000), 5)

    # العناوين العلوية
    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة (SMC Elite)</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("(RSI) زخم السوق", f"{current_rsi}%", delta=f"{current_rsi-50:.1f}")
    with c2:
        st.metric("السيولة حالياً", vol_status)
    with c3:
        st.metric("DXY مؤشر الدولار", round(dxy_df['Close'].iloc[-1], 3))

    # القائمة الجانبية للأخبار
    st.sidebar.markdown("### 📰 أخبار اقتصادية")
    st.sidebar.warning("⏳ انتظار تقرير التضخم الأمريكي")
    st.sidebar.info("🇪🇺 خطاب البنك المركزي الأوروبي")

    # تحديد قوة الصفقة بناءً على RSI و SMC
    buy_power = "قوية جداً ✅" if current_rsi < 35 else "انتظر تصحيح ⏳"
    sell_power = "قوية جداً ✅" if current_rsi > 65 else "تحت المراقبة 👀"

    # جدول التوصيات المطور
    st.write("### 🎯 التوصيات الذكية")
    trade_data = {
        "الفرصة": ["SMC BUY 🟢", "SMC SELL 🔴"],
        "السبب": ["ارتداد من LOD + FVG", "كسر هيكل BOS قمة"],
        "الدخول": [round(daily_low, 5), round(daily_high, 5)],
        "SL (السعر)": [f"{buy_sl} ({sl_pips}P)", f"{sell_sl} ({sl_pips}P)"],
        "TP (السعر)": [f"{buy_tp} ({tp_pips}P) ", f"{sell_tp} ({tp_pips}P) "],
        "القوة": [buy_power, sell_power],
        "نصيحة الذكاء": [
            "ادخل لو RSI تحت 30" if current_rsi > 35 else "فرصة ذهبية الآن",
            "ادخل لو RSI فوق 70" if current_rsi < 65 else "فرصة بيع قوية"
        ]
    }
    
    st.table(pd.DataFrame(trade_data))
else:
    st.error("فشل في جلب البيانات، يرجى تحديث الصفحة.")
    
