import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="centered")

USERNAME = "admin"
PASSWORD = "123"
USD_TO_SAR = 3.75

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
    st.title("منصة فيصل - الأسهم الذكية")
    st.markdown("---")

    stock_list = {
        "آبل (AAPL)": "AAPL",
        "نفيديا (NVDA)": "NVDA",
        "تسلا (TSLA)": "TSLA",
        "جوجل (GOOG)": "GOOG",
        "أمازون (AMZN)": "AMZN"
    }
    selected_label = st.selectbox("اختر السهم", options=list(stock_list.keys()))
    symbol = stock_list[selected_label]

    period_label = st.selectbox("اختر المدة", ["1 يوم", "5 أيام", "شهر", "6 أشهر", "سنة"])
    period_map = {
        "1 يوم": "1d",
        "5 أيام": "5d",
        "شهر": "1mo",
        "6 أشهر": "6mo",
        "سنة": "1y"
    }
    interval = "1m" if period_label == "1 يوم" else "1h"
    period = period_map[period_label]

    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)

        if data.empty:
            st.warning("لا توجد بيانات متاحة للفترة المحددة.")
            return

        current_price = data["Close"].iloc[-1]
        previous_price = data["Close"].iloc[-2] if len(data["Close"]) > 1 else current_price
        change = current_price - previous_price
        percent_change = (change / previous_price) * 100 if previous_price != 0 else 0

        st.metric(
            label=f"السعر الحالي لـ {symbol}",
            value=f"${current_price:.2f} / {current_price * USD_TO_SAR:.2f} ريال",
            delta=f"{percent_change:.2f}%",
            delta_color="normal"
        )

        st.line_chart(data["Close"], height=300)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        st.caption(f"آخر تحديث: {now}")

    except Exception as e:
        st.error("حدث خطأ أثناء جلب البيانات. تأكد من رمز السهم أو الاتصال.")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
