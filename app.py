import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعدادات الصفحة
st.set_page_config(page_title="SMC Sniper Elite", layout="wide")

# تصميم الواجهة وتصغير الخطوط
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stTable"] { font-size: 11px !important; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 5px; }
    </style>
    """, unsafe_allow_True=True)

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
    daily_low = df['Low'].min()
    daily_high = df['High'].max()
    vol_status = "عالية 🔥" if df['Volume'].iloc[-1] > df['Volume'].mean() else "هادئة ❄️"

    # حساب مستويات SL و TP كأرقام واضحة
    sl_pips = 12
    tp_pips = 45
    
    # تحويل النقاط إلى سعر
    b_sl = round(daily_low - (sl_pips/10000), 5)
    b_tp = round(daily_low + (tp_pips/10000), 5)
    s_sl = round(daily_high + (sl_pips/10000), 5)
    s_tp = round(daily_high - (tp_pips/10000), 5)

    st.markdown("<h3 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة المطور</h3>", unsafe_allow_html=True)
    
    # عرض المؤشرات
    col1, col2, col3 = st.columns(3)
    col1.metric("زخم RSI", f"{current_rsi}%")
    col2.metric("حالة السيولة", vol_status)
    col3.metric("مؤشر DXY", round(dxy_df['Close'].iloc[-1], 3))

    # القائمة الجانبية للأخبار
    st.sidebar.markdown("### 📰 مفكرة الأخبار")
    st.sidebar.info("انتظار بيانات التضخم ⏳")

    # تحديد القوة
    pwr = "قوية ✅" if (current_rsi < 35 or current_rsi > 65) else "ضعيفة ⚠️"

    # إنشاء الجدول ببيانات نصية واضحة جداً
    trade_data = {
        "الفرصة": ["SMC BUY 🟢", "SMC SELL 🔴"],
        "الدخول": [f"{round(daily_low, 5)}", f"{round(daily_high, 5)}"],
        "وقف الخسارة SL": [f"{b_sl} ({sl_pips}P)", f"{s_sl} ({sl_pips}P)"],
        "الهدف TP": [f"{b_tp} ({tp_pips}P)", f"{s_tp} ({tp_pips}P)"],
        "الحالة": [pwr, "مراقبة"],
        "نصيحة": ["انتظر RSI 30", "انتظر RSI 70"]
    }
    
    st.table(pd.DataFrame(trade_data))
    
