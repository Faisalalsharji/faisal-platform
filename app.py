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
    st.markdown("""
    مرحباً بك في منصة فيصل الذكية للأسهم  
    - اختر السهم من القائمة  
    - اختر المدة الزمنية  
    - سيتم عرض السعر الحالي والتغير  
    - سنقترح تنبيهات إذا وصل السعر لنقطة دخول  
    *تنبيه: لا تعتبر هذه التوصيات نصيحة مالية.
    """)

    selected_stock_label = st.selectbox("اختر السهم", list(stock_list.keys()))
    selected_stock = stock_list[selected_stock_label]

    period = st.selectbox("اختر المدة", ["1 يوم", "5 أيام", "1 شهر", "3 أشهر", "6 أشهر", "1 سنة"])
    period_map = {
        "1 يوم": "1d",
        "5 أيام": "5d",
        "1 شهر": "1mo",
        "3 أشهر": "3mo",
        "6 أشهر": "6mo",
        "1 سنة": "1y"
    }
    yf_period = period_map[period]

    # زر التحديث اليدوي
    if st.button("تحديث الآن"):
        st.session_state.refresh = True

    # تحميل البيانات
    if "refresh" not in st.session_state or st.session_state.refresh:
        data = yf.download(selected_stock, period=yf_period, interval="5m")
        st.session_state.refresh = False
    else:
        data = yf.download(selected_stock, period=yf_period, interval="5m")

    if data.empty or "Adj Close" not in data.columns:
        st.warning("لا توجد بيانات سعر حالياً، قد يكون السوق مغلق أو رمز السهم غير صحيح.")
        return

    # السعر الحالي
    latest_price = data["Adj Close"].iloc[-1]
    sar_price = round(latest_price * USD_TO_SAR, 2)

    # التغير
    if len(data["Adj Close"]) >= 2:
        change_percent = ((data["Adj Close"].iloc[-1] - data["Adj Close"].iloc[-2]) / data["Adj Close"].iloc[-2]) * 100
    else:
        change_percent = 0.0

    color = "green" if change_percent >= 0 else "red"

    # فرصة دخول
    suggested_entry = 196.00
    if latest_price < suggested_entry:
        st.success(f"أقل من السعر المقترح ({suggested_entry} USD) فرصة دخول! السعر الحالي: {round(latest_price, 2)}")

    # عرض السعر والتغير
    st.markdown(f"### السعر الحالي ({selected_stock})")
    st.markdown(f"<h2 style='color:white;'>{sar_price} ريال ({round(latest_price, 2)} USD)</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{color};'>تغير: {round(change_percent, 2)}%</p>", unsafe_allow_html=True)

    # تحليل الاتجاه
    if len(data["Adj Close"]) >= 3:
        last_3 = data["Adj Close"].iloc[-3:]
        if last_3.is_monotonic_increasing:
            trend = "صاعد"
            trend_color = "green"
        elif last_3.is_monotonic_decreasing:
            trend = "هابط"
            trend_color = "red"
        else:
            trend = "جانبي"
            trend_color = "orange"

        st.markdown(f"<h4 style='color:{trend_color};'>الاتجاه العام: {trend}</h4>", unsafe_allow_html=True)

    # رسم بياني
    st.line_chart(data["Adj Close"])

    # حفظ في قائمة المراقبة المؤقتة
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = []

    if st.button("أضف إلى قائمة المراقبة"):
        if selected_stock_label not in st.session_state.watchlist:
            st.session_state.watchlist.append(selected_stock_label)
            st.success("تمت الإضافة إلى قائمة المراقبة.")
        else:
            st.info("السهم موجود بالفعل في قائمة المراقبة.")

    # عرض قائمة المراقبة
    if st.session_state.watchlist:
        st.markdown("### قائمة المراقبة المؤقتة:")
        for stock in st.session_state.watchlist:
            st.markdown(f"- {stock}")

    # الوقت
    st.caption(f"آخر تحديث: {datetime.now().strftime('%H:%M:%S %d-%m-%Y')}")

# تشغيل التطبيق
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
