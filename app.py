import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import time

# تحديث تلقائي كل 5 ثواني
st.experimental_set_query_params(t=int(time.time()))
st.markdown(
    """<meta http-equiv="refresh" content="5">""",
    unsafe_allow_html=True
)

# إعداد الصفحة
st.set_page_config(page_title="منصة فيصل - الذكاء الصناعي", layout="wide")
st.title("منصة فيصل - الذكاء الصناعي الحقيقي")

# مفاتيح API
FINNHUB_API_KEY = "ضع_مفتاحك_هنا"
EODHD_API_KEY = "ضع_مفتاحك_هنا"
USD_TO_SAR = 3.75

# قائمة الأسهم الحلال
HALAL_STOCKS = ["AAPL", "MSFT", "TSLA", "NVDA", "GOOG", "AMZN"]

# الحصول على شعار السهم
def get_stock_logo(symbol):
    return f"https://logo.clearbit.com/{symbol.lower()}.com"

# جلب الأخبار
def get_news(symbol):
    try:
        url = f"https://eodhd.com/api/news?api_token={EODHD_API_KEY}&s={symbol}&limit=1"
        res = requests.get(url)
        articles = res.json()
        if articles:
            return articles[0]['title']
    except:
        pass
    return "لا توجد أخبار حالياً"

# تحليل الأخبار
def analyze_news(title):
    positive_keywords = ["expands", "growth", "launch", "beat", "strong"]
    negative_keywords = ["cut", "miss", "drop", "loss", "decline"]
    for word in positive_keywords:
        if word in title.lower():
            return "إيجابي"
    for word in negative_keywords:
        if word in title.lower():
            return "سلبي"
    return "محايد"

# آراء المحللين
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

# تحليل الفرصة الاستثمارية
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

        score = 0
        if sentiment == "إيجابي": score += 1
        if change > 0: score += 1
        if buy > sell: score += 1

        recommendation = "✅ دخول 🟢" if score >= 2 else "⏳ انتظار"
        reason_parts = []

        if percent > 0:
            reason_parts.append("📈 السعر مرتفع")
        if sentiment == "إيجابي":
            reason_parts.append("📰 أخبار إيجابية")
        if buy > sell:
            reason_parts.append("👨‍💼 عدد المشترين أعلى من البائعين")

        reason = " / ".join(reason_parts)

        return {
            "symbol": symbol,
            "price": price,
            "percent": percent,
            "news": sentiment,
            "analyst": f"{buy} شراء / {sell} بيع / {hold} احتفاظ",
            "recommendation": recommendation,
            "reason": reason
        }
    except:
        return None

# عرض بطاقة السهم
def show_stock_card(data):
    logo_url = get_stock_logo(data['symbol'])
    color = "green" if data['percent'] >= 0 else "red"

    st.markdown(f"""
        <div style='border:1px solid #444; border-radius:16px; padding:16px; margin-bottom:20px; background:#111;'>
            <div style='display:flex; align-items:center;'>
                <img src="{logo_url}" width="36" style="margin-left:10px">
                <h4 style='margin:0; color:white;'>{data['symbol'].upper()}</h4>
            </div>
            <p style='color:white;'>السعر: ${data['price']:.2f} / {data['price'] * USD_TO_SAR:.2f} ريال</p>
            <p style='color:{color}; font-weight:bold;'>التغير: {data['percent']:.2f}%</p>
            <p style='color:white;'>📰 الأخبار: {data['news']}</p>
            <p style='color:yellow;'>👨‍💼 المحللون: {data['analyst']}</p>
            <p style='color:cyan; font-weight:bold;'>✅ التوصية: {data['recommendation']}</p>
            <p style='color:orange;'>📌 السبب: {data['reason']}</p>
        </div>
    """, unsafe_allow_html=True)

# واجهة المستخدم
st.markdown("🔍 ابحث عن سهم (اكتب أول حرف فقط مثلاً A)")
query = st.text_input("")

matches = [s for s in HALAL_STOCKS if s.startswith(query.upper())] if query else HALAL_STOCKS

for symbol in matches:
    result = evaluate_opportunity(symbol)
    if result:
        show_stock_card(result)
    else:
        st.warning(f"⚠️ تعذر عرض بيانات السهم {symbol}")
