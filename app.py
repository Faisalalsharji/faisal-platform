import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(
    page_title="منصة فيصل - الأسهم الذكية",
    layout="centered"
)

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75

stock_list = {
    "آبل (AAPL)": "AAPL",
    "نفيديا (NVDA)": "NVDA",
    "تسلا (TSLA)": "TSLA",
    "قوقل (GOOG)": "GOOG",
    "أمازون (AMZN)": "AMZN"
}
import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(
    page_title="منصة فيصل - الأسهم الذكية",
    layout="centered"
)

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75

stock_list = {
    "آبل (AAPL)": "AAPL",
    "نفيديا (NVDA)": "NVDA",
    "تسلا (TSLA)": "TSLA",
    "قوقل (GOOG)": "GOOG",
    "أمازون (AMZN)": "AMZN"
}

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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    st.title("منصة فيصل - الأسهم الذكية")
    st.write("مرحبا بك، سيتم عرض البيانات بعد قليل.")
