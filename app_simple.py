import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Quant Screener", page_icon="📈", layout="wide")

st.title("📈 Quant Stock Screener")

with st.sidebar:
    st.header("⚙️ 設定")
    market = st.selectbox("市場", ["台灣", "美國"])
    market_val = "Taiwan" if market == "台灣" else "USA"

# 台灣熱門股票列表
TW_STOCKS = ['2330', '2317', '2454', '2412', '2882', '2891', '1301', '1326', '1215', '3008',
             '2382', '2451', '2308', '2207', '2227', '2231', '8046', '2105', '2609', '2474']

US_STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'JNJ', 'V',
             'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'CRM', 'NFLX', 'CSCO']

stocks = TW_STOCKS if market_val == "Taiwan" else US_STOCKS

# 按鈕強制刷新
if 'cache_cleared' not in st.session_state:
    st.session_state.cache_cleared = True
    
if st.button("🔄 強制重新整理"):
    for key in list(st.session_state.keys()):
        if key not in ['cache_cleared']:
            del st.session_state[key]
    st.rerun()

@st.cache_data(ttl=60)
def fetch_stock(s):
    try:
        suffix = ".TW" if market_val == "Taiwan" else ""
        stock = yf.Ticker(s + suffix)
        info = stock.info
        if not info or not info.get('currentPrice'):
            return None
        return {
            'symbol': s,
            'name': info.get('shortName', s),
            'price': info.get('currentPrice', 0),
            'pe': info.get('trailingPE', 0) or 0,
            'pb': info.get('priceToBook', 0) or 0,
            'div_yield': (info.get('dividendYield', 0) or 0) * 100,
            'roe': (info.get('returnOnEquity', 0) or 0) * 100,
            'yoy': (info.get('revenueGrowth', 0) or 0) * 100
        }
    except Exception as e:
        return None

with st.spinner("正在讀取股票資料..."):
    results = []
    for s in stocks[:20]:
        data = fetch_stock(s)
        if data:
            results.append(data)
    
st.success(f"✅ 成功讀取 {len(results)} 筆資料")

if results:
    df = pd.DataFrame(results)
    st.dataframe(df)
else:
    st.error("❌ 無法讀取資料，請檢查網路連線")