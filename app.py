import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz

# إعدادات الصفحة
st.set_page_config(page_title="SMC Sniper Elite", layout="wide")

# تصميم الواجهة
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stTable"] { font-size: 14px !important; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

def get_market_session():
    # توقيت طرابلس/ليبيا
    tz = pytz.timezone('Africa/Tripoli')
    now = datetime.now(tz).hour
    
    if 2 <= now < 10: return "جلسة آسيا 🇯🇵 (هادئة)"
    elif 10 <= now < 15: return "جلسة لندن 🇬🇧 (سيولة عالية)"
    elif 15 <= now < 21: return "جلسة نيويورك 🇺🇸 (انفجار سعري)"
    else: return "سوق ليلي 🌙 (تذبذب)"

def get_data():
    try:
        eur_data = yf.Ticker("EURUSD=X").history(period="2d", interval="1m")
        dxy_data = yf.Ticker("DX-Y.NYB").history(period="2d", interval="1m")
        return eur_data, dxy_data
    except:
        return pd.DataFrame(), pd.DataFrame()

df, dxy_df = get_data()

if not df.empty:
    # حساب المؤشرات
    df['RSI'] = ta.rsi(df['Close'], length=14)
    current_rsi = round(df['RSI'].iloc[-1], 2)
    daily_low = df['Low'].min()
    daily_high = df['High'].max()
    live_price = df['Close'].iloc[-1]
    
    # الجلسة الحالية
    session = get_market_session()
    
    # حساب SL و TP (سعر + نقاط)
    sl_p, tp_p = 12, 45
    b_sl = round(daily_low - (sl_p/10000), 5)
    b_tp = round(daily_low + (tp_p/10000), 5)
    s_sl = round(daily_high + (sl_p/10000), 5)
    s_tp = round(daily_high - (tp_p/10000), 5)

    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة SMC</h2>", unsafe_allow_html=True)
    
    # عرض المؤشرات في أعمدة
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("السعر الحالي", round(live_price, 5))
    c2.metric("الجلسة الحالية", session)
    c3.metric("زخم RSI", f"{current_rsi}%")
    c4.metric("DXY", round(dxy_df['Close'].iloc[-1], 3) if not dxy_df.empty else "N/A")

    # تحديد القوة
    status = "قوية جداً ✅" if (current_rsi < 35 or current_rsi > 65) else "ضعيفة (تذبذب) ⚠️"

    # جدول التوصيات مع الأسعار والنقاط
    data = {
        "الفرصة": ["SMC BUY 🟢", "SMC SELL 🔴"],
        "الدخول": [f"{round(daily_low, 5)}", f"{round(daily_high, 5)}"],
        "الستوب SL": [f"{b_sl} ({sl_p}P)", f"{s_sl} ({sl_p}P)"],
        "الهدف TP": [f"{b_tp} ({tp_p}P)", f"{s_tp} ({tp_p}P)"],
        "القوة": [status, "مراقبة 👀"],
        "نصيحة الذكاء": ["انتظر تأكيد RSI 30", "انتظر تأكيد RSI 70"]
    }
    
    st.table(pd.DataFrame(data))
    
    st.sidebar.title("📰 أخبار العملة")
    st.sidebar.info("تأكد من مطابقة الجلسة مع السيولة قبل الدخول.")
else:
    st.error("جاري جلب البيانات من السيرفر، يرجى الانتظار...")
    
