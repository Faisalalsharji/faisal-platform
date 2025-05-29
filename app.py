import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from ta.momentum import RSIIndicator
from ta.trend import MACD
from datetime import datetime, timedelta
import os
import plotly.graph_objects as go

st.set_page_config(page_title="منصة فيصل - الذكاء الصناعي الحقيقي", layout="wide")

FINNHUB_API_KEY = "d0sc3q9r01qkkpluc37gd0sc3q9r01qkkpluc380"
WATCHLIST = ["HOLO", "AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN"]
TRACK_FILE = "recommendation_history.csv"

st.title("📈 أفضل 5 توصيات ذكية لليوم (مدعومة بالأخبار)")

if not os.path.exists(TRACK_FILE):
    pd.DataFrame(columns=["السهم", "دخول", "هدف", "وقف", "نسبة النجاح", "الحالة", "الوقت"]).to_csv(TRACK_FILE, index=False)

recommendations = []

def get_news(symbol):
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')}&to={datetime.now().strftime('%Y-%m-%d')}&token={FINNHUB_API_KEY}"
        response = requests.get(url)
        news = response.json()
        if news and isinstance(news, list):
            latest = news[0]
            headline = latest.get("headline", "لا يوجد عنوان")
            summary = latest.get("summary", "لا يوجد ملخص")
            url = latest.get("url", "")
            return headline, summary, url
    except:
        return None, None, None
    return None, None, None

# تحليل كل سهم
for symbol in WATCHLIST:
    try:
        data = yf.download(symbol, period="7d", interval="1h")
        if data.empty:
            continue

        rsi = RSIIndicator(close=data["Close"].squeeze()).rsi()
        macd = MACD(close=data["Close"].squeeze()).macd_diff()
        volume = data["Volume"]

        latest_rsi = rsi.iloc[-1]
        latest_macd = macd.iloc[-1]
        latest_volume = volume.iloc[-1]
        price_now = data["Close"].iloc[-1]

        entry_price = round(price_now, 2)
        target_price = round(entry_price * 1.08, 2)
        stop_loss = round(entry_price * 0.96, 2)

        success_rate = 50
        analysis = []

        if latest_rsi > 55:
            success_rate += 10
            analysis.append("RSI إيجابي")
        if latest_macd > 0:
            success_rate += 15
            analysis.append("MACD صاعد")
        if latest_volume > volume.mean():
            success_rate += 10
            analysis.append("حجم تداول مرتفع")

        last_closes = data['Close'].iloc[-3:].tolist()
        if all(x < y for x, y in zip(last_closes, last_closes[1:])):
            success_rate += 10
            analysis.append("نمط تصاعدي في الشموع")

        news_headline, news_summary, news_url = get_news(symbol)

        if isinstance(news_headline, str) and any(word in news_headline.lower() for word in ["beat", "growth", "partner", "up", "record"]):
            success_rate += 5
            analysis.append("خبر إيجابي")
        elif isinstance(news_headline, str) and any(word in news_headline.lower() for word in ["drop", "loss", "lawsuit", "investigation"]):
            success_rate -= 10
            analysis.append("خبر سلبي")

        if success_rate >= 60:
            recommendations.append({
                "symbol": symbol,
                "entry": entry_price,
                "target": target_price,
                "stop": stop_loss,
                "success_rate": success_rate,
                "analysis": analysis,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "data": data[-50:],
                "news": news_headline,
                "url": news_url
            })

    except Exception as e:
        st.error(f"❌ خطأ في تحليل {symbol}: {e}")

recommendations = sorted(recommendations, key=lambda x: x['success_rate'], reverse=True)[:5]

for rec in recommendations:
    st.subheader(f"📌 {rec['symbol']}")
    st.markdown(f"**✅ دخول:** {rec['entry']} | **🎯 هدف:** {rec['target']} | **⛔ وقف خسارة:** {rec['stop']}")
    st.markdown("**🕒 المدى:** قصير (حتى نهاية اليوم)")
    st.markdown(f"**📊 التحليل الفني:** {' | '.join(rec['analysis'])}")
    st.markdown(f"**🔢 نسبة نجاح التوصية:** ✅ {rec['success_rate']}%")
    st.markdown(f"**⏰ وقت التوصية:** {rec['time']}")

    if isinstance(rec['news'], str):
        st.markdown(f"**📰 أهم خبر:** [{rec['news']}]({rec['url']})")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=rec['data'].index,
        open=rec['data']['Open'],
        high=rec['data']['High'],
        low=rec['data']['Low'],
        close=rec['data']['Close']
    ))
    fig.update_layout(title=f"الرسم البياني لـ {rec['symbol']}", height=300)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    history_df = pd.read_csv(TRACK_FILE)
    if not ((history_df['السهم'] == rec['symbol']) & (history_df['دخول'] == rec['entry'])).any():
        new_row = pd.DataFrame([{
            "السهم": rec['symbol'],
            "دخول": rec['entry'],
            "هدف": rec['target'],
            "وقف": rec['stop'],
            "نسبة النجاح": f"{rec['success_rate']}%",
            "الحالة": "⏳ مستمرة",
            "الوقت": rec['time']
        }])
        new_row.to_csv(TRACK_FILE, mode='a', header=False, index=False)

with st.expander("📜 سجل التوصيات السابقة"):
    hist = pd.read_csv(TRACK_FILE)
    st.dataframe(hist[::-1], use_container_width=True)
