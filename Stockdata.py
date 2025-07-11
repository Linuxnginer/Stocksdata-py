#stockdata.py
import streamlit as st
import yfinance as yf
import requests
from datetime import datetime, timedelta

# Page setup
st.set_page_config(layout="wide", page_title="stocks.py Microservice")

# Quote retrieval
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

# Trending tickers from ApeWisdom
def get_trending():
    try:
        url = "https://apewisdom.io/api/v1.0/filter/all"
        r = requests.get(url, timeout=5)
        return r.json()["results"][:15]
    except Exception as e:
        print(f"Error fetching trending tickers: {e}")
        return []

# Gemini 2.5 Flash Chat Function
def ask_gemini(message, api_key):
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key
        }
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": message}
                    ]
                }
            ]
        }
        response = requests.post(url, headers=headers, json=body, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error: {e}"

# Title
st.title("stocks.py Microservice")

# Layout: stock cards (left), trending tickers (right)
left_col, right_col = st.columns([3, 1])

# --- RIGHT: Trending Tickers ---
with right_col:
    st.markdown("### Trending Tickers")
    trending = get_trending()
    if not trending:
        st.info("No trending data available right now.")
    else:
        for i in range(0, len(trending), 2):
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

# --- LEFT: Stock Cards ---
with left_col:
    st.markdown("### Stocks Data")

    default_values = ["SPY", "QQQ", "BTC-USD", "META"]
    symbols = []
    input_cols = st.columns(4)
    for i in range(4):
        sym = input_cols[i].text_input(f"Symbol {i+1}", value=default_values[i]).upper().strip()
        symbols.append(sym)

    row1, row2 = st.columns(2), st.columns(2)
    rows = row1 + row2

    for i, sym in enumerate(symbols):
        q = get_quote(sym)
        with rows[i]:
            if not q:
                st.error(f"{sym} failed to load")
                continue
            color = "#00FF00" if q["change"] >= 0 else "#FF4B4B"
            st.markdown(f"""
            <div style='background:#111;padding:1.5em;border-radius:16px;text-align:center;
            color:{color};box-shadow:0 4px 20px rgba(0,255,0,0.2);'>
                <div style='color:white;font-size:20px;font-family:sans-serif;margin-bottom:5px;'>{sym}</div>
                <div style='font-size:32px;font-weight:bold;'>{q['current']:.2f}</div>
                <div style='font-size:16px;'>Change: {q['change']:+.2f} ({q['percent']:+.2f}%)</div>
            </div>
            """, unsafe_allow_html=True)

# --- LEFT (bottom): Gemini Chat Assistant ---
with left_col:
    st.markdown("### Stock AI Assistant")

    gemini_key = st.text_input("Gemini API Key", type="password")
    user_message = st.text_area("Ask a stock-related question")

    if st.button("Ask Gemini") and user_message and gemini_key:
        with st.spinner("Thinking..."):
            reply = ask_gemini(user_message, gemini_key)
            st.markdown("#### Response:")
            st.write(reply)

