
import pandas as pd
import yfinance as yf
import requests
import streamlit as st

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75
TELEGRAM_TOKEN = "ضع_توكن_البوت"
TELEGRAM_CHAT_ID = "ضع_معرف_المحادثة"

WATCHLIST_FILE = "watchlist.csv"
PORTFOLIO_FILE = "portfolio.csv"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        pass

def save_watchlist(watchlist):
    df = pd.DataFrame(watchlist, columns=["stock"])
    df.to_csv(WATCHLIST_FILE, index=False)

def load_watchlist():
    try:
        df = pd.read_csv(WATCHLIST_FILE)
        return df["stock"].tolist()
    except:
        return []

def save_portfolio(portfolio):
    df = pd.DataFrame(portfolio)
    df.to_csv(PORTFOLIO_FILE, index=False)

def load_portfolio():
    try:
        return pd.read_csv(PORTFOLIO_FILE)
    except:
        return pd.DataFrame(columns=["stock", "buy_price", "quantity"])

def login():
    st.title("تسجيل الدخول - منصة فيصل")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول")
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

def main_app():
    st.title("منصة فيصل - الأسهم الذكية")
    menu = st.sidebar.selectbox("القائمة", ["ملخص المحفظة", "قائمة المراقبة", "إرسال تنبيه"])

    if menu == "ملخص المحفظة":
        st.subheader("ملخص المحفظة")
        portfolio = load_portfolio()
        if not portfolio.empty:
            prices = []
            for symbol in portfolio["stock"]:
                data = yf.Ticker(symbol)
                prices.append(data.history(period="1d")["Close"].iloc[-1])
            portfolio["current_price"] = prices
            portfolio["gain_loss"] = (portfolio["current_price"] - portfolio["buy_price"]) * portfolio["quantity"]
            portfolio["total_value_usd"] = portfolio["current_price"] * portfolio["quantity"]
            portfolio["total_value_sar"] = portfolio["total_value_usd"] * USD_TO_SAR
            st.dataframe(portfolio)
            total_profit = portfolio["gain_loss"].sum()
            st.info(f"الربح/الخسارة الكلي: {total_profit:.2f} دولار / {total_profit * USD_TO_SAR:.2f} ريال")
        else:
            st.warning("لا توجد بيانات في المحفظة حالياً.")

    elif menu == "قائمة المراقبة":
        st.subheader("قائمة المراقبة")
        watchlist = load_watchlist()
        new_stock = st.text_input("أدخل رمز السهم (مثل AAPL)")
        if st.button("إضافة"):
            if new_stock and new_stock not in watchlist:
                watchlist.append(new_stock)
                save_watchlist([[s] for s in watchlist])
                st.success("تمت الإضافة")
        for stock in watchlist:
            col1, col2 = st.columns([4,1])
            col1.write(stock)
            if col2.button("❌", key=stock):
                watchlist.remove(stock)
                save_watchlist([[s] for s in watchlist])
                st.warning(f"تم حذف {stock}")

    elif menu == "إرسال تنبيه":
        st.subheader("تنبيه سعر السهم")
        stock = st.text_input("رمز السهم")
        target_price = st.number_input("أدخل السعر المستهدف", min_value=0.0)
        if st.button("فحص السعر الحالي"):
            if stock:
                try:
                    price = yf.Ticker(stock).history(period="1d")["Close"].iloc[-1]
                    st.write(f"السعر الحالي: {price:.2f}")
                    if price >= target_price:
                        send_telegram_message(f"السهم {stock} وصل السعر المستهدف: {price}")
                        st.success("تم إرسال التنبيه إلى تيليجرام")
                    else:
                        st.info("السعر الحالي لم يصل بعد للمستهدف")
                except:
                    st.error("حدث خطأ في جلب السعر")

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="centered")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if not st.session_state.logged_in:
    login()
else:
    main_app()
