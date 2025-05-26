import streamlit as st
import pandas as pd
import requests

# إعدادات الحساب
USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75
TELEGRAM_TOKEN = "ضع_توكن_البوت_هنا"
TELEGRAM_CHAT_ID = "ضع_Chat_ID_هنا"
WATCHLIST_FILE = "watchlist.csv"

# قائمة الأسهم
stock_list = {
    "آبل (AAPL)": "AAPL",
    "نفيديا (NVDA)": "NVDA",
    "تسلا (TSLA)": "TSLA",
    "قوقل (GOOG)": "GOOG",
    "أمازون (AMZN)": "AMZN"
}

# حفظ قائمة المراقبة
def save_watchlist(watchlist):
    df = pd.DataFrame(watchlist, columns=["stock"])
    df.to_csv(WATCHLIST_FILE, index=False)

# إرسال تنبيه إلى Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        pass

# تسجيل الدخول
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

# التطبيق الرئيسي
def main_app():
    st.title("منصة فيصل - الأسهم الذكية")
    menu = st.sidebar.selectbox("القائمة", ["ملخص المحفظة", "قائمة المراقبة", "إرسال تنبيه"])

    if menu == "ملخص المحفظة":
        st.subheader("ملخص المحفظة")
        st.info("سيتم إضافة ملخص المحفظة لاحقاً")

    elif menu == "قائمة المراقبة":
        st.subheader("قائمة المراقبة")
        watchlist = list(stock_list.values())
        selected = st.multiselect("اختر الأسهم", options=watchlist)
        if st.button("حفظ القائمة"):
            save_watchlist([[s] for s in selected])
            st.success("تم حفظ قائمة المراقبة")

    elif menu == "إرسال تنبيه":
        st.subheader("إرسال تنبيه إلى Telegram")
        msg = st.text_input("اكتب الرسالة")
        if st.button("إرسال"):
            send_telegram_message(msg)
            st.success("تم إرسال الرسالة")

# تشغيل التطبيق
st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="centered")
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
