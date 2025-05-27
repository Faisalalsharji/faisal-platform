import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="wide")

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75

WATCHLIST = ["AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN"]

def login():
    st.title("تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

def get_analysis(symbol):
    df = yf.Ticker(symbol).history(period="1mo")
    if df.empty or "Close" not in df:
        return None

    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]

    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = -delta.where(delta < 0, 0).rolling(14).mean()
    RS = gain / loss
    df["RSI"] = 100 - (100 / (1 + RS))

    latest = df.iloc[-1]
    price = latest["Close"]
    macd = latest["MACD"]
    rsi = latest["RSI"]
    ma20 = latest["MA20"]

    if rsi < 30 and macd > 0 and price > ma20:
        signal = "شراء قوي"
    elif rsi > 70 and macd < 0:
        signal = "بيع"
    else:
        signal = "انتظار"

    return {
        "price": price,
        "macd": macd,
        "rsi": rsi,
        "ma20": ma20,
        "signal": signal
    }

def display_card(symbol):
    data = get_analysis(symbol)
    if data is None:
        st.warning(f"{symbol} - تعذر تحميل البيانات")
        return

    sar_price = data["price"] * USD_TO_SAR
    change = f"{data['rsi']:.2f}"  # Just to display something for testing

    st.markdown(f"""
        <div style='background:#1f1f1f;padding:20px;border-radius:16px;margin-bottom:15px;border:1px solid #444'>
            <h3 style='color:#fff'>{symbol}</h3>
            <p style='color:#ccc'>السعر: {data['price']:.2f} $ ({sar_price:.2f} ريال)</p>
            <p style='color:#ccc'>RSI: {data['rsi']:.2f} | MACD: {data['macd']:.2f} | MA20: {data['ma20']:.2f}</p>
            <p style='color:#0f0;font-weight:bold'>توصية الذكاء الصناعي: {data['signal']}</p>
        </div>
    """, unsafe_allow_html=True)

def show_portfolio():
    st.subheader("صفحة المحفظة")
    st.info("هذه ميزة مستقبلية، سيتم عرض الأرباح والخسائر هنا بناءً على الصفقات.")

def main():
    st.markdown("<h1 style='text-align:center; color:gold;'>منصة فيصل - الأسهم الذكية</h1>", unsafe_allow_html=True)
    page = st.sidebar.radio("انتقل إلى:", ["الأسهم", "المحفظة"])

    if st.sidebar.button("تحديث يدوي"):
        st.experimental_rerun()

    if page == "الأسهم":
        st.subheader("الفرص الاستثمارية")
        stocks_ranked = []
        for symbol in WATCHLIST:
            data = get_analysis(symbol)
            score = 1 if data and data["signal"] == "شراء قوي" else 0
            stocks_ranked.append((symbol, score))

        sorted_symbols = [s[0] for s in sorted(stocks_ranked, key=lambda x: x[1], reverse=True)]

        for symbol in sorted_symbols:
            display_card(symbol)

    elif page == "المحفظة":
        show_portfolio()

main()
