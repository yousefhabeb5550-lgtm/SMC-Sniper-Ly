import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime
import pytz
import requests

# --- إعدادات التليجرام (تأكد من صحتها) ---
TELEGRAM_TOKEN = "8514661948:AAEBpNWf112SXZ5t5GoOCOR8-iLcwYENil4"
TELEGRAM_CHAT_ID = "8541033784"

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=data)
    except Exception as e:
        st.error(f"خطأ في إرسال التليجرام: {e}")

# --- إعدادات الصفحة ---
st.set_page_config(page_title="SMC Sniper Elite V8", layout="wide")

# حفظ حالة الصفقات لمنع التكرار
if 'active_trade' not in st.session_state: st.session_state.active_trade = False
if 'last_signal_price' not in st.session_state: st.session_state.last_signal_price = 0

# --- الأمان (طلبك: 15 نقطة ستوب) ---
STOP_LOSS_PIPS = 0.0015
TAKE_PROFIT_PIPS = 0.0045 # نسبة 1:3

def get_market_session():
    tz = pytz.timezone('Africa/Tripoli')
    now_hour = datetime.now(tz).hour
    if 2 <= now_hour < 10: return "آسيا 🇯🇵", 40
    elif 10 <= now_hour < 15: return "لندن 🇬🇧", 90
    elif 15 <= now_hour < 21: return "نيويورك 🇺🇸", 95
    else: return "سوق ليلي 🌙", 30

def fetch_data():
    try:
        # جلب بيانات دقيقة واحدة لدقة التأكيد (CHoCH)
        data = yf.Ticker("EURUSD=X").history(period="1d", interval="1m")
        return data
    except:
        return pd.DataFrame()

# --- معالجة البيانات ---
df = fetch_data()

if not df.empty:
    df['RSI'] = ta.rsi(df['Close'], length=14)
    price = round(df['Close'].iloc[-1], 5)
    prev_close = df['Close'].iloc[-2]
    curr_rsi = round(df['RSI'].iloc[-1], 2)
    session_n, session_weight = get_market_session()
    
    # تحديد مناطق الاهتمام (POI) بناءً على قمة وقاع اليوم
    low_v = df['Low'].min()
    high_v = df['High'].max()
    
    # حساب نسبة التأكيد الأولية
    b_conf = 0
    if price <= low_v + 0.0010:
        b_conf = session_weight * 0.4 + (40 if curr_rsi < 35 else 20) + 20
    
    # --- تطبيق درس الفيديو: فلتر التأكيد (CHoCH) ---
    # لن يرسل البوت إلا إذا كان السعر فوق المنطقة وبدأ بالارتداد (شمعة صاعدة)
    is_confirmed_buy = price > prev_close and price > low_v
    
    if b_conf >= 80 and not st.session_state.active_trade and is_confirmed_buy:
        entry_price = price
        sl_price = round(entry_price - STOP_LOSS_PIPS, 5)
        tp_price = round(entry_price + TAKE_PROFIT_PIPS, 5)
        
        msg = (f"🛡️ *تم رصد دخول مؤكد (V8)*\n\n"
               f"📈 النوع: BUY\n"
               f"💵 سعر الدخول: {entry_price}\n"
               f"🚩 الستوب (أمان): {sl_price}\n"
               f"✅ الهدف (1:3): {tp_price}\n\n"
               f"⚠️ *ملاحظة:* تم تفعيل فلتر التأكيد لضمان عدم الدخول أثناء الهبوط القوي.")
        
        send_telegram_alert(msg)
        st.session_state.active_trade = True
        st.session_state.last_signal_price = entry_price

    # تصفير الحالة إذا ابتعد السعر كثيراً للسماح بصفقة جديدة
    if abs(price - st.session_state.last_signal_price) > 0.0060:
        st.session_state.active_trade = False

    # --- الواجهة الرسومية ---
    st.title("💎 رادار القناص V8 | نسخة الأمان")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("السعر الحالي", price)
    col2.metric("الجلسة", session_n)
    col3.metric("قوة الارتداد (RSI)", f"{curr_rsi}%")

    st.markdown("---")
    st.subheader("🎯 حالة الرصد اللحظي")
    if b_conf > 50:
        st.warning(f"السعر يقترب من منطقة الشراء.. نسبة التأكيد الحالية: {int(b_conf)}%")
        if not is_confirmed_buy:
            st.info("🕒 بانتظار إغلاق شمعة صاعدة (تأكيد CHoCH) لإرسال التنبيه...")
    else:
        st.success("السعر في منطقة آمنة حالياً، بانتظار الوصول لمناطق السيولة.")

    # زر الاختبار في القائمة الجانبية
    if st.sidebar.button("🚀 إرسال رسالة اختبار"):
        send_telegram_alert("✅ فحص الاتصال: نظام V8 جاهز للعمل!")
        
