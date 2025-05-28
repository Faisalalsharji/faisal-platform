import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import os

# --- الإعدادات ---
FINNHUB_API_KEY = "d0ra3q1r01qn4tjhdq6gd0ra3q1r01qn4tjhdq6g"
EODHD_API_KEY = "ضع_مفتاحك"
USD_TO_SAR = 3.75
PORTFOLIO_FILE = "portfolio.csv"

# --- وظائف المساعدة ---
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

def plot_candlestick(symbol):
    try:
        data = yf.download(symbol, period="7d", interval="1d")
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close']
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, height=300)
        return fig
    except:
        return go.Figure()

def evaluate_opportunity(symbol):
    try:
        data = yf.Ticker(symbol)
        hist = data.history(period="2d")
        if len(hist) < 2:
            return {
                "symbol": symbol,
                "price": 0,
                "percent": 0,
                "news": "لا توجد بيانات",
                "analyst": "-",
                "recommendation": "لا يمكن التحليل",
                "score": 0
            }
        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[0]
        change = price - prev
        percent = (change / prev) * 100 if prev else 0
        news = get_news(symbol)
        sentiment = analyze_news(news)
        buy, sell, hold = get_analyst_opinion(symbol)
        score = 0
        if sentiment == "إيجابي":
            score += 1
        if change > 0:
            score += 1
        if buy > sell:
            score += 1
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
        return {
            "symbol": symbol,
            "price": 0,
            "percent": 0,
            "news": "تعذر الاتصال",
            "analyst": "-",
            "recommendation": "تعذر التحليل",
            "score": 0
        }

def show_stock_card(data):
    logo_url = get_stock_logo(data['symbol'])
    color = "green" if data['percent'] >= 0 else "red"
    st.markdown(f"""
    <div style='border:1px solid #444; border-radius:16px; padding:16px; margin-bottom:20px; background:#111;'>
        <div style='display:flex; align-items:center;'>
            <img src='{logo_url}' width='36' style='margin-left:10px'/>
            <h4 style='margin:0; color:white'>{data['symbol'].upper()}</h4>
        </div>
        <p style='color:white;'>السعر: ${data['price']:.2f} / {(data['price'] * USD_TO_SAR):.2f} ريال</p>
        <p style='color:{color}; font-weight:bold;'>التغير: {data['percent']:+.2f}%</p>
        <p style='color:white;'>📰 الأخبار: {data['news']}</p>
        <p style='color:yellow;'>👨‍💼 المحللون: {data['analyst']}</p>
        <p style='color:cyan; font-weight:bold;'>✅ التوصية: {data['recommendation']}</p>
    </div>
    """, unsafe_allow_html=True)

# --- الواجهة ---
st.set_page_config(page_title="الأسهم الذكية - فيصل", layout="wide")
st.title("منصة فيصل - الذكاء الصناعي الحقيقي")

symbols_input = st.text_input("أدخل رموز الأسهم مفصولة بفاصلة (مثل: AAPL, TSLA, MSFT)")
st.caption("📌 ملاحظة: تأكد من كتابة رمز السهم الصحيح (مثل: AAPL). البيانات قد لا تظهر إذا كان السوق مغلق.")

if st.button("تحليل"):
    if symbols_input:
        symbols = [s.strip().upper() for s in symbols_input.split(",")]
        for symbol in symbols:
            if not symbol.isalpha() or len(symbol) > 5:
                st.warning(f"❗ رمز غير صحيح: {symbol}")
                continue
            result = evaluate_opportunity(symbol)
            show_stock_card(result)
            st.plotly_chart(plot_candlestick(symbol), use_container_width=True)
