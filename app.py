import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# إعداد الصفحة
st.set_page_config(page_title="منصة فيصل - الذكاء الصناعي", layout="wide")
st.title("منصة فيصل - الذكاء الصناعي الحقيقي")

# مفاتيح API
FINNHUB_API_KEY = "ضع_مفتاحك_هنا"
EODHD_API_KEY = "ضع_مفتاحك_هنا"
USD_TO_SAR = 3.75

# قائمة الأسهم الحلال
HALAL_STOCKS = ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "NVDA"]

# الحصول على الأخبار
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

# تحليل الأخبار
def analyze_news(title):
    positives = ["expand", "growth", "launch", "beat", "strong"]
    negatives = ["cut", "miss", "drop", "loss", "decline"]
    for word in positives:
        if word in title.lower():
            return "إيجابي"
    for word in negatives:
        if word in title.lower():
            return "سلبي"
    return "محايد"

# رأي المحللين
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

# تحليل الشموع اليابانية (بسيط)
def analyze_candle(data):
    try:
        last_candle = data.tail(1)
        open_price = last_candle["Open"].values[0]
        close_price = last_candle["Close"].values[0]
        if close_price > open_price:
            return "شمعة صاعدة"
        elif close_price < open_price:
            return "شمعة هابطة"
        else:
            return "شمعة محايدة"
    except:
        return "غير متوفر"

# التقييم الذكي الكامل
def evaluate_stock(symbol):
    try:
        data = yf.Ticker(symbol)
        hist = data.history(period="2d")
        if len(hist) < 2:
            return None

        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[0]
        change = price - prev
        percent = (change / prev) * 100 if prev else 0

        news = get_news(symbol)
        sentiment = analyze_news(news)
        buy, sell, hold = get_analyst_opinion(symbol)
        candle = analyze_candle(hist)

        score = 0
        reason_parts = []

        if sentiment == "إيجابي":
            score += 1
            reason_parts.append("📈 الأخبار إيجابية")

        if change > 0:
            score += 1
            reason_parts.append("📊 السعر مرتفع")
        elif change < 0:
            reason_parts.append("📉 السعر منخفض")

        if buy > sell:
            score += 1
            reason_parts.append("👨‍💼 المحللون يوصون بالشراء")

        if "صاعدة" in candle:
            score += 1
            reason_parts.append("🕯️ الشمعة صاعدة")

        recommendation = "✅ دخول" if score >= 3 else "⏳ انتظار"
        reason = " | ".join(reason_parts)

        return {
            "symbol": symbol,
            "price": price,
            "percent": round(percent, 2),
            "news": sentiment,
            "analyst": f"{buy} شراء / {sell} بيع / {hold} احتفاظ",
            "recommendation": recommendation,
            "reason": reason,
            "price_sar": round(price * USD_TO_SAR, 2)
        }
    except:
        return None

# عرض بطاقة السهم
def show_stock_card(data):
    color = "green" if data["percent"] >= 0 else "red"
    st.markdown(f"""
    <div style='border:1px solid #444; border-radius:16px; padding:16px; margin-bottom:20px; background:#111;'>
        <h4 style='color:white;'>{data['symbol']}</h4>
        <p style='color:white;'>السعر: {data['price_sar']} ريال / ${data['price']}</p>
        <p style='color:{color}; font-weight:bold;'>% التغير: {data['percent']}+</p>
        <p style='color:white;'>📰 الأخبار: {data['news']}</p>
        <p style='color:yellow;'>👨‍💼 المحللون: {data['analyst']}</p>
        <p style='color:cyan; font-weight:bold;'>✅ التوصية: {data['recommendation']}</p>
        <p style='color:orange;'>📌 السبب: {data['reason']}</p>
    </div>
    """, unsafe_allow_html=True)

# إدخال المستخدم
query = st.text_input("🔍 ابحث عن سهم (اكتب أول حرف فقط مثلاً A)")

matches = [s for s in HALAL_STOCKS if s.startswith(query.upper())] if query else HALAL_STOCKS

for symbol in matches:
    result = evaluate_stock(symbol)
    if result:
        show_stock_card(result)
    else:
        st.warning(f"⚠️ تعذر عرض بيانات {symbol}")
