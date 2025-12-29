import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz

# إعدادات الصفحة
st.set_page_config(page_title="SMC Sniper Elite v6", layout="wide")

# تصميم الواجهة الاحترافي
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stTable"] { font-size: 13px !important; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
    .stSidebar { background-color: #161b22; }
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
        eur = yf.Ticker("EURUSD=X").history(period="2d", interval="5m")
        dxy = yf.Ticker("DX-Y.NYB").history(period="2d", interval="5m")
        return eur, dxy
    except:
        return pd.DataFrame(), pd.DataFrame()

df, dxy_df = fetch_data()

# --- القائمة الجانبية (الأخبار الاقتصادية) ---
st.sidebar.title("📰 رادار الأخبار الهامة")
st.sidebar.warning("⚠️ انتظار تقرير التضخم الأمريكي (CPI)")
st.sidebar.info("🇪🇺 خطاب رئيس البنك المركزي الأوروبي")
st.sidebar.markdown("---")
st.sidebar.write("💡 نصيحة اليوم: تجنب التداول قبل الخبر بـ 30 دقيقة.")

if not df.empty:
    # حسابات فنية
    df['RSI'] = ta.rsi(df['Close'], length=14)
    curr_rsi = round(df['RSI'].iloc[-1], 2)
    low_v = df['Low'].min()
    high_v = df['High'].max()
    price = df['Close'].iloc[-1]
    
    # تحديد نطاق الأوردر بلوك
    buy_ob = f"{round(low_v, 5)} - {round(low_v + 0.00012, 5)}"
    sell_ob = f"{round(high_v - 0.00012, 5)} - {round(high_v, 5)}"
    
    session_n, session_weight = get_market_session()
    
    # خوارزمية التأكيد
    def calc_conf(side, rsi, session_w):
        score = session_w * 0.35
        if side == "BUY":
            if rsi < 30: score += 45
            elif rsi < 45: score += 20
        else:
            if rsi > 70: score += 45
            elif rsi > 55: score += 20
        score += 20 
        return min(int(score), 99)

    b_conf = calc_conf("BUY", curr_rsi, session_weight)
    s_conf = calc_conf("SELL", curr_rsi, session_weight)

    # حساب SL و TP
    sl_p, tp_p = 12, 45
    b_sl, b_tp = round(low_v - (sl_p/10000), 5), round(low_v + (tp_p/10000), 5)
    s_sl, s_tp = round(high_v + (sl_p/10000), 5), round(high_v - (tp_p/10000), 5)

    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة المتكامل</h2>", unsafe_allow_html=True)
    
    # عرض المؤشرات
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("السعر الحالي", round(price, 5))
    m2.metric("الجلسة الحالية", session_n)
    m3.metric("زخم RSI", f"{curr_rsi}%")
    m4.metric("DXY مؤشر الدولار", round(dxy_df['Close'].iloc[-1], 3) if not dxy_df.empty else "N/A")

    # جدول التوصيات الشامل
    trade_list = {
        "الفرصة": ["BUY 🟢", "SELL 🔴"],
        "منطقة Order Block": [buy_ob, sell_ob],
        "الستوب SL": [f"{b_sl} ({sl_p}P)", f"{s_sl} ({sl_p}P)"],
        "الهدف TP": [f"{b_tp} ({tp_p}P)", f"{s_tp} ({tp_p}P)"],
        "نسبة التأكيد": [f"{b_conf}%", f"{s_conf}%"],
        "الحالة": ["قوية ✅" if b_conf > 75 else "انتظار ⏳", "مراقبة 👀"]
    }
    st.table(pd.DataFrame(trade_list))
    
    # توضيح الأوردر بلوك
    st.info(f"📍 تم تحديد مناطق السيولة بناءً على أعلى وأقل سعر خلال الـ 24 ساعة الماضية.")
else:
    st.error("فشل في الاتصال بمزود البيانات، يرجى إعادة المحاولة.")
    
