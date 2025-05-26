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
    "أمازون (AMZN)": "AMZN"
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

# واجهة المنصة
def main_app():
    st.title("منصة فيصل - الأسهم الذكية")

    st.markdown("""
    **مرحباً بك في منصة فيصل الذكية للأسهم.**

    - اختر السهم من القائمة (مثل آبل أو تسلا).
    - اختر المدة الزمنية.
    - سيتم عرض السعر الحالي والتغير.

    > **تنبيه:** لا تعتبر هذه التوصيات نصيحة مالية. استشر بناء على تحليلك وظروفك الشخصية.
    """)
    st.markdown("---")

    # اختيار السهم
    selected_label = st.selectbox("اختر السهم", options=list(stock_list.keys()))
    symbol = stock_list[selected_label]

    # اختيار المدة
    period_label = st.selectbox("اختر المدة", ["1 يوم", "5 أيام", "1 شهر", "6 أشهر", "1 سنة"])
    period_map = {
        "1 يوم": "1d",
        "5 أيام": "5d",
        "1 شهر": "1mo",
        "6 أشهر": "6mo",
        "1 سنة": "1y"
    }
    interval = "1m" if period_label == "1 يوم" else "1h"
    period = period_map[period_label]

    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)

        if data.empty:
            st.warning("لا توجد بيانات متاحة للفترة المحددة.")
            return

        current_price_usd = data["Close"].iloc[-1]
        previous_price_usd = data["Close"].iloc[-2] if len(data["Close"]) > 1 else current_price_usd
        change = current_price_usd - previous_price_usd
        percent_change = (change / previous_price_usd) * 100 if previous_price_usd != 0 else 0

        current_price_sar = current_price_usd * USD_TO_SAR

        st.metric(
            label=f"السعر الحالي ({symbol})",
            value=f"{current_price_sar:.2f} ريال ({current_price_usd:.2f} USD)",
            delta=f"{percent_change:.2f}%",
            delta_color="normal"
        )

        st.line_chart(data["Close"], height=300)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"آخر تحديث: {now}")

    except Exception as e:
        st.error("حدث خطأ أثناء جلب البيانات. تأكد من رمز السهم أو الاتصال بالإنترنت.")

# تشغيل التطبيق
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
