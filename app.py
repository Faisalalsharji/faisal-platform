import streamlit as st
import yfinance as yf

# بيانات الدخول
USERNAME = "admin"
PASSWORD = "123"
USD_TO_SAR = 3.75

# قائمة الأسهم الحلال
HALAL_STOCKS = ["AAPL", "NVDA", "GOOG", "MSFT", "TSLA", "AMZN", "META", "ADBE", "INTC", "CRM"]

# صفحة تسجيل الدخول
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

# توصية ذكية بناءً على حركة السعر
def get_recommendation(data):
    if len(data) < 2:
        return "لا توجد بيانات كافية"
    change = data[-1] - data[-2]
    if change > 0.5:
        return "شراء"
    elif change < -0.5:
        return "بيع"
    else:
        return "احتفاظ"

# الصفحة الرئيسية
def main_app():
    st.title("منصة الأسهم الذكية - فيصل")
    st.markdown("---")

    # اختيار سهم من القائمة أو إدخال يدوي
    st.subheader("اختر سهمًا من الأسهم الشرعية:")
    stock_choice = st.selectbox("الأسهم الحلال", HALAL_STOCKS)
    manual_input = st.text_input("أو أدخل رمز سهم آخر", value=stock_choice)

    symbol = manual_input.strip().upper()
    if symbol:
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d", interval="5m")

            if data.empty:
                st.warning("لا توجد بيانات حالياً لهذا السهم.")
                return

            price_usd = data["Close"].iloc[-1]
            price_sar = price_usd * USD_TO_SAR
            recommendation = get_recommendation(data["Close"])

            st.metric(label=f"السعر (USD)", value=f"${price_usd:.2f}")
            st.metric(label="السعر بالريال (SAR)", value=f"{price_sar:.2f} ريال")
            st.success(f"التوصية الذكية: {recommendation}")
            st.line_chart(data["Close"])

        except:
            st.error("حدث خطأ أثناء جلب البيانات. تأكد من رمز السهم.")

# حالة تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
