import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime

USERNAME = "faisal"
PASSWORD = "faisal2025"
INVITE_CODE = "INVITE2025"
USD_TO_SAR = 3.75
PORTFOLIO_FILE = "portfolio.csv"
TRADES_FILE = "trades.csv"
LANG_AR = "ar"
LANG_EN = "en"

def detect_lang():
    return LANG_AR if "ar" in st.get_option("browser.gatherUsageStats") else LANG_EN

lang = detect_lang()

def save_portfolio(portfolio):
    df = pd.DataFrame(portfolio)
    df.to_csv(PORTFOLIO_FILE, index=False)

def load_portfolio():
    try:
        return pd.read_csv(PORTFOLIO_FILE)
    except:
        return pd.DataFrame(columns=["stock", "buy_price", "quantity", "type", "date"])

def save_trades(trades):
    trades.to_csv(TRADES_FILE, index=False)

def load_trades():
    try:
        return pd.read_csv(TRADES_FILE)
    except:
        return pd.DataFrame(columns=["stock", "action", "price", "date"])

def rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def login():
    st.title("تسجيل الدخول - منصة فيصل")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    invite = st.text_input("رمز الدعوة")
    if st.button("دخول"):
        if username == USERNAME and password == PASSWORD and invite == INVITE_CODE:
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول")
        else:
            st.error("بيانات الدخول غير صحيحة")

def add_trade_ui():
    st.subheader("إضافة صفقة")
    stock = st.text_input("رمز السهم")
    action = st.selectbox("العملية", ["شراء", "بيع"])
    price = st.number_input("السعر", min_value=0.0)
    if st.button("سجل الصفقة"):
        if stock and price > 0:
            trades = load_trades()
            new = pd.DataFrame([{
                "stock": stock,
                "action": action,
                "price": price,
                "date": datetime.datetime.now().strftime("%Y-%m-%d")
            }])
            trades = pd.concat([trades, new], ignore_index=True)
            save_trades(trades)
            st.success("تم تسجيل الصفقة")

def dashboard():
    st.title("الملخص المالي الذكي")
    trades = load_trades()
    if not trades.empty:
        trades["date"] = pd.to_datetime(trades["date"])
        trades["month"] = trades["date"].dt.to_period("M")
        summary = trades.groupby("month")["price"].sum()
        summary.index = summary.index.astype(str)
        fig, ax = plt.subplots()
        ax.plot(summary.index, summary.values)
        ax.set_title("أداء الأرباح/الخسائر الشهرية")
        st.pyplot(fig)

        goal = 1000000
        current = summary.sum()
        percent = (current / goal) * 100
        st.progress(min(percent/100, 1))
        st.success(f"التقدم نحو المليون: {current:,.2f} ريال / {goal:,} ريال")
    else:
        st.info("لا يوجد صفقات مسجلة بعد.")

def advanced_ai_analysis():
    st.title("تحليل فني متقدم للأسهم")
    portfolio = load_portfolio()
    if not portfolio.empty:
        for symbol in portfolio["stock"]:
            try:
                data = yf.Ticker(symbol).history(period="30d")["Close"]
                if len(data) >= 15:
                    score = rsi(data).iloc[-1]
                    if score > 70:
                        signal = "بيع (مؤشر RSI مرتفع)"
                    elif score < 30:
                        signal = "شراء (RSI منخفض)"
                    else:
                        signal = "احتفاظ"
                    st.write(f"{symbol}: {signal} - RSI: {score:.2f}")
            except:
                st.warning(f"فشل تحليل {symbol}")
    else:
        st.info("المحفظة فارغة")

def ai_accuracy_report():
    st.title("تقييم ذكاء التوصيات السابقة")
    trades = load_trades()
    if not trades.empty:
        trades["date"] = pd.to_datetime(trades["date"])
        win_count = 0
        total = 0
        for i, row in trades.iterrows():
            symbol = row["stock"]
            price_then = row["price"]
            try:
                now = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1]
                if (row["action"] == "شراء" and now > price_then) or (row["action"] == "بيع" and now < price_then):
                    win_count += 1
                total += 1
            except:
                continue
        if total > 0:
            percent = (win_count / total) * 100
            st.success(f"دقة الذكاء الاصطناعي: {percent:.2f}% من التوصيات كانت صحيحة")
        else:
            st.info("لا يمكن التقييم حالياً")
    else:
        st.info("لا يوجد صفقات للتقييم")

def main_app():
    st.sidebar.title("القائمة")
    page = st.sidebar.selectbox("اختر", ["Dashboard", "تسجيل صفقة", "تحليل AI", "تقييم AI"])
    if page == "Dashboard":
        dashboard()
    elif page == "تسجيل صفقة":
        add_trade_ui()
    elif page == "تحليل AI":
        advanced_ai_analysis()
    elif page == "تقييم AI":
        ai_accuracy_report()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
else:
    main_app()
