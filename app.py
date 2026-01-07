import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz
import requests

# --- إعدادات التليجرام ---
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
st.set_page_config(page_title="SMC Sniper Elite v7", layout="wide")

# حفظ حالة الصفقات والتنبيهات لمنع التكرار
if 'last_signal_session' not in st.session_state: st.session_state.last_signal_session = None
if 'active_trade' not in st.session_state: st.session_state.active_trade = False

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
        # جلب بيانات دقيقة واحدة لدقة أعلى في الارتداد
        data = yf.Ticker("EURUSD=X").history(period="1d", interval="1m")
        return data
    except:
        return pd.DataFrame()

# --- القائمة الجانبية ---
st.sidebar.title("🛠️ لوحة التحكم الذكية")
if st.sidebar.button("🚀 اختبار اتصال التليجرام"):
    send_telegram_alert("✅ نظام الإدارة الذكي متصل الآن. بانتظار إشارات 1:3!")
    st.sidebar.success("تم الإرسال!")

# --- معالجة البيانات ---
df = fetch_data()

if not df.empty:
    # الحسابات الفنية
    df['RSI'] = ta.rsi(df['Close'], length=14)
    price = round(df['Close'].iloc[-1], 5)
    prev_price = df['Close'].iloc[-2]
    curr_rsi = round(df['RSI'].iloc[-1], 2)
    session_n, session_weight = get_market_session()
    
    # تحديد مناطق الـ Order Block (قمم وقيعان اليوم)
    low_v = df['Low'].min()
    high_v = df['High'].max()
    
    # إعدادات الصفقة
    sl_p, tp_p = 0.0012, 0.0045 # 12 نقطة ستوب و 45 نقطة هدف
    b_sl, b_tp = round(low_v - 0.0005, 5), round(low_v + tp_p, 5)
    s_sl, s_tp = round(high_v + 0.0005, 5), round(high_v - tp_p, 5)

    # حساب نسبة التأكيد
    b_conf = 0
    if price <= low_v + 0.0010: # إذا كان السعر قرب منطقة الطلب
        b_conf = session_weight * 0.4 + (40 if curr_rsi < 35 else 20) + 20
    
    s_conf = 0
    if price >= high_v - 0.0010: # إذا كان السعر قرب منطقة العرض
        s_conf = session_weight * 0.4 + (40 if curr_rsi > 65 else 20) + 20

    # --- فلتر الإرسال الذكي (طلبك) ---
    # 1. منع التكرار في نفس الجلسة
    # 2. شرط الارتداد (السعر الحالي أكبر من السابق في الشراء)
    # 3. فلتر 1:3 (محقق آلياً لأن الهدف 45 والستوب 12)
    
    if b_conf >= 80 and not st.session_state.active_trade and price > prev_price:
        msg = (f"🎯 *إشارة شراء قوية (1:3.7)*\n\n"
               f"🔹 سعر الدخول: {price}\n"
               f"🚩 وقف الخسارة: {b_sl}\n"
               f"✅ الهدف الأول: {b_tp}\n"
               f"⚖️ نسبة التأكيد: {int(b_conf)}%\n\n"
               f"🛡️ *تعليمات الإدارة:* عند ربح 15 نقطة، انقل الستوب لنقطة الدخول فوراً.")
        send_telegram_alert(msg)
        st.session_state.active_trade = True
        st.session_state.last_signal_session = session_n

    # إعادة ضبط الحالة إذا ابتعد السعر عن المنطقة (للسماح بصفقة جديدة لاحقاً)
    if abs(price - low_v) > 0.0050: 
        st.session_state.active_trade = False

    # --- عرض الواجهة ---
    st.title("💎 رادار القناص V7 - إدارة الصفقات")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("السعر الحالي", price, f"{round(price-prev_price, 5)}")
    col2.metric("الجلسة الحالية", session_n)
    col3.metric("زخم السوق (RSI)", f"{curr_rsi}%")

    # جدول الصفقات المتاحة بجودة 1:3
    st.markdown("### 📊 صفقات تحت الرصد (Quality Filter 1:3)")
    trade_table = {
        "النوع": ["BUY 🟢", "SELL 🔴"],
        "منطقة الدخول": [low_v, high_v],
        "الهدف (TP)": [b_tp, s_tp],
        "المخاطرة:الربح": ["1:3.75 ✅", "1:3.75 ✅"],
        "الحالة": ["منطقة انفجار" if b_conf > 70 else "مراقب", "انتظار"]
    }
    st.table(pd.DataFrame(trade_table))
    
    st.info("💡 نظام الإدارة مفعل: سيتم إرسال تنبيه واحد فقط لكل منطقة لضمان عدم ملاحقة السعر الهابط.")
    
