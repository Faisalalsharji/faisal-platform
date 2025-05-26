
import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt

USERNAME = "faisal"
PASSWORD = "faisal2025"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("تسجيل الدخول - منصة فيصل")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول بنجاح!")
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

def main_app():
    st.title("منصة الأسهم الذكية - فيصل")
    st.subheader("سهم Apple (AAPL)")

    # جلب البيانات
    data = yf.download("AAPL", period="5d", interval="1h")
    last_price = data["Close"][-1]
    sar_price = last_price * 3.75  # تحويل للدولار إلى ريال

    st.metric("السعر (USD)", f"${last_price:.2f}")
    st.metric("السعر (SAR)", f"{sar_price:.2f} ريال")

    # توصية ذكية
    st.info("التوصية: احتفاظ - لا توجد إشارة شراء حالياً")

    # رسم بياني
    st.line_chart(data["Close"], use_container_width=True)

    # زر تداول تجريبي
    if st.button("تفعيل التداول التجريبي"):
        st.success("تم تفعيل التداول التجريبي! (لا يتم تنفيذ أي صفقة فعلية)")

if not st.session_state.logged_in:
    login()
else:
    main_app()
