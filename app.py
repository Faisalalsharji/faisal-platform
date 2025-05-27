import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import os
from datetime import datetime
import requests

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="wide")

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

WATCHLIST_FILE = "watchlist.csv"
PORTFOLIO_FILE = "portfolio.csv"
DEFAULT_STOCKS = ["AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN"]

if not os.path.exists(WATCHLIST_FILE):
    pd.DataFrame({"Symbol": DEFAULT_STOCKS}).to_csv(WATCHLIST_FILE, index=False)
if not os.path.exists(PORTFOLIO_FILE):
    pd.DataFrame(columns=["Symbol", "BuyPrice", "Date"]).to_csv(PORTFOLIO_FILE, index=False)

def get_stock_data(symbol):
    df = yf.Ticker(symbol).history(period="1mo")
    return df

def ai_analysis(df):
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    delta = df["Close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
    RS = gain / loss
    df["RSI"] = 100 - (100 / (1 + RS))
    rsi = df["RSI"].iloc[-1]
    macd = df["MACD"].iloc[-1]
    ma = df["MA20"].iloc[-1]
    price = df["Close"].iloc[-1]
    if rsi < 30 and macd > 0 and price > ma:
        return rsi, macd, ma, "شراء قوي"
    elif rsi > 70 and macd < 0:
        return rsi, macd, ma, "بيع"
    else:
        return rsi, macd, ma, "انتظار"

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
    except:
        pass

def load_watchlist():
    return pd.read_csv(WATCHLIST_FILE)["Symbol"].tolist()

def display_stock(symbol):
    df = get_stock_data(symbol)
    rsi, macd, ma, rec = ai_analysis(df)
    price = df["Close"].iloc[-1]
    change = ((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2]) * 100

    st.markdown(f"""
        <div style='background:#1f1f1f;padding:16px;border-radius:12px;border:1px solid #444;margin-bottom:10px'>
            <h4 style='color:white'>{symbol}</h4>
            <p style='color:white'>السعر: {price:.2f} $ | التغير: {change:.2f}%</p>
            <p style='color:white'>RSI: {rsi:.2f} | MACD: {macd:.2f} | MA20: {ma:.2f}</p>
            <p style='color:white'><b>توصية الذكاء الصناعي: {rec}</b></p>
        </div>
    """, unsafe_allow_html=True)

    if rec == "شراء قوي":
        send_telegram(f"فرصة شراء قوية: {symbol} بسعر {price:.2f}$")

def show_portfolio():
    st.title("المحفظة")
    df = pd.read_csv(PORTFOLIO_FILE)
    if df.empty:
        st.info("لا توجد صفقات.")
        return
    total_profit = 0
    for _, row in df.iterrows():
        current_price = yf.Ticker(row["Symbol"]).history(period="1d")["Close"].iloc[-1]
        profit = current_price - row["BuyPrice"]
        total_profit += profit
        st.write(f"{row['Symbol']}: ربح = {profit:.2f} $")
    st.success(f"إجمالي الربح: {total_profit:.2f} $")

def main_app():
    st.markdown("<h1 style='color:gold;text-align:center;'>منصة فيصل - الأسهم الذكية</h1>", unsafe_allow_html=True)
    st.image("https://i.imgur.com/lwxQfxT.png", width=80)

    page = st.sidebar.selectbox("القائمة", ["الأسهم", "المحفظة"])
    if page == "الأسهم":
        symbols = load_watchlist()
        stocks_ranked = []
        for sym in symbols:
            df = get_stock_data(sym)
            _, _, _, rec = ai_analysis(df)
            score = 1 if rec == "شراء قوي" else 0
            stocks_ranked.append((sym, score))
        sorted_symbols = [s[0] for s in sorted(stocks_ranked, key=lambda x: x[1], reverse=True)]

        for symbol in sorted_symbols:
            display_stock(symbol)
    elif page == "المحفظة":
        show_portfolio()

def login():
    st.title("تسجيل الدخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
        else:
            st.error("بيانات خاطئة")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
