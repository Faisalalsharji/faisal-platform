import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
import time

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75
UPDATE_INTERVAL = 5  # تحديث كل 5 ثواني

HALAL_STOCKS = ["AAPL", "MSFT", "GOOG", "NVDA", "TSLA", "AMZN", "META", "ADBE", "CRM", "INTC"]

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="wide")

def login():
    st.title("تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD:
            st.success("تم تسجيل الدخول بنجاح")
            return True
        else:
            st.error("بيانات الدخول غير صحيحة")
    return False

def fetch_stock_data(ticker):
    data = yf.download(ticker, period="7d", interval="1h")
    return data

def calculate_macd(df):
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def calculate_rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def ai_recommendation(df):
    macd, signal = calculate_macd(df)
    rsi = calculate_rsi(df)
    latest_macd = macd.iloc[-1]
    latest_signal = signal.iloc[-1]
    latest_rsi = rsi.iloc[-1]

    price = df["Close"].iloc[-1]
    target_price = round(price * 1.05, 2)

    if latest_macd > latest_signal and latest_rsi < 70:
        return "دخول قوي", f"السعر المستهدف: {target_price} USD", "السبب: MACD إيجابي و RSI أقل من 70"
    elif latest_rsi > 70:
        return "خروج", f"السعر الحالي مرتفع: {price} USD", "السبب: RSI مرتفع جدًا"
    else:
        return "انتظار", f"السعر الحالي: {price} USD", "السبب: لا توجد إشارات واضحة"

if login():
    search = st.text_input("ابحث عن السهم (مثل AAPL):")
    st.write(f"تحديث كل {UPDATE_INTERVAL} ثوانٍ...")

    if search:
        stock_symbol = search.upper()
        if stock_symbol in HALAL_STOCKS:
            data_load_state = st.text("جاري تحميل البيانات...")
            data = fetch_stock_data(stock_symbol)
            data_load_state.text("")

            if not data.empty:
                st.subheader(f"{stock_symbol} بيانات السهم")
                price = data["Close"].iloc[-1]
                st.metric(label="السعر الحالي", value=f"{price:.2f} USD", delta=f"{price * USD_TO_SAR:.2f} SAR")

                reco, target, reason = ai_recommendation(data)
                st.success(f"التوصية: {reco}")
                st.info(target)
                st.caption(reason)
            else:
                st.warning("لا توجد بيانات حالياً لهذا السهم.")
        else:
            st.error("السهم غير موجود في قائمة الأسهم الحلال.")

    time.sleep(UPDATE_INTERVAL)
    st.experimental_rerun()
