import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import requests

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75
TELEGRAM_TOKEN = "ضع_توكن_البوت"
TELEGRAM_CHAT_ID = "ضع_معرّف_الشات"
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
            st.success("تم تسجيل الدخول بنجاح")
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

def main_app():
    st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="centered")
    st.title("منصة فيصل - الأسهم الذكية")
    menu = st.sidebar.selectbox("القائمة", ["قائمة المراقبة", "ملخص المحفظة", "إضافة سهم للمحفظة", "تنبيه سعر"])

    if menu == "ملخص المحفظة":
        st.subheader("ملخص المحفظة")
        portfolio = load_portfolio()
        if not portfolio.empty:
            if st.button("تحديث الأسعار"):
                prices = []
                for symbol in portfolio["stock"]:
                    data = yf.Ticker(symbol)
                    prices.append(data.history(period="1d")["Close"].iloc[-1])
                portfolio["current_price"] = prices
                save_portfolio(portfolio)
            else:
                if "current_price" not in portfolio.columns:
                    prices = []
                    for symbol in portfolio["stock"]:
                        data = yf.Ticker(symbol)
                        prices.append(data.history(period="1d")["Close"].iloc[-1])
                    portfolio["current_price"] = prices
                    save_portfolio(portfolio)

            portfolio["gain_loss"] = (portfolio["current_price"] - portfolio["buy_price"]) * portfolio["quantity"]
            portfolio["total_value_usd"] = portfolio["current_price"] * portfolio["quantity"]
            portfolio["total_value_sar"] = portfolio["total_value_usd"] * USD_TO_SAR
            st.dataframe(portfolio)

            total_profit = portfolio["gain_loss"].sum()
            total_value = portfolio["total_value_sar"].sum()
            st.info(f"الربح/الخسارة الكلي: {total_profit:,.2f} دولار / {total_profit * USD_TO_SAR:,.2f} ريال")
            st.success(f"القيمة الحالية للمحفظة: {total_value:,.2f} ريال")

            for symbol in portfolio["stock"]:
                st.write(f"الرسم البياني للسهم: {symbol}")
                data = yf.Ticker(symbol).history(period="1mo")
                plt.figure()
                data["Close"].plot(title=symbol)
                st.pyplot(plt)

            for index, row in portfolio.iterrows():
                if st.button(f"حذف {row['stock']}", key=row['stock']):
                    portfolio = portfolio.drop(index)
                    save_portfolio(portfolio)
                    st.warning(f"تم حذف {row['stock']}")
                    st.experimental_rerun()
        else:
            st.warning("لا توجد بيانات في المحفظة حالياً.")

    elif menu == "إضافة سهم للمحفظة":
        st.subheader("إضافة سهم جديد")
        stock = st.text_input("رمز السهم")
        buy_price = st.number_input("سعر الشراء", min_value=0.0)
        quantity = st.number_input("الكمية", min_value=1)
        if st.button("إضافة للسجل"):
            if stock and buy_price > 0 and quantity > 0:
                portfolio = load_portfolio()
                new_row = pd.DataFrame([{
                    "stock": stock,
                    "buy_price": buy_price,
                    "quantity": quantity
                }])
                portfolio = pd.concat([portfolio, new_row], ignore_index=True)
                save_portfolio(portfolio)
                st.success("تمت إضافة السهم للمحفظة")

    elif menu == "قائمة المراقبة":
        st.subheader("قائمة المراقبة")
        watchlist = load_watchlist()
        new_stock = st.text_input("أدخل رمز السهم (مثال: AAPL)")
        if st.button("إضافة"):
            if new_stock and new_stock not in watchlist:
                watchlist.append(new_stock)
                save_watchlist([[s] for s in watchlist])
                st.success("تمت إضافة السهم إلى القائمة")

        for stock in watchlist:
            col1, col2 = st.columns([4, 1])
            col1.write(stock)
            if col2.button("X", key=stock):
                watchlist.remove(stock)
                save_watchlist([[s] for s in watchlist])
                st.warning(f"تم حذف {stock}")

    elif menu == "تنبيه سعر":
        st.subheader("تنبيه سعر السهم")
        stock = st.text_input("رمز السهم")
        target_price = st.number_input("أدخل السعر المستهدف", min_value=0.0)
        if st.button("تنبيه"):
            if stock:
                try:
                    price = yf.Ticker(stock).history(period="1d")["Close"].iloc[-1]
                    st.write(f"السعر الحالي لـ {stock}: {price:.2f}")
                    if price >= target_price:
                        send_telegram_message(f"سعر السهم {stock} وصل إلى {price:.2f}")
                        st.success("تم إرسال التنبيه إلى التليجرام")
                    else:
                        st.info("السعر الحالي لم يصل بعد للسعر المستهدف")
                except:
                    st.error("حدث خطأ في جلب السعر")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
