import streamlit as st import yfinance as yf import pandas as pd import requests

FINNHUB_API_KEY = "ضع_مفتاح_finnhub_هنا" EODHD_API_KEY = "ضع_مفتاح_eodhd_هنا"

USERNAME = "faisal" PASSWORD = "faisal2025" USD_TO_SAR = 3.75 WATCHLIST_FILE = "watchlist.csv" HALAL_STOCKS = ["AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN", "META", "ADBE", "INTC", "CRM"]

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="wide")

st.markdown(""" <div style='text-align:center;padding:10px;'> <img src='https://i.imgur.com/lwxQfxT.png' width='120'/> </div> """, unsafe_allow_html=True)

def login(): st.title("تسجيل الدخول - منصة فيصل") username = st.text_input("اسم المستخدم") password = st.text_input("كلمة المرور", type="password") if st.button("دخول"): if username == USERNAME and password == PASSWORD: st.session_state.logged_in = True st.success("تم تسجيل الدخول") st.rerun() else: st.error("بيانات الدخول غير صحيحة")

def save_watchlist(watchlist): df = pd.DataFrame(watchlist, columns=["stock"]) df.to_csv(WATCHLIST_FILE, index=False)

def load_watchlist(): try: df = pd.read_csv(WATCHLIST_FILE) return df["stock"].tolist() except: return []

def fetch_news(symbol): try: url = f"https://eodhd.com/api/news?api_token={EODHD_API_KEY}&s={symbol}&limit=1" res = requests.get(url) articles = res.json() if articles: return articles[0]['title'] except: return "لا توجد أخبار حالياً"

def fetch_recommendation(symbol): try: url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={FINNHUB_API_KEY}" res = requests.get(url) recs = res.json() if recs: latest = recs[0] buy = latest['buy'] sell = latest['sell'] if buy > sell: return "توصية: شراء" elif sell > buy: return "توصية: بيع" else: return "توصية: احتفاظ" except: return "لا توجد توصية حالياً"

def stock_cards(): st.header("الأسهم") watchlist = load_watchlist()

filter_type = st.radio("عرض الأسهم:", ["الكل", "الحلال فقط"], horizontal=True)
filtered_list = [s for s in watchlist if s in HALAL_STOCKS] if filter_type == "الحلال فقط" else watchlist

new_stock = st.text_input("أضف سهم إلى قائمة المراقبة")
if st.button("إضافة"):
    if new_stock and new_stock.upper() not in watchlist:
        watchlist.append(new_stock.upper())
        save_watchlist([[s] for s in watchlist])
        st.success("تمت الإضافة")

if not filtered_list:
    st.warning("لا توجد أسهم في القائمة")
else:
    cols = st.columns(3)
    for i, symbol in enumerate(filtered_list):
        try:
            data = yf.Ticker(symbol)
            info = data.info
            price = data.history(period="1d")["Close"].iloc[-1]
            prev_close = data.history(period="2d")["Close"].iloc[0]
            change = price - prev_close
            percent = (change / prev_close) * 100 if prev_close else 0
            color = "green" if change >= 0 else "red"
            news = fetch_news(symbol)
            recommendation = fetch_recommendation(symbol)
            with cols[i % 3]:
                st.markdown(f"""
                <div style='background-color:#111;padding:16px;border-radius:12px;margin-bottom:16px;border:1px solid #333;'>
                    <h4 style='margin:0;color:white'>{info.get('shortName', symbol)} <span style='font-size:0.8em;color:#999;'>({symbol})</span></h4>
                    <p style='margin:4px 0;font-size:1.1em;color:white'>${price:.2f} USD / {(price * USD_TO_SAR):.2f} SAR</p>
                    <p style='margin:0;color:{color};font-weight:bold'>
                        {change:+.2f} ({percent:+.2f}%)
                    </p>
                    <p style='color:white;font-size:0.9em;'>أخبار: {news}</p>
                    <p style='color:yellow;font-weight:bold;'>{recommendation}</p>
                </div>
                """, unsafe_allow_html=True)
        except:
            with cols[i % 3]:
                st.error(f"فشل في تحميل {symbol}")

def main_app(): st.sidebar.title("القائمة") page = st.sidebar.selectbox("اختر الصفحة", ["الأسهم"]) if page == "الأسهم": stock_cards()

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in: login()

