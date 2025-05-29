import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD
from datetime import datetime
import os

st.set_page_config(page_title="منصة فيصل - الذكاء الصناعي الحقيقي", layout="wide")

WATCHLIST = ["HOLO", "AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN"]
TRACK_FILE = "recommendation_history.csv"

st.title("📈 أفضل 5 توصيات ذكية لليوم")

# إنشاء سجل التوصيات إذا لم يكن موجودًا
if not os.path.exists(TRACK_FILE):
    pd.DataFrame(columns=["السهم", "دخول", "هدف", "وقف", "نسبة النجاح", "الحالة", "الوقت"]).to_csv(TRACK_FILE, index=False)

recommendations = []

# تحليل كل سهم
for symbol in WATCHLIST:
    try:
        data = yf.download(symbol, period="7d", interval="1h")
        if data.empty:
            continue

        rsi = RSIIndicator(close=data["Close"]).rsi()
        macd = MACD(close=data["Close"]).macd_diff()
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

        if success_rate >= 60:
            recommendations.append({
                "symbol": symbol,
                "entry": entry_price,
                "target": target_price,
                "stop": stop_loss,
                "success_rate": success_rate,
                "analysis": analysis,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

    except Exception as e:
        st.error(f"❌ خطأ في تحليل {symbol}: {e}")

# ترتيب التوصيات حسب أعلى نسبة نجاح وعرض أفضل 5
recommendations = sorted(recommendations, key=lambda x: x['success_rate'], reverse=True)[:5]

for rec in recommendations:
    st.subheader(f"📌 {rec['symbol']}")
    st.markdown(f"**✅ دخول:** {rec['entry']} | **🎯 هدف:** {rec['target']} | **⛔ وقف خسارة:** {rec['stop']}")
    st.markdown("**🕒 المدى:** قصير (حتى نهاية اليوم)")
    st.markdown(f"**📊 التحليل الفني:** {' | '.join(rec['analysis'])}")
    st.markdown(f"**🔢 نسبة نجاح التوصية:** ✅ {rec['success_rate']}%")
    st.markdown(f"**⏰ وقت التوصية:** {rec['time']}")
    st.markdown("---")

    # حفظ التوصية في سجل الأداء إذا لم تكن موجودة
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

# عرض سجل التوصيات السابقة
with st.expander("📜 سجل التوصيات السابقة"):
    hist = pd.read_csv(TRACK_FILE)
    st.dataframe(hist[::-1], use_container_width=True)
