import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(
    page_title="منصة فيصل - الأسهم الذكية",
    layout="centered"
)

USERNAME = "faisal"
PASSWORD = "faisal2025"
USD_TO_SAR = 3.75

stock_list = {
    "آبل (AAPL)": "AAPL",
    "نفيديا (NVDA)": "NVDA",
    "تسلا (TSLA)": "TSLA",
    "قوقل (GOOG)": "GOOG",
    "أمازون (AMZN)": "AMZN"
}
