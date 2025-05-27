import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import requests
from datetime import datetime

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="wide")

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75

WATCHLIST_FILE = "watchlist.csv"
PORTFOLIO_FILE = "portfolio.csv"
TRADES_FILE = "trades.csv"
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

HALAL_STOCKS = ["AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN", "META", "ADBE", "INTC", "CRM"]

for file in [WATCHLIST_FILE, PORTFOLIO_FILE, TRADES_FILE]:
    if not os.path.exists(file):
        pd.DataFrame(columns=["Symbol"]).to_csv(file, index=False)

def get_stock_data(symbol):
    data = yf.Ticker(symbol)
    df = data.history(period="1mo")
    return df, data.info

def ai_analysis(df):
    df["EMA12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = df["EMA12"] - df["EMA26"]
    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    RS = gain / loss
    df["RSI"] = 100 - (100 / (1 + RS))
    latest_rsi = df["RSI"].iloc[-1]
    latest_macd = df["MACD"].iloc[-1]
    recommendation = "شراء" if latest_rsi < 30 and latest_macd > 0 else "انتظار"
    return latest_rsi, latest_macd, recommendation

def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.get(url, params=params)
    except:
        pass

def login():
    st.title("تسجيل الدخول - منصة فيصل")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
        else:
            st.error("بيانات الدخول غير صحيحة")

def display_stock_card(symbol):
    try:
        df, info = get_stock_data(symbol)
        current_price = df["Close"].iloc[-1]
        price_change = ((df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2]) * 100
        rsi, macd, ai_signal = ai_analysis(df)

        st.markdown(f"""
        <div class='stock-card'>
            <h4>{info['shortName']} ({symbol})</h4>
            <p>السعر: {current_price:.2f} $ ({current_price * USD_TO_SAR:.2f} ريال)</p>
            <p>نسبة التغير: {price_change:.2f}%</p>
            <p>RSI: {rsi:.2f} | MACD: {macd:.2f}</p>
            <p><strong>توصية AI: {ai_signal}</strong></p>
        </div>
        """, unsafe_allow_html=True)

        if ai_signal == "شراء":
            send_telegram_alert(f"فرصة شراء في {symbol} - السعر الحالي: {current_price:.2f} $")

        cols = st.columns([1, 1])
        if cols[0].button(f"حذف {symbol}", key=f"delete_{symbol}"):
            remove_from_watchlist(symbol)
        if cols[1].button(f"إضافة {symbol} للمحفظة", key=f"add_{symbol}"):
            add_to_portfolio(symbol, current_price)

    except Exception as e:
        st.warning(f"تعذر تحميل {symbol}: {e}")

st.markdown("""
<style>
    .stock-card {
        background-color: #1e1e1e;
        color: white;
        padding: 16px;
        border-radius: 20px;
        border: 1px solid #333;
        margin-bottom: 16px;
        transition: 0.3s ease;
    }
    .stock-card:hover {
        border: 1px solid gold;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

def load_watchlist():
    return pd.read_csv(WATCHLIST_FILE)["Symbol"].tolist()

def save_watchlist(symbols):
    pd.DataFrame(symbols, columns=["Symbol"]).to_csv(WATCHLIST_FILE, index=False)

def remove_from_watchlist(symbol):
    symbols = load_watchlist()
    if symbol in symbols:
        symbols.remove(symbol)
        save_watchlist(symbols)
        st.success(f"تم حذف {symbol}")

def add_to_portfolio(symbol, price):
    df = pd.read_csv(PORTFOLIO_FILE)
    df = df.append({"Symbol": symbol, "BuyPrice": price, "Date": datetime.now().strftime("%Y-%m-%d")}, ignore_index=True)
    df.to_csv(PORTFOLIO_FILE, index=False)
    st.success(f"تمت إضافة {symbol} إلى المحفظة")

def portfolio_summary():
    st.title("المحفظة")
    if not os.path.exists(PORTFOLIO_FILE):
        st.info("لا توجد بيانات.")
        return

    df = pd.read_csv(PORTFOLIO_FILE)
    if df.empty:
        st.info("لا توجد بيانات.")
        return

    total_profit = 0
    for i, row in df.iterrows():
        symbol = row["Symbol"]
        buy_price = row["BuyPrice"]
        current_price = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
        profit = current_price - buy_price
        total_profit += profit
        st.write(f"{symbol}: اشتريت بـ {buy_price}, السعر الآن {current_price:.2f}, الربح: {profit:.2f}")

    st.success(f"الربح الإجمالي: {total_profit:.2f} $")

def main_app():
    page = st.sidebar.selectbox("انتقل إلى", ["قائمة المراقبة", "المحفظة"])
    if page == "قائمة المراقبة":
        st.title("قائمة المراقبة")
        watchlist = load_watchlist()
        if st.button("تحديث يدوي"):
            st.experimental_rerun()
        for symbol in watchlist:
            display_stock_card(symbol)
    elif page == "المحفظة":
        portfolio_summary()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
