import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="wide")
st_autorefresh(interval=10000, limit=None, key="refresh")

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75

HALAL_LIST = ["AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN", "META"]
WATCHLIST = HALAL_LIST.copy()

def save_trade(symbol, action, price):
    with open("portfolio.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([symbol, action, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def login():
    st.title("تسجيل الدخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == USERNAME and p == PASSWORD:
            st.session_state.logged_in = True
        else:
            st.error("كلمة المرور أو اسم المستخدم غير صحيح")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

show_halal = st.sidebar.checkbox("عرض الأسهم الحلال فقط", value=True)
symbols = HALAL_LIST if show_halal else WATCHLIST

def analyze_stock(symbol):
    try:
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
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # تقييم وهمي للأخبار كمثال تجريبي
        news_score = np.random.uniform(-1, 1)

        last = df.iloc[-1]
        price = last["Close"]
        macd = last["MACD"]
        rsi = last["RSI"]
        ma20 = last["MA20"]

        if news_score > 0.3 and rsi < 30 and macd > 0 and price > ma20:
            signal = "شراء قوي"
            entry = price
            exit_price = price * 1.05
            suggestion = "أخبار إيجابية وسهم تحت تقييمه، فرصة دخول"
        elif news_score < -0.3 and rsi > 70 and macd < 0:
            signal = "بيع فوري"
            entry = price * 0.95
            exit_price = price
            suggestion = "أخبار سلبية ومؤشرات تدل على هبوط متوقع"
        else:
            signal = "مراقبة"
            entry = price * 0.97
            exit_price = price * 1.03
            suggestion = "راقب السهم حتى يتضح الاتجاه"

        return {
            "price": price,
            "macd": macd,
            "rsi": rsi,
            "ma20": ma20,
            "signal": signal,
            "entry": entry,
            "exit": exit_price,
            "suggestion": suggestion,
            "df": df
        }
    except:
        return None

portfolio = []

def display_stock(symbol):
    data = analyze_stock(symbol)
    if data is None:
        st.warning(f"{symbol}: تعذر تحميل البيانات.")
        return

    sar_price = data["price"] * USD_TO_SAR
    change_percent = (data["price"] - data["ma20"]) / data["ma20"] * 100

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
            <div style='background:#1f1f1f;padding:20px;border-radius:16px;margin-bottom:15px;border:1px solid #444'>
                <h3 style='color:#fff'>{symbol}</h3>
                <p style='color:#ccc'>السعر: {data['price']:.2f} $ ({sar_price:.2f} ريال)</p>
                <p style='color:#ccc'>RSI: {data['rsi']:.2f} | MACD: {data['macd']:.2f} | MA20: {data['ma20']:.2f}</p>
                <p style='color:#0f0'><b>توصية AI: {data['signal']}</b></p>
                <p style='color:#ff0'>اقتراح: {data['suggestion']}</p>
                <p style='color:#aaa'>أفضل دخول: {data['entry']:.2f} $ | بيع عند: {data['exit']:.2f} $</p>
            </div>
        """, unsafe_allow_html=True)

        col_buy, col_sell = st.columns(2)
        with col_buy:
            if st.button(f"شراء {symbol}"):
                portfolio.append((symbol, data["price"], "شراء"))
                save_trade(symbol, "شراء", data["price"])
                st.success(f"تم شراء {symbol} بسعر {data['price']:.2f}$")

        with col_sell:
            if st.button(f"بيع {symbol}"):
                portfolio.append((symbol, data["price"], "بيع"))
                save_trade(symbol, "بيع", data["price"])
                st.success(f"تم بيع {symbol} بسعر {data['price']:.2f}$")

    with col2:
        st.write("رسم بياني للسهم")
        fig, ax = plt.subplots()
        data["df"]["Close"].plot(ax=ax)
        ax.set_title(f"{symbol} - السعر خلال شهر")
        st.pyplot(fig)

def show_portfolio():
    st.subheader("المحفظة الحالية")
    if not portfolio:
        st.info("لا توجد صفقات حالياً.")
    else:
        for item in portfolio:
            symbol, price, action = item
            st.write(f"{action} - {symbol} بسعر {price:.2f} $")

def main():
    st.title("منصة فيصل - الأسهم الذكية")
    page = st.sidebar.selectbox("انتقل إلى:", ["الأسهم", "المحفظة"])
    sort_by = st.sidebar.selectbox("ترتيب حسب:", ["الأفضل حسب AI", "الأعلى تغيرًا", "الأرخص سعرًا"])

    if st.sidebar.button("تحديث الآن"):
        st.rerun()

    if page == "الأسهم":
        scored = []
        for symbol in symbols:
            data = analyze_stock(symbol)
            if data:
                score = 1 if data["signal"] == "شراء قوي" else 0
                scored.append((symbol, score, data["price"], data["ma20"]))

        if sort_by == "الأعلى تغيرًا":
            sorted_syms = sorted(scored, key=lambda x: (x[2] - x[3]) / x[3], reverse=True)
        elif sort_by == "الأرخص سعرًا":
            sorted_syms = sorted(scored, key=lambda x: x[2])
        else:
            sorted_syms = sorted(scored, key=lambda x: x[1], reverse=True)

        for s in sorted_syms:
            display_stock(s[0])
    else:
        show_portfolio()

main()
