import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# إعدادات الصفحة
st.set_page_config(page_title="SMC Sniper Elite", layout="wide")

# تصميم بسيط ومضمون العمل
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stTable"] { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

def get_data():
    try:
        eur_data = yf.Ticker("EURUSD=X").history(period="2d", interval="1m")
        dxy_data = yf.Ticker("DX-Y.NYB").history(period="2d", interval="1m")
        return eur_data, dxy_data
    except:
        return pd.DataFrame(), pd.DataFrame()

df, dxy_df = get_data()

if not df.empty:
    # حساب المؤشرات الأساسية
    df['RSI'] = ta.rsi(df['Close'], length=14)
    current_rsi = round(df['RSI'].iloc[-1], 2)
    daily_low = df['Low'].min()
    daily_high = df['High'].max()
    live_price = df['Close'].iloc[-1]
    
    # حساب SL و TP (سعر + نقاط)
    sl_p = 12
    tp_p = 45
    
    b_sl = round(daily_low - (sl_p/10000), 5)
    b_tp = round(daily_low + (tp_p/10000), 5)
    s_sl = round(daily_high + (sl_p/10000), 5)
    s_tp = round(daily_high - (tp_p/10000), 5)

    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة المطور</h2>", unsafe_allow_html=True)
    
    # عرض المؤشرات في أعمدة
    c1, c2, c3 = st.columns(3)
    c1.metric("السعر الحالي", round(live_price, 5))
    c2.metric("زخم السوق RSI", f"{current_rsi}%")
    c3.metric("مؤشر الدولار DXY", round(dxy_df['Close'].iloc[-1], 3) if not dxy_df.empty else "N/A")

    st.sidebar.title("📰 الأخبار")
    st.sidebar.info("انتظار بيانات التضخم ⏳")

    # تحديد الحالة بناءً على RSI
    status = "قوية ✅" if (current_rsi < 35 or current_rsi > 65) else "ضعيفة ⚠️"

    # جدول التوصيات النهائي
    data = {
        "الفرصة": ["BUY 🟢", "SELL 🔴"],
        "الدخول": [f"{round(daily_low, 5)}", f"{round(daily_high, 5)}"],
        "الستوب SL": [f"{b_sl} ({sl_p}P)", f"{s_sl} ({sl_p}P)"],
        "الهدف TP": [f"{b_tp} ({tp_p}P)", f"{s_tp} ({tp_p}P)"],
        "القوة": [status, "مراقبة 👀"]
    }
    
    st.table(pd.DataFrame(data))
else:
    st.error("يرجى الانتظار ثواني لتحديث البيانات من السيرفر...")
    
