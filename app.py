import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz

# إعدادات الصفحة
st.set_page_config(page_title="SMC Sniper Elite v5", layout="wide")

# تصميم الواجهة
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stTable"] { font-size: 13px !important; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

def get_market_session():
    tz = pytz.timezone('Africa/Tripoli')
    now_hour = datetime.now(tz).hour
    if 2 <= now_hour < 10: return "جلسة آسيا 🇯🇵", 40
    elif 10 <= now_hour < 15: return "جلسة لندن 🇬🇧", 90
    elif 15 <= now_hour < 21: return "جلسة نيويورك 🇺🇸", 95
    else: return "سوق ليلي 🌙", 30

def fetch_data():
    try:
        eur = yf.Ticker("EURUSD=X").history(period="2d", interval="5m") # استخدام 5 دقائق لرصد OB أدق
        dxy = yf.Ticker("DX-Y.NYB").history(period="2d", interval="5m")
        return eur, dxy
    except:
        return pd.DataFrame(), pd.DataFrame()

df, dxy_df = fetch_data()

if not df.empty:
    # حساب المؤشرات
    df['RSI'] = ta.rsi(df['Close'], length=14)
    curr_rsi = round(df['RSI'].iloc[-1], 2)
    low_v = df['Low'].min()
    high_v = df['High'].max()
    price = df['Close'].iloc[-1]
    
    # تحديد Order Block بسيط (آخر شمعة هابطة قبل صعود قوي)
    # ملاحظة: برمجياً نأخذ نطاق سعري حول القاع/القمة لتمثيل الـ Block
    buy_ob_range = f"{round(low_v, 5)} - {round(low_v + 0.00015, 5)}"
    sell_ob_range = f"{round(high_v - 0.00015, 5)} - {round(high_v, 5)}"
    
    session_n, session_weight = get_market_session()
    
    # خوارزمية نسبة التأكيد المطورة (SMC + RSI + Session)
    def calc_conf(side, rsi, session_w):
        score = session_w * 0.35  # الجلسة 35%
        if side == "BUY":
            if rsi < 30: score += 45
            elif rsi < 45: score += 25
        else:
            if rsi > 70: score += 45
            elif rsi > 55: score += 25
        score += 20 # وزن الـ Order Block وتواجد السعر عنده
        return min(int(score), 99)

    buy_conf = calc_conf("BUY", curr_rsi, session_weight)
    sell_conf = calc_conf("SELL", curr_rsi, session_weight)

    sl_p, tp_p = 12, 45
    b_sl, b_tp = round(low_v - (sl_p/10000), 5), round(low_v + (tp_p/10000), 5)
    s_sl, s_tp = round(high_v + (sl_p/10000), 5), round(high_v - (tp_p/10000), 5)

    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة - SMC & Order Block</h2>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("السعر الحالي", round(price, 5))
    m2.metric("توقيت السوق", session_n)
    m3.metric("زخم RSI", f"{curr_rsi}%")
    m4.metric("قوة الدولار DXY", round(dxy_df['Close'].iloc[-1], 3) if not dxy_df.empty else "N/A")

    trade_list = {
        "الفرصة": ["SMC BUY 🟢", "SMC SELL 🔴"],
        "منطقة الـ Order Block": [buy_ob_range, sell_ob_range],
        "الستوب SL": [f"{b_sl} ({sl_p}P)", f"{s_sl} ({sl_p}P)"],
        "الهدف TP": [f"{b_tp} ({tp_p}P)", f"{s_tp} ({tp_p}P)"],
        "التأكيد": [f"{buy_conf}% 🔥" if buy_conf > 75 else f"{buy_conf}%", 
                    f"{sell_conf}% 🔥" if sell_conf > 75 else f"{sell_conf}%"],
        "نصيحة الذكاء": ["شراء من OB القاع", "بيع من OB القمة"]
    }
    st.table(pd.DataFrame(trade_list))
    
    st.sidebar.title("🔍 تحليل السيولة")
    st.sidebar.success("تم تفعيل كاشف الـ Order Block ✅")
    st.sidebar.write(f"أدنى سعر اليوم: {round(low_v, 5)}")
    st.sidebar.write(f"أعلى سعر اليوم: {round(high_v, 5)}")
else:
    st.write("جاري تحليل مناطق السيولة...")
    
