import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz
import requests

# --- إعدادات التليجرام الخاصة بك ---
TELEGRAM_TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
TELEGRAM_CHAT_ID = "8541033784"

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    except:
        pass

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SMC Sniper Elite v6", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stTable"] { font-size: 13px !important; background-color: #161b22; }
    .stMetric { background-color: #1c2128; border: 1px solid #30363d; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- الدوال المساعدة ---
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

# --- القائمة الجانبية (الأخبار + الاختبار) ---
st.sidebar.title("🛠️ أدوات التحكم")
if st.sidebar.button("🚀 إرسال رسالة اختبار"):
    send_telegram_alert("🌟 مرحبا بك يا صديقي! رادار القناص متصل الآن بهاتفك بنجاح. صيداً موفقاً!")
    st.sidebar.success("وصلت الرسالة؟ تفقد هاتفك! ✅")

st.sidebar.markdown("---")
st.sidebar.title("📰 رادار الأخبار")
st.sidebar.warning("⚠️ ترقب تقارير التضخم")
st.sidebar.info("🇪🇺 خطاب البنك المركزي الأوروبي")

# --- معالجة البيانات ---
df, dxy_df = fetch_data()

if not df.empty:
    df['RSI'] = ta.rsi(df['Close'], length=14)
    curr_rsi = round(df['RSI'].iloc[-1], 2)
    low_v = df['Low'].min()
    high_v = df['High'].max()
    price = round(df['Close'].iloc[-1], 5)
    
    session_n, session_weight = get_market_session()
    
    # حساب نسبة التأكيد
    def calc_conf(side, rsi, session_w):
        score = session_w * 0.35
        if side == "BUY":
            score += (45 if rsi < 35 else 20 if rsi < 45 else 0)
        else:
            score += (45 if rsi > 65 else 20 if rsi > 55 else 0)
        score += 20
        return min(int(score), 99)

    b_conf = calc_conf("BUY", curr_rsi, session_weight)
    s_conf = calc_conf("SELL", curr_rsi, session_weight)

    # مستويات الصفقة
    sl_p, tp_p = 12, 45
    b_sl, b_tp = round(low_v - (sl_p/10000), 5), round(low_v + (tp_p/10000), 5)
    s_sl, s_tp = round(high_v + (sl_p/10000), 5), round(high_v - (tp_p/10000), 5)

    # إرسال تلقائي إذا كانت النسبة قوية (أكثر من 80%)
    if 'alert_sent' not in st.session_state: st.session_state.alert_sent = None
    if (b_conf >= 80 or s_conf >= 80) and st.session_state.alert_sent != session_n:
        msg = f"🎯 *فرصة قناص مؤكدة!*\n\n🔹 النوع: {'BUY' if b_conf >= 80 else 'SELL'}\n🔹 الدخول: {price}\n🔹 الهدف: {b_tp if b_conf >= 80 else s_tp}\n🔥 التأكيد: {max(b_conf, s_conf)}%"
        send_telegram_alert(msg)
        st.session_state.alert_sent = session_n

    # عرض الواجهة
    st.markdown("<h2 style='text-align: center; color: #00FFCC;'>💎 رادار النخبة - النسخة المتكاملة</h2>", unsafe_allow_html=True)
    
    cols = st.columns(4)
    cols[0].metric("السعر الحالي", price)
    cols[1].metric("الجلسة", session_n)
    cols[2].metric("زخم RSI", f"{curr_rsi}%")
    cols[3].metric("DXY", round(dxy_df['Close'].iloc[-1], 3) if not dxy_df.empty else "N/A")

    trade_data = {
        "الفرصة": ["BUY 🟢", "SELL 🔴"],
        "منطقة Order Block": [f"{round(low_v, 5)} - {round(low_v+0.00012, 5)}", f"{round(high_v-0.00012, 5)} - {round(high_v, 5)}"],
        "الستوب SL": [f"{b_sl} (12P)", f"{s_sl} (12P)"],
        "الهدف TP": [f"{b_tp} (45P)", f"{s_tp} (45P)"],
        "نسبة التأكيد": [f"{b_conf}%", f"{s_conf}%"],
        "الحالة": ["قوية ✅" if b_conf > 75 else "انتظار ⏳", "مراقبة 👀"]
    }
    st.table(pd.DataFrame(trade_data))
    st.info("📍 ملاحظة: نسبة التأكيد تأخذ بعين الاعتبار قوة السيولة في الجلسة الحالية وزخم السعر عند مناطق الأوردر بلوك.")
else:
    st.error("فشل في تحديث البيانات.. يرجى التحقق من الاتصال.")
    
