#stockdata.py
import streamlit as st
import yfinance as yf
import requests
import time

# Page setup
st.set_page_config(layout="wide", page_title="stocks.py Microservice")

# Get quote using yfinance
@st.cache_data(ttl=60)
def get_quote(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        current = info["regularMarketPrice"]
        prev_close = info["previousClose"]
        change = current - prev_close
        percent = (change / prev_close) * 100 if prev_close else 0
        return {
            "symbol": symbol,
            "current": current,
            "change": change,
            "percent": percent
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# Get trending tickers from ApeWisdom
def get_trending():
    try:
        url = "https://apewisdom.io/api/v1.0/filter/all"
        r = requests.get(url, timeout=5)
        return r.json()["results"][:15]
    except Exception as e:
        print(f"Error fetching trending tickers: {e}")
        return []

# Title
st.title("stocks.py Microservice")

# Default tickers
default_tickers = ["SPY", "QQQ", "BTC-USD", "META"]

# Custom ticker input
custom_input = st.text_input("Add your own ticker symbols:", value="")
custom_tickers = [x.strip().upper() for x in custom_input.split(",") if x.strip()]
tickers = default_tickers + custom_tickers

# Layout: stock cards on the left, trending on the right
left_col, right_col = st.columns([3, 1])

# Right side: Trending Tickers styled like stock cards
with right_col:
    st.markdown("### Trending Tickers")

    trending = get_trending()
    if not trending:
        st.info("No trending data available right now.")
    else:
        for i in range(0, len(trending), 2):  # 2 columns per row
            row = st.columns(2)
            for j in range(2):
                if i + j < len(trending):
                    item = trending[i + j]
                    sym = item["ticker"]
                    url = f"https://finance.yahoo.com/quote/{sym}"

                    with row[j]:
                        st.markdown(f"""
                        <div style='background:#111;padding:1.5em;border-radius:16px;text-align:center;
                                    color:#00FF00;box-shadow:0 4px 20px rgba(0,255,0,0.15);'>
                            <div style='color:white;font-size:20px;font-family:sans-serif;margin-bottom:8px;'>{sym}</div>
                            <a href='{url}' target='_blank' style='font-size:14px;color:#1a73e8;'>View on Yahoo Finance</a>
                        </div>
                        """, unsafe_allow_html=True)

# Left side: Live Stock Cards
with left_col:
    st.markdown("### Stocks Data ")
    cols = st.columns(min(len(tickers), 4))
    for i, sym in enumerate(tickers):
        if i % 4 == 0 and i > 0:
            cols = st.columns(min(len(tickers) - i, 4))
        col = cols[i % 4]
        q = get_quote(sym)
        if not q:
            col.error(f"{sym} failed to load")
            continue

        color = "#00FF00" if q["change"] >= 0 else "#FF4B4B"
        col.markdown(f"""
        <div style='background:#111;padding:1.5em;border-radius:16px;text-align:center;
        color:{color};box-shadow:0 4px 20px rgba(0,255,0,0.2);'>
            <div style='color:white;font-size:20px;font-family:sans-serif;margin-bottom:5px;'>{sym}</div>
            <div style='font-size:32px;font-weight:bold;'>{q['current']:.2f}</div>
            <div style='font-size:16px;'>Change: {q['change']:+.2f} ({q['percent']:+.2f}%)</div>
        </div>
        """, unsafe_allow_html=True)

# Optional auto-refresh (manual control)
# time.sleep(60)
# st.experimental_rerun()
