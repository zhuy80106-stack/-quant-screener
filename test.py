import streamlit as st
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="Test", page_icon="📈", layout="wide")

st.title("Simple Test")

def fetch_one(symbol):
    try:
        stock = yf.Ticker(f"{symbol}.TW")
        info = stock.info
        if info and info.get('currentPrice'):
            return {
                'symbol': symbol,
                'price': info.get('currentPrice'),
                'pe': info.get('trailingPE', 0)
            }
    except:
        pass
    return None

stocks = ['2330', '2317', '2454', '2412', '2882']

with st.spinner('Fetching...'):
    results = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        for r in as_completed([ex.submit(fetch_one, s) for s in stocks]):
            if r.result():
                results.append(r.result())

st.write(f"Got {len(results)} results:")
for r in results:
    st.write(f"  {r['symbol']}: ${r['price']}, PE: {r['pe']}")