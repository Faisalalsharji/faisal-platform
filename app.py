import streamlit as st import yfinance as yf import pandas as pd import plotly.graph_objects as go import requests

--- إعدادات ---

FINNHUB_API_KEY = "ضع_مفتاحك" EODHD_API_KEY = "ضع_مفتاحك" USD_TO_SAR = 3.75 HALAL_STOCKS = ["AAPL", "MSFT", "TSLA", "NVDA", "GOOG", "AMZN", "META", "ADBE", "INTC", "CRM"]

--- وظائف التحليل ---

def get_news(symbol): try: url = f"https://eodhd.com/api/news?api_token={EODHD_API_KEY}&s={symbol}&limit=1" res = requests.get(url) articles = res.json() if articles: return articles[0]['title'] except: pass return "لا توجد أخبار حاليًا"

def analyze_news(title): positives = ["expands", "growth", "launch", "beat", "strong"] negatives = ["cut", "miss", "drop", "loss", "decline"] for word in positives: if word in title.lower(): return "إيجابي" for word in negatives: if word in title.lower(): return "سلبي" return "محايد"

def get_analyst_opinion(symbol): try: url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={FINNHUB_API_KEY}" res = requests.get(url) rec = res.json() if rec: latest = rec[0] return latest['buy'], latest['sell'], latest['hold'] except: pass return 0, 0, 0

def evaluate_stock(symbol): try: data = yf.Ticker(symbol) hist = data.history(period="2d") if len(hist) < 2: return None price = hist["Close"].iloc[-1] prev = hist["Close"].iloc[0] change = price - prev percent = (change / prev) * 100 if prev else 0 news = get_news(symbol) sentiment = analyze_news(news) buy, sell, hold = get_analyst_opinion(symbol) score = 0 if sentiment == "إيجابي": score += 1 if change > 0: score += 1 if buy > sell: score += 1 return { "symbol": symbol, "price": price, "percent": percent, "news": sentiment, "analyst": f"{buy} شراء / {sell} بيع / {hold} احتفاظ", "recommendation": "دخول" if score >= 2 else "انتظار" } except: return None

--- واجهة البطاقة ---

def show_stock_card(data): color = "green" if data['percent'] >= 0 else "red" st.markdown(f""" <div style='border:1px solid #444; border-radius:12px; padding:16px; margin-bottom:20px; background:#111;'> <h4 style='color:white'>{data['symbol']}</h4> <p style='color:white;'>السعر: ${data['price']:.2f} / {(data['price'] * USD_TO_SAR):.2f} ريال</p> <p style='color:{color}; font-weight:bold;'>التغير: {data['percent']:+.2f}%</p> <p style='color:white;'>📰 تحليل الأخبار: {data['news']}</p> <p style='color:yellow;'>👨‍💼 المحللون: {data['analyst']}</p> <p style='color:cyan;'>✅ التوصية: {data['recommendation']}</p> </div> """, unsafe_allow_html=True)

--- واجهة المستخدم ---

st.set_page_config(page_title="الأسهم الحلال الذكية", layout="wide") st.title("منصة فيصل - الأسهم الحلال الذكية")

query = st.text_input("🔎 ابحث عن سهم (اكتب أول حرف فقط):")

matches = [s for s in HALAL_STOCKS if s.startswith(query.upper())] if query else HALAL_STOCKS

for symbol in matches: result = evaluate_stock(symbol) if result: show_stock_card(result) else: st.warning(f"تعذر عرض بيانات {symbol}")

