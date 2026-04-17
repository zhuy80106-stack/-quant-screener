import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Quant Stock Screener", page_icon="📈", layout="wide")

COLORS = {
    'bg': '#0f0f1a',
    'card': 'rgba(255,255,255,0.05)',
    'border': 'rgba(255,255,255,0.1)',
    'primary': '#e94560',
    'success': '#00d9a5',
    'text': '#eaeaea',
    'secondary': '#16213e'
}

st.markdown(f'''
    <style>
    .stApp {{background-color: {COLORS['bg']}; color: {COLORS['text']};}}
    .css-1d391kg {{background-color: {COLORS['secondary']};}}
    div.stButton > button {{
        background-color: {COLORS['primary']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
    }}
    div.stButton > button:hover {{
        background-color: #ff6b6b;
    }}
    .metric-card {{
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
    }}
    input[type="range"] {{
        -webkit-tap-highlight-color: transparent;
        touch-action: pan-x;
    }}
    .stSlider {{
        padding-bottom: 20px;
    }}
    div[data-baseweb="slider"] {{
        touch-action: none;
    }}
    </style>
''', unsafe_allow_html=True)

TEXT = {
    'en': {
        'settings': '⚙️ Settings',
        'market': 'Market',
        'taiwan': 'Taiwan',
        'usa': 'USA',
        'strategy_template': '📋 Strategy Template',
        'select_strategy': 'Select Strategy',
        'value_investing': 'Value Investing',
        'quality_growth': 'Quality Growth',
        'high_dividend': 'High Dividend',
        'custom': 'Custom',
        'pe_ratio': 'P/E Ratio (max)',
        'pb_ratio': 'P/B Ratio (max)',
        'dividend_yield': 'Dividend Yield (%) (min)',
        'roe': 'ROE (%) (min)',
        'debt_ratio': 'Debt Ratio (%) (max)',
        'profit_margin': 'Profit Margin (%) (min)',
        'screener': '🔍 Screener',
        'backtest': '📊 Backtest',
        'analytics': '📈 Analytics',
        'multi_factor': 'Multi-Factor Stock Screener',
        'loading_stock': 'Loading stock list...',
        'fetching': 'Fetching stock data (parallel)...',
        'refresh': '🔄 Refresh Data',
        'results': 'Results',
        'no_match': 'No stocks match your criteria',
        'unable_fetch': 'Unable to fetch stock data. Please try again.',
        'backtest_engine': 'Backtesting Engine',
        'filter_first': 'Please filter stocks in the Screener first',
        'start_date': 'Start Date',
        'end_date': 'End Date',
        'run_backtest': '🚀 Run Backtest',
        'running': 'Running backtest...',
        'performance': '📊 Performance Comparison',
        'strategy_return': 'Strategy Return',
        'annual_return': 'Annual Return',
        'benchmark_return': 'Benchmark Return',
        'alpha': 'Alpha',
        'volatility': 'Volatility',
        'sharpe': 'Sharpe Ratio',
        'sortino': 'Sortino Ratio',
        'cumulative': '📈 Cumulative Return',
        'strategy': 'Strategy',
        'benchmark': 'Benchmark',
        'date': 'Date',
        'return_pct': 'Return (%)',
        'backtest_fail': 'Backtest failed. Please check your stock selection.',
        'strategy_analytics': 'Strategy Analytics',
        'sector_dist': '🏭 Sector Distribution',
        'sector_title': 'Stock Sector Distribution',
        'key_metrics': '📊 Key Metrics Summary',
        'avg_pe': 'Avg P/E',
        'avg_pb': 'Avg P/B',
        'avg_div': 'Avg Dividend',
        'avg_roe': 'Avg ROE',
        'metrics_dist': '📈 Metrics Distribution',
        'pe_div': 'P/E & Dividend Yield Distribution',
        'growth': 'Growth',
        'na': 'N/A',
    },
    'zh': {
        'settings': '⚙️ 設定',
        'market': '市場',
        'taiwan': '台灣',
        'usa': '美國',
        'strategy_template': '📋 策略模板',
        'select_strategy': '選擇策略',
        'value_investing': '價值投資型',
        'quality_growth': '品質成長型',
        'high_dividend': '高股息型',
        'custom': '自訂',
        'pe_ratio': '本益比 (最高)',
        'pb_ratio': '股價淨值比 (最高)',
        'dividend_yield': '殖利率 (%) (最低)',
        'roe': 'ROE (%) (最低)',
        'debt_ratio': '負債比 (%) (最高)',
        'profit_margin': '營業利益率 (%) (最低)',
        'screener': '🔍 選股器',
        'backtest': '📊 回測',
        'analytics': '📈 分析',
        'multi_factor': '多維度選股器',
        'loading_stock': '載入股票列表...',
        'fetching': '分析股票中 (平行處理)...',
        'refresh': '🔄 重新整理',
        'results': '篩選結果',
        'no_match': '沒有符合條件的股票',
        'unable_fetch': '無法獲取股票數據，請重試',
        'backtest_engine': '回測系統',
        'filter_first': '請先在選股器中篩選股票',
        'start_date': '開始日期',
        'end_date': '結束日期',
        'run_backtest': '🚀 開始回測',
        'running': '執行回測中...',
        'performance': '📊 績效對比',
        'strategy_return': '策略報酬',
        'annual_return': '年化報酬',
        'benchmark_return': '大盤報酬',
        'alpha': '超額報酬',
        'volatility': '波動率',
        'sharpe': '夏普比率',
        'sortino': '索提諾比率',
        'cumulative': '📈 累積報酬率走勢',
        'strategy': '策略',
        'benchmark': '大盤',
        'date': '日期',
        'return_pct': '報酬率 (%)',
        'backtest_fail': '回測失敗，請檢查選股結果',
        'strategy_analytics': '策略分析',
        'sector_dist': '🏭 產業分佈',
        'sector_title': '股票產業分佈',
        'key_metrics': '📊 關鍵指標統計',
        'avg_pe': '平均 P/E',
        'avg_pb': '平均 P/B',
        'avg_div': '平均殖利率',
        'avg_roe': '平均 ROE',
        'metrics_dist': '📈 指標分布',
        'pe_div': 'P/E 與殖利率分布',
        'growth': '成長中',
        'na': '無資料',
    }
}

def t(key):
    lang = st.session_state.get('lang', 'en')
    return TEXT[lang].get(key, TEXT['en'][key])

def is_valid_taiwan_stock(stock_id):
    if not stock_id:
        return False
    if stock_id.endswith(('T', 'B', 'D', 'R')):
        return False
    if len(stock_id) == 6 and stock_id.isdigit():
        return False
    if len(stock_id) != 4:
        return False
    if not stock_id.isdigit():
        return False
    return True

@st.cache_data(ttl=1800)
def get_taiwan_stocks():
    default_stocks = ['2330', '2317', '2454', '3034', '2412', '2882', '2891', '1301', '1326', '1215',
            '3008', '2382', '2451', '2308', '2207', '2227', '2231', '8046', '2105', '2609',
            '2474', '2449', '2377', '2353', '2344', '2327', '2315', '2303', '2297', '2288',
            '2408', '2409', '2413', '2417', '2420', '2421', '2425', '2427', '2428', '2430',
            '2431', '2433', '2434', '2436', '2437', '2438', '2441', '2443', '2444', '2445']
    try:
        url = "https://api.finmindtrade.com/api/v4/data"
        params = {"dataset": "TaiwanStockInfo", "data": ""}
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if 'data' in data and data['data']:
                df = pd.DataFrame(data['data'])
                stocks = df['stock_id'].tolist()[:500]
                valid = [s for s in stocks if is_valid_taiwan_stock(s)]
                if valid:
                    return valid
    except Exception as e:
        print(f"API error: {e}")
    return default_stocks

@st.cache_data(ttl=3600)
def get_us_stocks():
    sp500 = ['A', 'AAL', 'AAPL', 'ABBV', 'ABC', 'ABMD', 'ACN', 'ADBE', 'ADI', 'ADM',
             'ADP', 'ADSK', 'AEE', 'AEP', 'AES', 'AFL', 'AIG', 'AIV', 'AMAT', 'AMGN',
             'AMP', 'AMT', 'AMZN', 'ANET', 'ANSS', 'ANTM', 'AON', 'APA', 'APD', 'APH',
             'APTV', 'ARE', 'ATO', 'AVB', 'AVGO', 'AWK', 'AXP', 'AZO', 'BA', 'BAC',
             'BAX', 'BBY', 'BDX', 'BEN', 'BHF', 'BK', 'BKNG', 'BLK', 'BMY', 'BR',
             'BSX', 'BWA', 'BXP', 'C', 'CAG', 'CAH', 'CAT', 'CB', 'CBOE', 'CBRE',
             'CCI', 'CDNS', 'CDW', 'CE', 'CHKP', 'CI', 'CINF', 'CL', 'CLX', 'CME',
             'CNC', 'COF', 'COO', 'COST', 'CRM', 'CSCO', 'CSX', 'CTAS', 'CTSH', 'CVS',
             'CVX', 'D', 'DAL', 'DD', 'DE', 'DFS', 'DG', 'DGX', 'DHI', 'DHR',
             'DIS', 'DLR', 'DLTR', 'DOV', 'DOW', 'DPZ', 'DRI', 'DTE', 'DUK', 'DVA',
             'DVN', 'DXC', 'EA', 'EBAY', 'ECL', 'ED', 'EIX', 'EL', 'EMR', 'EOG',
             'EQIX', 'EQR', 'ES', 'ESS', 'ETN', 'ETR', 'EXC', 'EXPD', 'EXPE', 'EXR',
             'F', 'FANG', 'FAST', 'FCX', 'FDX', 'FE', 'FFIV', 'FIS', 'FISV', 'FLT',
             'FMC', 'FRC', 'FRT', 'FSLR', 'FTNT', 'GD', 'GE', 'GILD', 'GIS', 'GL',
             'GM', 'GNRC', 'GOOG', 'GOOGL', 'GPC', 'GPN', 'GS', 'GWW', 'HAL', 'HAS',
             'HBAN', 'HCA', 'HD', 'HES', 'HIG', 'HLT', 'HOLX', 'HON', 'HP', 'HPE',
             'HPQ', 'HR', 'HRL', 'HSIC', 'HST', 'HSY', 'HUM', 'HWM', 'IBM', 'ICE',
             'IDXX', 'IEX', 'IFF', 'ILMN', 'INCY', 'INFO', 'INTC', 'INTU', 'INVH', 'IP',
             'IPG', 'IQV', 'IR', 'IRM', 'ISRG', 'IT', 'ITW', 'IVZ', 'J', 'JBHT',
             'JCI', 'JKHY', 'JNJ', 'JPM', 'K', 'KEY', 'KMB', 'KMX', 'KO', 'KR',
             'L', 'LDOS', 'LEG', 'LEN', 'LH', 'LHX', 'LIN', 'LKQ', 'LLY', 'LMT',
             'LNC', 'LNT', 'LOW', 'LRCX', 'LUV', 'LVS', 'LYB', 'LYV', 'MA', 'MAA',
             'MAR', 'MAS', 'MCD', 'MCHP', 'MCK', 'MCO', 'MDLZ', 'MDT', 'MET', 'MGM',
             'MHK', 'MKC', 'MLM', 'MMC', 'MMM', 'MO', 'MOS', 'MPC', 'MRK', 'MRO',
             'MS', 'MSCI', 'MTCH', 'MTD', 'MU', 'META', 'NEE', 'NEM', 'NFLX', 'NI',
             'NKE', 'NOC', 'NOW', 'NRG', 'NSC', 'NTAP', 'NTRS', 'NUE', 'NVDA', 'NVR',
             'NXPI', 'O', 'ODFL', 'OKTA', 'OMC', 'ON', 'ORCL', 'ORLY', 'OXY', 'PACC',
             'PARA', 'PAYC', 'PBCT', 'PCAR', 'PCG', 'PEAK', 'PEG', 'PFE', 'PFG',
             'PG', 'PGR', 'PH', 'PHM', 'PKG', 'PKI', 'PLD', 'PM', 'PNC', 'PNW',
             'POOL', 'PPG', 'PPL', 'PRU', 'PSA', 'PSX', 'PTC', 'PWR', 'PYPL',
             'QCOM', 'RCL', 'RE', 'REG', 'REGN', 'RF', 'RHI', 'RMD', 'ROK', 'ROL',
             'ROP', 'ROST', 'RSG', 'RTX', 'RXN', 'S', 'SBAC', 'SBUX', 'SCHW', 'SEDG',
             'SEE', 'SHW', 'SIRI', 'SLB', 'SLG', 'SNA', 'SNPS', 'SO', 'SPG', 'SPGI',
             'SRE', 'STZ', 'SWK', 'SWKS', 'SYF', 'SYK', 'SYY', 'T', 'TAP', 'TDG',
             'TEL', 'TER', 'TFC', 'TGT', 'TIF', 'TJX', 'TMO', 'TMUS', 'TROW', 'TRV',
             'TSCO', 'TSLA', 'TSN', 'TT', 'TTWO', 'TXN', 'TXT', 'TYL', 'UHS', 'ULTA',
             'UNH', 'UNP', 'UPS', 'URI', 'USB', 'V', 'VFC', 'VICI', 'VLO', 'VMC',
             'VRSK', 'VRSN', 'VRTX', 'VZ', 'WAB', 'WAT', 'WBA', 'WBD', 'WDAY', 'WDC',
             'WEC', 'WELL', 'WFC', 'WHR', 'WMB', 'WMT', 'WRB', 'WST', 'WTW', 'WY',
             'XEL', 'XOM', 'XRAY', 'YUM', 'YUMC', 'ZBH', 'ZBRA', 'ZION', 'ZTS']
    return list(set(sp500))[:200]

def fetch_stock_metrics(symbol, market):
    try:
        if market == 'Taiwan':
            symbol_yf = f"{symbol}.TW"
        else:
            symbol_yf = symbol
        
        stock = yf.Ticker(symbol_yf)
        
        info = stock.info
        if not info or info.get('regularMarketPrice') is None:
            hist = stock.history(period="2y")
            if hist.empty or len(hist) < 10:
                return None
        
        try:
            actions = stock.dividends
            if not actions.empty and len(actions) >= 2:
                last_div = actions.iloc[-1]
                current_price = info.get('currentPrice') if info else hist['Close'].iloc[-1]
                div_yield = (last_div / current_price * 100) if current_price and current_price > 0 else 0
            else:
                div_yield = info.get('dividendYield') * 100 if info and info.get('dividendYield') else 0
        except:
            div_yield = info.get('dividendYield') * 100 if info and info.get('dividendYield') else 0
        
        if not info:
            return None
        
        pe = info.get('trailingPE')
        pb = info.get('priceToBook')
        is_growth = False
        
        if pe is None or not isinstance(pe, (int, float)) or pe <= 0 or pe > 500:
            pe = 0
            if info.get('trailingPE') and info.get('trailingPE') < 0:
                is_growth = True
        else:
            pe = float(pe)
            
        if pb is None or not isinstance(pb, (int, float)) or pb <= 0:
            pb = 0
        else:
            pb = float(pb)
            
        if div_yield is None or not isinstance(div_yield, (int, float)) or div_yield < 0:
            div_yield = 0
        elif div_yield > 20:
            div_yield = 20
        
        roe = 0
        if info.get('returnOnEquity'):
            try:
                roe = float(info.get('returnOnEquity')) * 100
            except:
                roe = 0
            
        debt = 0
        if info.get('debtToEquity'):
            try:
                debt = float(info.get('debtToEquity'))
            except:
                debt = 0
        
        profit_margin = 0
        if info.get('profitMargins'):
            try:
                profit_margin = float(info.get('profitMargins')) * 100
            except:
                profit_margin = 0
        
        yoy = 0
        if info.get('revenueGrowth'):
            try:
                yoy = float(info.get('revenueGrowth')) * 100
            except:
                yoy = 0
        
        eps_growth = 0
        if info.get('earningsGrowth'):
            try:
                eps_growth = float(info.get('earningsGrowth')) * 100
            except:
                eps_growth = 0
        
        price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        if not price:
            return None
            
        return {
            'symbol': symbol,
            'name': info.get('shortName', symbol),
            'sector': info.get('sector') or 'Technology',
            'pe': pe,
            'pb': pb,
            'div_yield': div_yield,
            'roe': roe,
            'debt': debt,
            'profit_margin': profit_margin,
            'price': price,
            'is_growth': is_growth,
            'yoy': yoy,
            'eps_growth': eps_growth
        }
    except:
        return None

@st.cache_data(ttl=3600)
def get_all_metrics(stock_list, market):
    results = []
    seen = set()
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(fetch_stock_metrics, s, market): s for s in stock_list}
        for future in as_completed(futures):
            result = future.result()
            if result and result['symbol'] not in seen:
                seen.add(result['symbol'])
                results.append(result)
    return results

@st.cache_data(ttl=3600)
def run_backtest(symbols, market, start_date, end_date):
    if not symbols:
        return None, None
    
    benchmark = "^TWII" if market == 'Taiwan' else "^GSPC"
    
    try:
        tickers = symbols[:50] + [benchmark]
        data = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)['Close']
        
        if data.empty or data.dropna().empty:
            return None, None
        
        data = data.dropna()
        returns = data.pct_change().dropna()
        
        port_ret = returns[symbols[:50]].mean(axis=1)
        bench_ret = returns[benchmark]
        
        port_cum = (1 + port_ret).cumprod() - 1
        bench_cum = (1 + bench_ret).cumprod() - 1
        
        return port_cum, bench_cum
    except:
        return None, None

def calc_metrics(returns):
    if returns is None or len(returns) == 0:
        return {}
    total = returns.iloc[-1] if len(returns) > 0 else 0
    annual = (1 + total) ** (252 / max(len(returns), 1)) - 1 if len(returns) > 0 else 0
    volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0
    sharpe = annual / volatility if volatility > 0 else 0
    downside = returns[returns < 0].std() * np.sqrt(252) if len(returns[returns < 0]) > 0 else volatility
    sortino = annual / downside if downside > 0 else 0
    cummax = returns.cumsum().cummax()
    drawdown = (returns.cumsum() - cummax)
    max_dd = drawdown.min() if len(drawdown) > 0 else 0
    return {
        'total_return': total * 100,
        'annual_return': annual * 100,
        'volatility': volatility * 100,
        'sharpe': sharpe,
        'sortino': sortino,
        'max_drawdown': max_dd * 100
    }

def format_value(val, field):
    if val == 0 or val is None:
        return t('na')
    if field in ['pe', 'pb', 'div_yield', 'roe', 'profit_margin']:
        return f"{val:.2f}"

def calc_score(row):
    score = 0
    if row['pe'] > 0:
        score += max(0, 30 - row['pe'])
    if row['pb'] > 0:
        score += max(0, 20 - row['pb'])
    score += row['div_yield'] * 2
    score += row['roe'] * 0.5
    if row['yoy'] > 0:
        score += min(row['yoy'], 20)
    if row['eps_growth'] > 0:
        score += min(row['eps_growth'], 10)
    return round(score, 1)
    return str(val)

st.title("📈 Quant Stock Screener")
st.caption(f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if 'lang' not in st.session_state:
    st.session_state.lang = 'en'

with st.sidebar:
    st.header(t('settings'))
    lang = st.selectbox("Language / 語言", ["English", "中文"], index=0)
    st.session_state.lang = 'en' if lang == "English" else 'zh'
    
    market = st.selectbox(t('market'), [t('taiwan'), t('usa')])
    market_val = 'Taiwan' if market == t('taiwan') else 'USA'
    
    st.subheader(t('strategy_template'))
    strategy = st.selectbox(
        t('select_strategy'),
        [t('value_investing'), t('quality_growth'), t('high_dividend'), t('custom')]
    )
    
    params = {}
    if strategy == t('value_investing'):
        params['pe'] = st.slider(t('pe_ratio'), 0, 50, 20, 1)
        params['pb'] = st.slider(t('pb_ratio'), 0.0, 10.0, 3.0, 0.1)
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 15.0, 2.0, 0.1)
    elif strategy == t('quality_growth'):
        params['roe'] = st.slider(t('roe'), 0, 50, 15, 1)
        params['debt'] = st.slider(t('debt_ratio'), 0, 100, 80, 5)
        params['profit_margin'] = st.slider(t('profit_margin'), 0, 50, 10, 1)
    elif strategy == t('high_dividend'):
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 15.0, 4.0, 0.1)
    else:
        params['pe'] = st.slider(t('pe_ratio'), 0, 50, 25, 1)
        params['pb'] = st.slider(t('pb_ratio'), 0.0, 10.0, 3.0, 0.1)
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 15.0, 2.0, 0.1)
        params['roe'] = st.slider(t('roe'), 0, 50, 10, 1)
    
    params['yoy_min'] = st.slider("📈 Revenue YoY Growth (%) (min)", -100, 100, -100, 5)

tab1, tab2, tab3 = st.tabs([t('screener'), t('backtest'), t('analytics')])

with tab1:
    st.header(t('multi_factor'))
    
    if 'stocks' not in st.session_state or st.session_state.get('current_market') != market_val:
        with st.spinner(t('loading_stock')):
            if market_val == "Taiwan":
                st.session_state.stocks = get_taiwan_stocks()
            else:
                st.session_state.stocks = get_us_stocks()
            st.session_state.current_market = market_val
            st.session_state.cached_data = None
    
    if 'cached_data' not in st.session_state or st.session_state.cached_data is None:
        with st.spinner(t('fetching')):
            stock_limit = 80 if market_val == "Taiwan" else 150
            st.session_state.cached_data = get_all_metrics(st.session_state.stocks[:stock_limit], market_val)
    
    df = pd.DataFrame(st.session_state.cached_data)
    if df.empty:
        st.warning("No data fetched. Trying alternative stock list...")
        fallback_stocks = get_taiwan_stocks() if market_val == "Taiwan" else get_us_stocks()
        st.session_state.cached_data = get_all_metrics(fallback_stocks[:50], market_val)
        df = pd.DataFrame(st.session_state.cached_data)
    
    df = df.drop_duplicates(subset=['symbol'], keep='first')
    
    if 'yoy' not in df.columns:
        df['yoy'] = 0
    if 'eps_growth' not in df.columns:
        df['eps_growth'] = 0
    
    if not df.empty:
        if strategy == t('value_investing'):
            mask = (df['pe'] > 0) & (df['pe'] <= params['pe']) & (df['pb'] <= params['pb']) & (df['div_yield'] >= params['div_yield']) & (df['yoy'] >= params['yoy_min'])
        elif strategy == t('quality_growth'):
            mask = (df['roe'] >= params['roe']) & (df['debt'] <= params['debt']) & (df['profit_margin'] >= params['profit_margin']) & (df['yoy'] >= params['yoy_min'])
        elif strategy == t('high_dividend'):
            mask = (df['div_yield'] >= params['div_yield']) & (df['yoy'] >= params['yoy_min'])
        else:
            mask = (df['pe'] > 0) & (df['pe'] <= params['pe']) & (df['pb'] <= params['pb']) & (df['div_yield'] >= params['div_yield']) & (df['roe'] >= params['roe']) & (df['yoy'] >= params['yoy_min'])
        
        filtered = df[mask]
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric(t('results'), f"{len(filtered)} / {len(df)}")
        with col2:
            search_term = st.text_input("🔍 Search stock", placeholder="e.g. MU, AAPL", label_visibility="collapsed")
            if st.button(t('refresh')):
                st.session_state.cached_data = None
                st.rerun()
        
        if search_term:
            filtered = filtered[filtered['symbol'].str.upper().str.contains(search_term.upper()) | 
                               filtered['name'].str.upper().str.contains(search_term.upper())]
        
        if len(filtered) > 0:
            display_df = filtered[['symbol', 'name', 'sector', 'pe', 'pb', 'div_yield', 'roe', 'price', 'yoy', 'eps_growth']].copy()
            
            display_df['score'] = display_df.apply(calc_score, axis=1)
            
            display_df['warning'] = display_df['eps_growth'].apply(lambda x: '⚠️' if x < -20 else '')
            display_df['name'] = display_df.apply(lambda r: f"{r['name']} {r['warning']}", axis=1)
            
            sort_col = st.selectbox("Sort by", ['score', 'pe', 'pb', 'div_yield', 'roe', 'price', 'yoy', 'eps_growth'], index=0, 
                                    format_func=lambda x: {'score': 'Score', 'pe': 'P/E', 'pb': 'P/B', 'div_yield': 'Dividend Yield', 'roe': 'ROE', 'price': 'Price', 'yoy': 'YoY', 'eps_growth': 'EPS Growth'}[x])
            ascending = st.checkbox("Ascending", value=True)
            
            display_df = display_df.sort_values(sort_col, ascending=ascending)
            
            display_df['pe'] = display_df['pe'].apply(lambda x: f"{x:.2f}" if x > 0 else t('na'))
            display_df['pb'] = display_df['pb'].apply(lambda x: f"{x:.2f}" if x > 0 else t('na'))
            display_df['div_yield'] = display_df['div_yield'].apply(lambda x: f"{x:.2f}%" if x > 0 else t('na'))
            display_df['roe'] = display_df['roe'].apply(lambda x: f"{x:.2f}%" if x > 0 else t('na'))
            display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if x > 0 else t('na'))
            display_df['yoy'] = display_df['yoy'].apply(lambda x: f"{x:.1f}%" if x != 0 else t('na'))
            display_df['eps_growth'] = display_df['eps_growth'].apply(lambda x: f"{x:.1f}%" if x != 0 else t('na'))
            
            st.dataframe(
                display_df.drop(columns=['warning']),
                use_container_width=True,
                hide_index=True,
                column_config={
                    'score': st.column_config.NumberColumn('Score', format='%.1f', width=70),
                    'symbol': st.column_config.TextColumn('Symbol', width=70),
                    'name': st.column_config.TextColumn('Name', width=180),
                    'sector': st.column_config.TextColumn('Sector', width=130),
                    'pe': st.column_config.TextColumn('P/E', width=70),
                    'pb': st.column_config.TextColumn('P/B', width=70),
                    'div_yield': st.column_config.TextColumn('Div Yield', width=80),
                    'roe': st.column_config.TextColumn('ROE', width=70),
                    'price': st.column_config.TextColumn('Price', width=80),
                    'yoy': st.column_config.TextColumn('YoY %', width=80),
                    'eps_growth': st.column_config.TextColumn('EPS Growth %', width=100),
                }
            )
            
            if (filtered['yoy'] < -20).any():
                st.warning("⚠️ Some stocks have earnings decline > 20%")
            
            st.session_state.selected = filtered['symbol'].tolist()
        else:
            st.warning(t('no_match'))
            st.session_state.selected = []
    else:
        st.error(t('unable_fetch'))

with tab2:
    st.header(t('backtest_engine'))
    
    if 'selected' not in st.session_state or not st.session_state.get('selected'):
        st.info(t('filter_first'))
    else:
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(t('start_date'), datetime.now() - timedelta(days=730))
        with col2:
            end_date = st.date_input(t('end_date'), datetime.now())
        
        if st.button(t('run_backtest')):
            with st.spinner(t('running')):
                port_ret, bench_ret = run_backtest(
                    st.session_state.selected,
                    market_val,
                    start_date,
                    end_date
                )
                
                if port_ret is not None and bench_ret is not None:
                    port_metrics = calc_metrics(port_ret)
                    bench_metrics = calc_metrics(bench_ret)
                    
                    st.subheader(t('performance'))
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric(t('strategy_return'), f"{port_metrics.get('total_return', 0):.2f}%")
                    c2.metric(t('annual_return'), f"{port_metrics.get('annual_return', 0):.2f}%")
                    c3.metric(t('benchmark_return'), f"{bench_metrics.get('total_return', 0):.2f}%")
                    c4.metric(t('alpha'), f"{port_metrics.get('total_return', 0) - bench_metrics.get('total_return', 0):.2f}%")
                    
                    c5, c6, c7 = st.columns(3)
                    c5.metric(t('volatility'), f"{port_metrics.get('volatility', 0):.2f}%")
                    c6.metric(t('sharpe'), f"{port_metrics.get('sharpe', 0):.2f}")
                    c7.metric(t('sortino'), f"{port_metrics.get('sortino', 0):.2f}")
                    
                    st.subheader(t('cumulative'))
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=port_ret.index, y=port_ret * 100, name=t('strategy'), line=dict(color=COLORS['success'], width=2)))
                    fig.add_trace(go.Scatter(x=bench_ret.index, y=bench_ret * 100, name=t('benchmark'), line=dict(color=COLORS['primary'], width=2)))
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor=COLORS['bg'],
                        plot_bgcolor=COLORS['bg'],
                        xaxis_title=t('date'),
                        yaxis_title=t('return_pct')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(t('backtest_fail'))

with tab3:
    st.header(t('strategy_analytics'))
    
    if 'selected' not in st.session_state or not st.session_state.get('selected'):
        st.info(t('filter_first'))
    elif 'cached_data' in st.session_state and st.session_state.cached_data:
        df = pd.DataFrame(st.session_state.cached_data)
        df = df.drop_duplicates(subset=['symbol'], keep='first')
        filtered = df[df['symbol'].isin(st.session_state.selected)]
        
        if not filtered.empty:
            st.subheader(t('sector_dist'))
            sector_counts = filtered['sector'].value_counts()
            fig_pie = px.pie(
                values=sector_counts.values,
                names=sector_counts.index,
                title=t('sector_title'),
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor=COLORS['bg']
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.subheader(t('key_metrics'))
            valid_pe = filtered[filtered['pe'] > 0]['pe']
            valid_pb = filtered[filtered['pb'] > 0]['pb']
            valid_div = filtered[filtered['div_yield'] > 0]['div_yield']
            valid_roe = filtered[filtered['roe'] > 0]['roe']
            
            cols = st.columns(4)
            cols[0].metric(t('avg_pe'), f"{valid_pe.mean():.2f}" if len(valid_pe) > 0 else t('na'))
            cols[1].metric(t('avg_pb'), f"{valid_pb.mean():.2f}" if len(valid_pb) > 0 else t('na'))
            cols[2].metric(t('avg_div'), f"{valid_div.mean():.2f}%" if len(valid_div) > 0 else t('na'))
            cols[3].metric(t('avg_roe'), f"{valid_roe.mean():.2f}%" if len(valid_roe) > 0 else t('na'))
            
            st.subheader(t('metrics_dist'))
            fig_hist = go.Figure()
            if len(valid_pe) > 0:
                fig_hist.add_trace(go.Histogram(x=valid_pe, name='P/E', marker_color=COLORS['primary'], opacity=0.75))
            if len(valid_div) > 0:
                fig_hist.add_trace(go.Histogram(x=valid_div, name='Dividend Yield', marker_color=COLORS['success'], opacity=0.75))
            fig_hist.update_layout(
                template="plotly_dark",
                paper_bgcolor=COLORS['bg'],
                plot_bgcolor=COLORS['bg'],
                barmode='overlay',
                title=t('pe_div')
            )
            st.plotly_chart(fig_hist, use_container_width=True)