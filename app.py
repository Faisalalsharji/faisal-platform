import streamlit as st
import yfinance as yf
import pandas as pd

# بيانات الدخول
USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75
WATCHLIST_FILE = "watchlist.csv"
HALAL_STOCKS = ["AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN", "META", "ADBE", "INTC", "CRM"]

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="wide")

# تصميم CSS احترافي
st.markdown("""
    <style>
    .stock-card {
        background-color: #111;
        padding: 18px;
        border-radius: 20px;
        border: 1px solid #333;
        margin-bottom: 16px;
        transition: 0.3s ease;
    }
    .stock-card:hover {
        border: 1px solid #00FFAA;
        transform: scale(1.01);
    }
    .footer-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111;
        padding: 8px;
        display: flex;
        justify-content: space-around;
        border-top: 1px solid #333;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# تسجيل الدخول
def login():
    st.title("تسجيل الدخول - منصة فيصل")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

# حفظ واسترجاع قائمة الأسهم
def save_watchlist(watchlist):
    df = pd.DataFrame(watchlist, columns=["stock"])
    df.to_csv(WATCHLIST_FILE, index=False)

def load_watchlist():
    try:
        df = pd.read_csv(WATCHLIST_FILE)
        return df["stock"].tolist()
    except:
        return []

# عرض بطاقات الأسهم
def stock_cards():
    st.header("الأسهم")
    watchlist = load_watchlist()

    st.sidebar.title("إدارة قائمة الأسهم")
    new_stock = st.sidebar.text_input("أضف سهم")
    if st.sidebar.button("إضافة"):
        if new_stock and new_stock.upper() not in watchlist:
            watchlist.append(new_stock.upper())
            save_watchlist(watchlist)
            st.rerun()

    filter_type = st.sidebar.radio("فلتر:", ["الكل", "الحلال فقط"])
    filtered_list = [s for s in watchlist if s in HALAL_STOCKS] if filter_type == "الحلال فقط" else watchlist

    stocks_data = []
    for symbol in filtered_list:
        try:
            data = yf.Ticker(symbol)
            price = data.history(period="1d")["Close"].iloc[-1]
            prev = data.history(period="2d")["Close"].iloc[0]
            change = price - prev
            percent = (change / prev) * 100 if prev else 0
            stocks_data.append({
                "symbol": symbol,
                "price": price,
                "sar": price * USD_TO_SAR,
                "change": change,
                "percent": percent,
                "color": "green" if change >= 0 else "red"
            })
        except:
            continue

    if not stocks_data:
        st.warning("لا توجد أسهم مضافة")
    else:
        st.subheader("قائمة الأسهم")
        for stock in stocks_data:
            st.markdown(f"""
                <div class='stock-card'>
                    <h4 style='color:white'>{stock['symbol']}</h4>
                    <p style='color:white'>${stock['price']:.2f} / {stock['sar']:.2f} ريال</p>
                    <p style='color:{stock['color']};font-weight:bold'>{stock['change']:+.2f} ({stock['percent']:+.2f}%)</p>
                </div>
            """, unsafe_allow_html=True)

# صفحة رئيسية
def main_app():
    st.sidebar.title("القائمة")
    page = st.sidebar.selectbox("اختر الصفحة", ["الأسهم"])
    if page == "الأسهم":
        stock_cards()

# بدء التطبيق
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()

# شريط تنقل سفلي ثابت
st.markdown("""
<div class='footer-bar'>
    <div style='color:white'>الأسهم</div>
    <div style='color:gray'>المراجعات</div>
    <div style='color:gray'>الصناديق</div>
    <div style='color:gray'>المحفظة</div>
</div>
""", unsafe_allow_html=True)
