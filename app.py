import streamlit as st
from streamlit_autorefresh import st_autorefresh
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import os

# ✅ التحديث التلقائي كل 10 ثواني
st_autorefresh(interval=10000, key="datarefresh")

# إعدادات
FINNHUB_API_KEY = "ضع_مفتاحك"
EODHD_API_KEY = "ضع_مفتاحك"
USD_TO_SAR = 3.75
PORTFOLIO_FILE = "portfolio.csv"

# --- وظائف مساعدة ---
def get_stock_logo(symbol):
    return f"https://logo.clearbit.com/{symbol.lower()}.com"

def get_news(symbol):
    try:
        url = f"https://eodhd.com/api/news?api_token={EODHD_API_KEY}&s={symbol}&limit=1"
        res = requests.get(url)
        articles = res.json()
        if articles:
            return articles[0]['title']
    except:
        pass
    return "لا توجد أخبار حاليًا"

def analyze_news(title):
    positive = ["expands", "growth", "launch", "beat", "strong"]
    negative = ["cut", "miss", "drop", "loss", "decline"]
    for word in positive:
        if word in title.lower():
            return "إيجابي"
    for word in negative:
        if word in title.lower():
            return "سلبي"
    return "محايد"

def get_analyst_opinion(symbol):
    try:
        url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={FINNHUB_API_KEY}"
        res = requests.get(url)
        rec = res.json()
        if rec:
            latest = rec[0]
            return latest['buy'], latest['sell'], latest['hold']
    except:
        pass
    return 0, 0, 0

def evaluate_opportunity(symbol):
    try:
        data = yf.Ticker(symbol)
        hist = data.history(period="2d")
        if len(hist) < 2:
            return {"symbol": symbol, "price": 0, "percent": 0, "news": "لا توجد بيانات", "analyst": "-", "recommendation": "لا يمكن التحليل", "score": 0}
        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[0]
        change = price - prev
        percent = (change / prev) * 100 if prev else 0
        news = get_news(symbol)
        sentiment = analyze_news(news)
        buy, sell, hold = get_analyst_opinion(symbol)
        score = 0
        if sentiment == "إيجابي": score += 1
        if change > 0: score += 1
        if buy > sell: score += 1
        return {
            "symbol": symbol,
            "price": price,
            "percent": percent,
            "news": sentiment,
            "analyst": f"{buy} شراء / {sell} بيع / {hold} احتفاظ",
            "recommendation": "دخول" if score >= 2 else "انتظار",
            "score": score
        }
    except:
        return {"symbol": symbol, "price": 0, "percent": 0, "news": "تعذر الاتصال", "analyst": "-", "recommendation": "تعذر التحليل", "score": 0}

def show_stock_card(data):
    logo = get_stock_logo(data['symbol'])
    color = "green" if data['percent'] >= 0 else "red"
    st.markdown(f"""
    <div style='border:1px solid #444; border-radius:16px; padding:16px; margin-bottom:20px; background:#111;'>
        <div style='display:flex; align-items:center;'>
            <img src='{logo}' width='36' style='margin-left:10px'/>
            <h4 style='margin:0; color:white'>{data['symbol'].upper()}</h4>
        </div>
        <p style='color:white;'>السعر: ${data['price']:.2f} / {(data['price'] * USD_TO_SAR):.2f} ريال</p>
        <p style='color:{color}; font-weight:bold;'>التغير: {data['percent']:+.2f}%</p>
        <p style='color:white;'>📰 الأخبار: {data['news']}</p>
        <p style='color:yellow;'>👨‍💼 المحللون: {data['analyst']}</p>
        <p style='color:cyan; font-weight:bold;'>✅ التوصية: {data['recommendation']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- صفحة المحفظة ---
def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        return pd.read_csv(PORTFOLIO_FILE)
    return pd.DataFrame(columns=["رمز السهم", "الكمية", "سعر الشراء"])

def save_portfolio(df):
    df.to_csv(PORTFOLIO_FILE, index=False)

def portfolio_page():
    st.subheader("📦 المحفظة")
    df = load_portfolio()

    if not df.empty:
        delete_index = st.selectbox("اختر الصفقة المراد حذفها", df.index, format_func=lambda i: f"{df.loc[i, 'رمز السهم']} - {df.loc[i, 'الكمية']} سهم @ {df.loc[i, 'سعر الشراء']}$")
        if st.button("🗑️ حذف الصفقة"):
            df = df.drop(delete_index).reset_index(drop=True)
            save_portfolio(df)
            st.success("تم حذف الصفقة.")
    st.dataframe(df)

    with st.form("إضافة صفقة"):
        symbol = st.text_input("رمز السهم")
        quantity = st.number_input("الكمية", min_value=1)
        buy_price = st.number_input("سعر الشراء")
        submitted = st.form_submit_button("إضافة")
        if submitted and symbol:
            new_row = pd.DataFrame([[symbol.upper(), quantity, buy_price]], columns=df.columns)
            df = pd.concat([df, new_row], ignore_index=True)
            save_portfolio(df)
            st.success("تمت إضافة الصفقة للمحفظة.")

    if not df.empty:
        st.subheader("📊 تحليل الربح / الخسارة")
        profits = []
        percents = []
        for _, row in df.iterrows():
            try:
                current_price = yf.Ticker(row["رمز السهم"]).history(period="1d")["Close"].iloc[-1]
                profit = (current_price - row["سعر الشراء"]) * row["الكمية"]
                percent = ((current_price - row["سعر الشراء"]) / row["سعر الشراء"]) * 100
                profits.append(profit)
                percents.append(percent)
            except:
                profits.append(0)
                percents.append(0)
        df["الربح"] = profits
        df["نسبة الربح (%)"] = [f"{p:.2f}%" for p in percents]
        st.dataframe(df)
        st.info(f"💰 إجمالي الربح الحالي: {sum(profits):.2f} دولار")

# --- الواجهة ---
st.set_page_config(page_title="الأسهم الذكية - فيصل", layout="wide")
st.title("منصة فيصل - الذكاء الصناعي الحقيقي")

menu = st.sidebar.radio("اختر الصفحة", ["تحليل الأسهم", "أفضل الفرص", "المحفظة"])

if menu == "تحليل الأسهم":
    symbols_input = st.text_input("أدخل رموز الأسهم مفصولة بفاصلة (مثل: AAPL, TSLA, MSFT)")
    if symbols_input:
        symbols = [s.strip().upper() for s in symbols_input.split(",")]
        for symbol in symbols:
            result = evaluate_opportunity(symbol)
            show_stock_card(result)

elif menu == "أفضل الفرص":
    symbols_input = st.text_input("أدخل رموز الأسهم لتقييم أفضل الفرص (مثل: AAPL, TSLA, MSFT)")
    if symbols_input:
        symbols = [s.strip().upper() for s in symbols_input.split(",")]
        results = [evaluate_opportunity(sym) for sym in symbols]
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        for res in sorted_results:
            show_stock_card(res)

elif menu == "المحفظة":
    portfolio_page()
