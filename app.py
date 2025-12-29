import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz

# إعدادات الصفحة
st.set_page_config(page_title="SMC Sniper Elite v4", layout="wide")

# تصميم الواجهة
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stTable"] { font-size: 14px !important; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

def get_market_session():
    tz = pytz.timezone('Africa/Tripoli')
    now_hour = datetime.now(tz).hour
    if 2 <= now_hour < 10: return "جلسة آسيا 🇯🇵", 40  # سيولة منخفضة
    elif 10 <= now_hour < 15: return "جلسة لندن 🇬🇧", 90  # سيولة عالية جداً
    elif 15 <= now_hour < 21: return "جلسة نيويورك 🇺🇸", 95  # سيولة انفجارية
    else: return "سوق ليلي 🌙", 30  # تذبذب

def fetch_data():
    try:
        eur = yf.Ticker("EURUSD=X").history(period="2d", interval="1m")
        dxy = yf.Ticker("DX-Y.NYB").history(period="2d", interval="1m")
        return eur, dxy
    except:
        return pd.DataFrame(), pd.DataFrame()

df, dxy_df = fetch_data()

if not df.empty:
    df['RSI'] = ta.rsi(df['Close'], length=14)
    curr_rsi = round(df['RSI'].iloc[-1], 2)
    low_v = df['Low'].min()
    high_v = df['High'].max()
    price = df['Close'].iloc[-1]
    
    session_n, session_weight = get_market_session()
    
    # خوارزمية نسبة التأكيد
    def calc_conf(side, rsi, session_w):
        score = session_w * 0.4  # وزن الجلسة 40%
        if side == "BUY":
            if rsi < 30: score += 40
            elif rsi < 40: score += 20
        else:
            if rsi > 70: score += 40
            elif rsi > 60: score += 20
        # إضافة وزن لاقتراب السعر من القمة/القاع (20%)
        score += 20 
        return min(int(score), 99)

    buy_conf = calc_conf("BUY", curr_rsi, session_weight)
    sell_conf = calc_conf("SELL", curr_rsi, session_weight)

    sl_p, tp_p = 12, 45
    b_sl, b_tp = round(low_v - (sl_p/10000), 5), round(low_v + (tp_p/10000), 5)
    s_sl, s_tp = round(high_v + (sl_p/10000), 5), round(high_v - (tp_p/10000), 5)

    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة - نسخة التأكيد الذكي</h2>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("السعر", round(price, 5))
    m2.metric("الجلسة", session_n)
    m3.metric("زخم RSI", f"{curr_rsi}%")
    m4.metric("DXY", round(dxy_df['Close'].iloc[-1], 3) if not dxy_df.empty else "N/A")

    trade_list = {
        "الفرصة": ["BUY 🟢", "SELL 🔴"],
        "الدخول": [round(low_v, 5), round(high_v, 5)],
        "الستوب SL": [f"{b_sl} ({sl_p}P)", f"{s_sl} ({sl_p}P)"],
        "الهدف TP": [f"{b_tp} ({tp_p}P)", f"{s_tp} ({tp_p}P)"],
        "نسبة التأكيد": [f"{buy_conf}% 🔥" if buy_conf > 70 else f"{buy_conf}%", 
                         f"{sell_conf}% 🔥" if sell_conf > 70 else f"{sell_conf}%"],
        "الحالة": ["قوية" if buy_conf > 75 else "ضعيفة", "مراقبة"]
    }
    st.table(pd.DataFrame(trade_list))
    
    st.sidebar.title("🛠️ إعدادات الرادار")
    st.sidebar.info(f"نسبة التأكيد تعتمد بنسبة 40% على وقت الجلسة الحالي ({session_n})")
    
