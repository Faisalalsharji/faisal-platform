import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(page_title="منصة فيصل - الذكاء الصناعي الحقيقي", layout="wide")
st_autorefresh(interval=5000, key="auto-refresh")

FINNHUB_API_KEY = "d0rm6m1r01qumepf3hi0d0rm6m1r01qumepf3hig"
EODHD_API_KEY = "ضع_مفتاحك_هنا"
USD_TO_SAR = 3.75
HALAL_STOCKS = ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "NVDA"]

def get_news(symbol):
    try:
        url = f"https://eodhd.com/api/news?api_token={EODHD_API_KEY}&s={symbol}&limit=1"
        res = requests.get(url)
        articles = res.json()
        if articles:
            return articles[0]["title"]
    except:
        pass
    return "لا توجد أخبار حالياً"

def analyze_news(title):
    positives = ["expands", "growth", "launch", "beat", "strong"]
    negatives = ["cut", "miss", "drop", "loss", "decline"]
    for word in positives:
        if word in title.lower():
            return "إيجابي"
    for word in negatives:
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
            return latest["buy"], latest["sell"], latest["hold"]
    except:
        pass
    return 0, 0, 0

def estimate_days_to_target(change_percent):
    if change_percent <= 0.5:
        return "من 10 إلى 15 يوم"
    elif change_percent <= 1:
        return "من 7 إلى 10 أيام"
    elif change_percent <= 2:
        return "من 4 إلى 7 أيام"
    else:
        return "من 2 إلى 4 أيام"

def calculate_rsi(data, period=14):
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data):
    exp1 = data["Close"].ewm(span=12, adjust=False).mean()
    exp2 = data["Close"].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def evaluate_opportunity(symbol):
    try:
        data = yf.Ticker(symbol)
        hist = data.history(period="30d")
        if len(hist) < 20:
            return None

        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]
        change = price - prev
        percent = (change / prev) * 100 if prev else 0
        news = get_news(symbol)
        sentiment = analyze_news(news)
        buy, sell, hold = get_analyst_opinion(symbol)
        rsi = calculate_rsi(hist).iloc[-1]
        macd, signal = calculate_macd(hist)
        macd_signal_diff = macd.iloc[-1] - signal.iloc[-1]
        volume = hist["Volume"].iloc[-1]

        score = 0
        reasons = []

        if sentiment == "إيجابي":
            score += 1
            reasons.append("📰 الأخبار إيجابية")
        if change > 0:
            score += 1
            reasons.append("📈 السعر مرتفع")
        if buy > sell:
            score += 1
            reasons.append("👨‍💼 عدد المشترين أعلى من البائعين")
        if price > prev:
            reasons.append("🕯️ الشمعة صاعدة")
        if rsi < 70:
            score += 1
            reasons.append("📊 RSI جيد")
        if macd_signal_diff > 0:
            score += 1
            reasons.append("📈 مؤشر MACD إيجابي")
        if volume > hist["Volume"].mean():
            score += 1
            reasons.append("🔊 حجم تداول مرتفع")

        recommendation = "✅ دخول" if score >= 3 else "⏳ انتظار"
        entry_price = round(price - (price * 0.01), 2)
        target_price = round(price + (price * 0.03), 2)
        exit_price = round(price + (price * 0.04), 2)
        estimated_days = estimate_days_to_target(percent)

        return {
            "symbol": symbol,
            "price": price,
            "percent": percent,
            "news": sentiment,
            "analyst": f"{buy} شراء / {sell} بيع / {hold} احتفاظ",
            "recommendation": recommendation,
            "reason": " | ".join(reasons),
            "entry_price": entry_price,
            "target_price": target_price,
            "exit_price": exit_price,
            "estimated_days": estimated_days
        }
    except:
        return None

def show_stock_card(data):
    color = "green" if data["percent"] >= 0 else "red"
    st.markdown(f"""
    <div style='border:1px solid #444; border-radius:16px; padding:20px; margin-bottom:20px; background:#111;'>
        <h4 style='color:white;'><img src='https://logo.clearbit.com/{data['symbol'].lower()}.com' width='28'> {data['symbol']}</h4>
        <p style='color:white;'>السعر: {data['price'] * USD_TO_SAR:.2f} ريال / {data['price']}$</p>
        <p style='color:{color}; font-weight:bold;'>% التغير: {data['percent']:.2f}+ </p>
        <p style='color:white;'>📰 الأخبار: {data['news']}</p>
        <p style='color:yellow;'>👨‍💼 المحللون: {data['analyst']}</p>
        <p style='color:cyan; font-weight:bold;'>✅ التوصية: {data['recommendation']}</p>
        <p style='color:orange;'>📌 السبب: {data['reason']}</p>
        <p style='color:lime;'>💡 أفضل دخول: {data['entry_price']}$</p>
        <p style='color:#00FF99;'>🎯 الهدف: {data['target_price']}$</p>
        <p style='color:#FFCC00;'>🚪 الخروج: عند {data['exit_price']}$</p>
        <p style='color:#87CEEB;'>🕐 المدة المتوقعة للوصول للهدف: {data['estimated_days']}</p>
    </div>
    """, unsafe_allow_html=True)

st.title("منصة فيصل - الذكاء الصناعي الحقيقي")
query = st.text_input("🔍 ابحث عن سهم (اكتب أول حرف فقط مثلاً A)")

matches = [s for s in HALAL_STOCKS if s.startswith(query.upper())] if query else HALAL_STOCKS

for symbol in matches:
    result = evaluate_opportunity(symbol)
    if result:
        show_stock_card(result)
    else:
        st.warning(f"⚠️ تعذر عرض بيانات {symbol}")
