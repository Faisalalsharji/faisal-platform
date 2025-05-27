import streamlit as st import yfinance as yf import pandas as pd import matplotlib.pyplot as plt from datetime import datetime

USERNAME = "faisal" PASSWORD = "faisal2025" USD_TO_SAR = 3.75 WATCHLIST_FILE = "watchlist.csv" PORTFOLIO_FILE = "portfolio.csv" TRADES_FILE = "trades.csv" HALAL_STOCKS = ["AAPL", "GOOG", "MSFT", "NVDA", "TSLA", "AMZN", "META", "ADBE", "INTC", "CRM"]

st.set_page_config(page_title="منصة فيصل - الأسهم الذكية", layout="wide")

تنسيق CSS للتصميم التفاعلي

st.markdown(""" <style> .stock-card { background-color: #1e1e1e; padding: 16px; border-radius: 20px; border: 1px solid #333; margin-bottom: 16px; transition: 0.3s ease; } .stock-card:hover { border: 1px solid gold; transform: scale(1.02); } </style> """, unsafe_allow_html=True)

شعار فيصل الرسمي

st.markdown(""" <div style='text-align:center;padding:10px;'> <img src='https://cdn.jsdelivr.net/gh/0xflair/logos/faisal-bg.png' width='220'/> </div> """, unsafe_allow_html=True)

def login(): st.title("تسجيل الدخول - منصة فيصل") username = st.text_input("اسم المستخدم") password = st.text_input("كلمة المرور", type="password") if st.button("دخول"): if username == USERNAME and password == PASSWORD: st.session_state.logged_in = True st.success("تم تسجيل الدخول") st.rerun() else: st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

def save_watchlist(watchlist): df = pd.DataFrame(watchlist, columns=["stock"]) df.to_csv(WATCHLIST_FILE, index=False)

def load_watchlist(): try: df = pd.read_csv(WATCHLIST_FILE) return df["stock"].tolist() except: return []

def save_portfolio(portfolio): df = pd.DataFrame(portfolio) df.to_csv(PORTFOLIO_FILE, index=False)

def load_portfolio(): try: return pd.read_csv(PORTFOLIO_FILE) except: return pd.DataFrame(columns=["stock", "buy_price", "quantity", "type", "date"])

def save_trades(trades): trades.to_csv(TRADES_FILE, index=False)

def load_trades(): try: return pd.read_csv(TRADES_FILE) except: return pd.DataFrame(columns=["stock", "action", "price", "date"])

def rsi(prices, window=14): delta = prices.diff() gain = delta.clip(lower=0) loss = -1 * delta.clip(upper=0) avg_gain = gain.rolling(window=window).mean() avg_loss = loss.rolling(window=window).mean() rs = avg_gain / avg_loss return 100 - (100 / (1 + rs))

def macd(prices): exp1 = prices.ewm(span=12, adjust=False).mean() exp2 = prices.ewm(span=26, adjust=False).mean() return exp1 - exp2

def dashboard(): st.header("الملخص المالي") trades = load_trades() if not trades.empty: trades["date"] = pd.to_datetime(trades["date"]) trades["month"] = trades["date"].dt.to_period("M") summary = trades.groupby("month")["price"].sum() summary.index = summary.index.astype(str) fig, ax = plt.subplots() ax.plot(summary.index, summary.values) ax.set_title("أداء الأرباح/الخسائر الشهرية") st.pyplot(fig) goal = 1000000 current = summary.sum() percent = (current / goal) * 100 st.progress(min(percent / 100, 1)) st.success(f"التقدم نحو المليون: {current:,.2f} ريال / {goal:,} ريال") else: st.info("لا يوجد صفقات مسجلة بعد.")

def add_trade_ui(): st.header("تسجيل صفقة") stock = st.selectbox("رمز السهم", HALAL_STOCKS) action = st.selectbox("العملية", ["شراء", "بيع"]) price = st.number_input("السعر", min_value=0.0) if st.button("سجل الصفقة"): if stock and price > 0: trades = load_trades() new = pd.DataFrame([{ "stock": stock, "action": action, "price": price, "date": datetime.now().strftime("%Y-%m-%d") }]) trades = pd.concat([trades, new], ignore_index=True) save_trades(trades) st.success("تم تسجيل الصفقة")

def smart_ai_analysis(): st.header("تحليل AI وترتيب الفرص") portfolio = load_portfolio() results = [] if not portfolio.empty: for symbol in portfolio["stock"]: try: data = yf.Ticker(symbol).history(period="60d")["Close"] if len(data) >= 30: rsi_score = rsi(data).iloc[-1] macd_score = macd(data).iloc[-1] score = 0 if rsi_score < 30: score += 1 if macd_score > 0: score += 1 results.append((symbol, score, rsi_score, macd_score)) except: continue results.sort(key=lambda x: x[1], reverse=True) for sym, score, rsi_v, macd_v in results: st.markdown(f"{sym} | RSI: {rsi_v:.2f} | MACD: {macd_v:.2f} | فرصة: {'عالية' if score==2 else 'متوسطة' if score==1 else 'ضعيفة'}") else: st.info("المحفظة فارغة")

def ai_accuracy_report(): st.header("تقييم الذكاء الاصطناعي") trades = load_trades() if not trades.empty: trades["date"] = pd.to_datetime(trades["date"]) win_count = 0 total = 0 for _, row in trades.iterrows(): symbol = row["stock"] price_then = row["price"] try: now = yf.Ticker(symbol).history(period="1d")["Close"].iloc[-1] if (row["action"] == "شراء" and now > price_then) or (row["action"] == "بيع" and now < price_then): win_count += 1 total += 1 except: continue if total > 0: percent = (win_count / total) * 100 st.success(f"دقة التوصيات السابقة: {percent:.2f}%") else: st.info("لا يمكن التقييم حاليًا") else: st.info("لا توجد صفقات للتقييم")

def stock_cards(): st.header("الأسهم") watchlist = load_watchlist()

st.sidebar.title("إدارة قائمة الأسهم")
new_stock = st.sidebar.text_input("أضف سهم")
if st.sidebar.button("إضافة"):
    if new_stock and new_stock.upper() not in watchlist:
        watchlist.append(new_stock.upper())
        save_watchlist(watchlist)
        st.experimental_rerun()

filter_type = st.sidebar.radio("فلتر:", ["الكل", "الحلال فقط"])
sort_order = st.sidebar.radio("ترتيب حسب التغير:", ["الأعلى", "الأقل"])

filtered_list = [s for s in watchlist if s in HALAL_STOCKS] if filter_type == "الحلال فقط" else watchlist
st.button("تحديث الأسعار")  # يدوي الآن فقط

stocks_data = []
for symbol in filtered_list:
    try:
        data = yf.Ticker(symbol)
        price = data.history(period="1d")["Close"].iloc[-1]
        prev = data.history(period="2d")["Close"].iloc[0]
        change = price - prev
        percent = (change / prev) * 100 if prev else 0
        stocks_data.append({
            "symbol": symbol,
            "price": price,
            "sar": price * USD_TO_SAR,
            "change": change,
            "percent": percent,
            "color": "green" if change >= 0 else "red"
        })
    except:
        continue

reverse = True if sort_order == "الأعلى" else False
stocks_data = sorted(stocks_data, key=lambda x: x["percent"], reverse=reverse)

if not stocks_data:
    st.warning("لا توجد أسهم")
else:
    cols = st.columns(3)
    for i, stock in enumerate(stocks_data):
        with cols[i % 3]:
            st.markdown(f"""
            <div class='stock-card'>
                <h4 style='color:white'>{stock['symbol']}</h4>
                <p style='color:white'>${stock['price']:.2f} / {stock['sar']:.2f} SAR</p>
                <p style='color:{stock['color']};font-weight:bold'>{stock['change']:+.2f} ({stock['percent']:+.2f}%)</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("X", key=f"remove_{stock['symbol']}"):
                watchlist.remove(stock['symbol'])
                save_watchlist(watchlist)
                st.experimental_rerun()

def main_app(): st.sidebar.title("القائمة") page = st.sidebar.selectbox("اختر الصفحة", ["الملخص المالي", "تسجيل صفقة", "تحليل AI", "تقييم AI", "الأسهم"]) if page == "الملخص المالي": dashboard() elif page == "تسجيل صفقة": add_trade_ui() elif page == "تحليل AI": smart_ai_analysis() elif page == "تقييم AI": ai_accuracy_report() elif page == "الأسهم": stock_cards()

if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in: login() else: main_app()

