import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import numpy as np
from sklearn.linear_model import LinearRegression
from streamlit_autorefresh import st_autorefresh

# إعداد الصفحة
st.set_page_config(page_title="منصة فيصل - الذكاء الصناعي الحقيقي", layout="wide")
st_autorefresh(interval=5000, key="auto-refresh")

# إعدادات عامة
FINNHUB_API_KEY = "d0rm6m1r01qumepf3hi0d0rm6m1r01qumepf3hig"
EODHD_API_KEY = "ضع_مفتاحك_هنا"
USD_TO_SAR = 3.75
HALAL_STOCKS = ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "NVDA"]

# جلب الأخبار
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
    positives = ["expands", "growth", "launch", "beat", "strong"]
    negatives = ["cut", "miss", "drop", "loss", "decline"]
    for word in positives:
        if word in title.lower():
            return "إيجابي"
    for word in negatives:
        if word in title.lower():
            return "سلبي"
    return "محايد"

# توصيات المحللين
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

# تحليل الانحدار الخطي لتوقع الاتجاه
def linear_regression_trend(symbol):
    try:
        df = yf.Ticker(symbol).history(period="14d")
        df = df.reset_index()
        df["day"] = np.arange(len(df)).reshape(-1, 1)
        X = df["day"].values.reshape(-1, 1)
        y = df["Close"].values.reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)
        next_day = np.array([[len(df)]])
        predicted_price = model.predict(next_day)[0][0]
        slope = model.coef_[0][0]

        trend = "صاعد" if slope > 0 else "هابط"
        return predicted_price, trend
    except:
        return None, "غير معروف"

# تقدير المدة للوصول للهدف
def estimate_days_to_target(change_percent):
    if change_percent <= 0.5:
        return "من 10 إلى 15 يوم"
    elif change_percent <= 1:
        return "من 7 إلى 10 أيام"
    elif change_percent <= 2:
        return "من 4 إلى 7 أيام"
    else:
        return "من 2 إلى 4 أيام"

# تحليل السهم بالذكاء الصناعي
def evaluate_opportunity(symbol):
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
        predicted_price, trend = linear_regression_trend(symbol)

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

        recommendation = "✅ دخول" if score >= 2 else "⏳ انتظار"
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
            "estimated_days": estimated_days,
            "predicted_price": predicted_price,
            "trend": trend
        }
    except:
        return None

# عرض بطاقة السهم
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
        <p style='color:#7FFFD4;'>📊 توقع الغد: {data['predicted_price']:.2f}$ | الاتجاه: {data['trend']}</p>
    </div>
    """, unsafe_allow_html=True)

# الواجهة
st.title("منصة فيصل - الذكاء الصناعي الحقيقي")
query = st.text_input("🔍 ابحث عن سهم (اكتب أول حرف فقط مثلاً A)")

matches = [s for s in HALAL_STOCKS if s.startswith(query.upper())] if query else HALAL_STOCKS

for symbol in matches:
    result = evaluate_opportunity(symbol)
    if result:
        show_stock_card(result)
    else:
        st.warning(f"⚠️ تعذر عرض بيانات {symbol}")
