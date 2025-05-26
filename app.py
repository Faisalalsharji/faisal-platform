import streamlit as st
import yfinance as yf
from datetime import datetime

# إعداد الصفحة
st.set_page_config(
    page_title="منصة فيصل - الأسهم الذكية",
    layout="centered"
)

# بيانات الدخول
USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75

# قائمة الأسهم
stock_list = {
    "آبل (AAPL)": "AAPL",
    "نفيديا (NVDA)": "NVDA",
    "تسلا (TSLA)": "TSLA",
    "قوقل (GOOG)": "GOOG",
    "أمازون (AMZN)": "AMZN",
    "مايكروسوفت (MSFT)": "MSFT",
    "ميتا (META)": "META"
}

# واجهة تسجيل الدخول
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

# الوظائف الرئيسية للمنصة
def main_app():
    st.title("منصة فيصل - الأسهم الذكية")
    st.markdown("""
    مرحباً بك في منصة فيصل الذكية للأسهم  
    - اختر السهم من القائمة (مثل آبل أو تسلا)  
    - اختر المدة الزمنية  
    - سيتم عرض السعر الحالي والتغير  
    - سنقترح تنبيهات إذا وصل السعر لنقطة دخول  
    *تنبيه: لا تعتبر هذه التوصيات نصيحة مالية.
    """)

    # اختيار السهم
    selected_stock_label = st.selectbox("اختر السهم", list(stock_list.keys()))
    selected_stock = stock_list[selected_stock_label]

    # اختيار المدة
    period = st.selectbox("اختر المدة", ["1 يوم", "5 أيام", "1 شهر", "3 أشهر", "6 أشهر", "1 سنة"])

    # تحويل المدة لـ yfinance
    period_map = {
        "1 يوم": "1d",
        "5 أيام": "5d",
        "1 شهر": "1mo",
        "3 أشهر": "3mo",
        "6 أشهر": "6mo",
        "1 سنة": "1y"
    }
    yf_period = period_map[period]

    # تحميل بيانات السهم
    data = yf.download(selected_stock, period=yf_period, interval="5m")
    if data.empty:
        st.warning("لا توجد بيانات متاحة حالياً.")
        return

    # حساب السعر الحالي
    latest_price = data["Close"][-1]
    sar_price = round(latest_price * USD_TO_SAR, 2)

    # التغير
    change_percent = ((data["Close"][-1] - data["Close"][-2]) / data["Close"][-2]) * 100
    color = "green" if change_percent >= 0 else "red"

    # سعر دخول مقترح
    suggested_entry = 196.00  # كمثال لآبل (تخصيص لاحقًا حسب السهم)

    # عرض تنبيه
    if latest_price < suggested_entry:
        st.success(f"أقل من السعر المقترح ({suggested_entry} USD) فرصة دخول! السعر الحالي: {round(latest_price, 2)}")

    # عرض السعر
    st.markdown(f"### السعر الحالي ({selected_stock})")
    st.markdown(f"<h2 style='color:white;'>{sar_price} ريال ({round(latest_price, 2)} USD)</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{color};'>تغير: {round(change_percent, 2)}%</p>", unsafe_allow_html=True)

    # رسم بياني
    st.line_chart(data["Close"])

    # إضافة إلى قائمة المراقبة (لاحقًا سنفعلها)
    if st.button("أضف إلى قائمة المراقبة"):
        st.info("تمت الإضافة إلى قائمة المراقبة (قريبًا سيتم حفظها فعلياً)")

    st.caption(f"آخر تحديث: {datetime.now().strftime('%H:%M:%S %d-%m-%Y')}")

# إدارة جلسة الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
