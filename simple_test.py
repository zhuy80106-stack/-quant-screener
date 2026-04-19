import streamlit as st
import yfinance as yf

st.title("Simple Test - Taiwan Stocks")

stock = yf.Ticker("2330.TW")
info = stock.info
st.write(f"2330 Price: {info.get('currentPrice')}")
st.write(f"2330 PE: {info.get('trailingPE')}")