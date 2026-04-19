import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Quant Stock Screener", page_icon="📈", layout="wide", menu_items={
        'About': 'Quant Stock Screener v1.0'
    })

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
    @media (max-width: 768px) {{
        section[data-testid="stSidebar"] {{
            width: 300px !important;
        }}
        section[data-testid="stSidebar"].collapsed {{
            width: 0px !important;
        }}
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
        'high_growth': 'High Growth',
        'conservative': 'Conservative Income',
        'tech_growth': 'Tech Growth',
        'value_trap': 'Value Trap',
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
        'fetched_count': 'Fetched {0} stocks',
        'fetch_error': 'Unable to fetch data. Try USA market.',
        'debug_mode': '🔧 Debug Mode',
        'show_all': 'Show All (no filter)',
        'ticker_list': '📋 Ticker List',
        'stock_count': 'Stocks',
        'export_report': '📥 Export Report',
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
        'high_growth': '高成長型',
        'conservative': '保守存股',
        'tech_growth': '科技成長',
        'value_trap': '危機入市',
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
        'fetched_count': '目前有 {0} 筆資料',
        'fetch_error': '無法讀取資料，請嘗試美國市場',
        'debug_mode': '🔧 除錯模式',
        'show_all': '顯示所有股票 (無篩選)',
        'ticker_list': '📋 本次回測股票清單',
        'stock_count': '股票數量',
        'export_report': '📥 匯出報告',
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
        print(f"FinMind API error: {e}")
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
        
        # Debug: print what we got
        if not info:
            return {'symbol': symbol, 'error': 'No info'}
        if not info.get('regularMarketPrice'):
            return {'symbol': symbol, 'error': 'No price'}
        
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        if not price:
            return {'symbol': symbol, 'error': 'Price is None'}
            
        dividend_yield = info.get('dividendYield')
        if isinstance(dividend_yield, (int, float)) and dividend_yield > 0:
            div_yield_pct = dividend_yield if dividend_yield >= 1 else dividend_yield * 100
        else:
            dividend_rate = info.get('dividendRate') or info.get('lastDividendValue') or 0
            if isinstance(dividend_rate, (int, float)) and dividend_rate > 0 and price:
                div_yield_pct = (dividend_rate / price) * 100
            else:
                div_yield_pct = 0
        
        if div_yield_pct > 20:
            div_yield_pct = 0
        
        return {
            'symbol': symbol,
            'name': info.get('shortName', symbol),
            'sector': info.get('sector') or 'Unknown',
            'pe': info.get('trailingPE') or 0,
            'pb': info.get('priceToBook') or 0,
            'div_yield': div_yield_pct,
            'roe': min((info.get('returnOnEquity') or 0) * 100, 100),
            'debt': info.get('debtToEquity') or 0,
            'profit_margin': (info.get('profitMargins') or 0) * 100,
            'price': price,
            'is_growth': info.get('trailingPE', 0) and info.get('trailingPE') < 0,
            'yoy': (info.get('revenueGrowth') or 0) * 100,
            'eps_growth': (info.get('earningsGrowth') or 0) * 100
        }
    except Exception as e:
        return {'symbol': symbol, 'error': str(e)}

def get_all_metrics(stock_list, market):
    if not stock_list:
        return []
    
    def fetch_one(symbol):
        result = fetch_stock_metrics(symbol, market)
        if result and 'error' not in result and result.get('price'):
            return result
        return None
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        results = [r for r in executor.map(fetch_one, stock_list) if r]
    
    # Remove duplicates by symbol
    seen = set()
    unique_results = []
    for r in results:
        if r['symbol'] not in seen:
            seen.add(r['symbol'])
            unique_results.append(r)
    return unique_results

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
    
    # Remove extreme outliers (> 50% daily move) to avoid skewing
    returns = returns[abs(returns) < 0.5]
    
    if len(returns) == 0:
        return {}
    
    total = returns.iloc[-1] if len(returns) > 0 else 0
    
    # Annualize based on actual trading days
    trading_days = len(returns)
    annual_factor = 252 / trading_days if trading_days > 0 else 1
    annual = (1 + total) ** annual_factor - 1
    
    # Volatility: annualize daily std
    daily_vol = returns.std()
    volatility = daily_vol * np.sqrt(252)
    
    # Sharpe: assume 0% risk-free rate for simplicity
    sharpe = annual / volatility if volatility > 0 else 0
    
    # Downside volatility for Sortino (only negative returns)
    negative_returns = returns[returns < 0]
    downside = negative_returns.std() * np.sqrt(252) if len(negative_returns) > 0 else volatility
    sortino = annual / downside if downside > 0 else 0
    
    # Max drawdown
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
        [t('value_investing'), t('quality_growth'), t('high_dividend'), t('high_growth'), 
         t('conservative'), t('tech_growth'), t('value_trap'), t('custom')]
    )
    
    params = {}
    if strategy == t('value_investing'):
        params['pe'] = st.slider(t('pe_ratio'), 0, 100, 25, 1)
        params['pb'] = st.slider(t('pb_ratio'), 0.0, 15.0, 5.0, 0.1)
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 20.0, 2.0, 0.1)
    elif strategy == t('quality_growth'):
        params['roe'] = st.slider(t('roe'), 0, 50, 15, 1)
        params['debt'] = st.slider(t('debt_ratio'), 0, 100, 80, 5)
        params['profit_margin'] = st.slider(t('profit_margin'), 0, 50, 10, 1)
    elif strategy == t('high_dividend'):
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 20.0, 4.0, 0.1)
    elif strategy == t('high_growth'):
        params['pe'] = st.slider(t('pe_ratio'), 0, 100, 50, 1)
        params['roe'] = st.slider(t('roe'), 0, 50, 20, 1)
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 20.0, 0.0, 0.1)
    elif strategy == t('conservative'):
        params['pe'] = st.slider(t('pe_ratio'), 0, 100, 15, 1)
        params['pb'] = st.slider(t('pb_ratio'), 0.0, 15.0, 2.0, 0.1)
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 20.0, 4.0, 0.1)
    elif strategy == t('tech_growth'):
        params['pe'] = st.slider(t('pe_ratio'), 0, 100, 45, 1)
        params['roe'] = st.slider(t('roe'), 0, 50, 20, 1)
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 20.0, 0.0, 0.1)
    elif strategy == t('value_trap'):
        params['pb'] = st.slider(t('pb_ratio'), 0.0, 15.0, 1.0, 0.1)
        params['pe'] = st.slider(t('pe_ratio'), 0, 100, 20, 1)
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 20.0, 2.0, 0.1)
    else:
        params['pe'] = st.slider(t('pe_ratio'), 0, 100, 30, 1)
        params['pb'] = st.slider(t('pb_ratio'), 0.0, 15.0, 5.0, 0.1)
        params['div_yield'] = st.slider(t('dividend_yield'), 0.0, 20.0, 2.0, 0.1)
        params['roe'] = st.slider(t('roe'), 0, 50, 10, 1)
    
    params['yoy_min'] = st.slider("📈 Revenue YoY Growth (%) (min)", -100, 100, -100, 5)

tab1, tab2, tab3 = st.tabs([t('screener'), t('backtest'), t('analytics')])

with tab1:
    st.header(t('multi_factor'))
    
    if 'stocks' not in st.session_state or st.session_state.get('current_market') != market_val:
        if market_val == "Taiwan":
            st.session_state.stocks = ['2330', '2317', '2454', '2412', '2882', '2891', '1301', '1326', '1215', '3008',
                               '2382', '2451', '2308', '2207', '2227', '2231', '8046', '2105', '2609', '2474',
                               '2449', '2377', '2353', '2344', '2327', '2315', '2303', '2297', '2288', '2408',
                               '2409', '2413', '2417', '2420', '2421', '2425', '2427', '2428', '2430', '2431',
                               '2433', '2434', '2436', '2437', '2438', '2441', '2443', '2444', '2445', '2448',
                               '2455', '2456', '2457', '2458', '2460', '2461', '2462', '2463', '2464', '2465',
                               '2474', '2475', '2476', '2478', '2480', '2481', '2482', '2491', '2492', '2493',
                               '2603', '2605', '2606', '2607', '2608', '2609', '2610', '2611', '2612', '2613',
                               '2614', '2615', '2616', '2617', '2618', '2624', '2630', '2633', '2634', '2635',
                               '2881', '2883', '2884', '2885', '2886', '2887', '2888', '2889', '2890', '2892',
                               '3044', '3045', '3050', '3060', '3071', '3083', '3085', '3089', '3094', '3105']
        else:
            # US stocks - major companies
            st.session_state.stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'JNJ', 'V',
                               'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'CRM', 'NFLX', 'CSCO',
                               'INTC', 'CSCO', 'VZ', 'T', 'PFE', 'MRK', 'ABBV', 'KO', 'PEP', 'WMT',
                               'COST', 'NKE', 'MCD', 'BA', 'IBM', 'ORCL', 'QCOM', 'TXN', 'AVGO', 'AMD',
                               'CRM', 'NOW', 'INTU', 'ADP', 'FIS', 'FI', 'GS', 'MS', 'C', 'BLK',
                               'AXP', 'SCHW', 'COF', 'USB', 'TFC', 'WFC', 'JPM', 'SPGI', 'MCO', 'CME',
                               'ICE', 'AON', 'MMC', 'CB', 'PGR', 'TRV', 'AFL', 'MET', 'PRU', 'LNC']
        st.session_state.current_market = market_val
        st.session_state.cached_data = None
    
    # 強制重新讀取
    force_refresh = st.button(t('refresh'))
    if force_refresh:
        st.session_state.cached_data = None
        st.rerun()
    
    if st.session_state.cached_data is None:
        # Try CSV first (real data snapshot)
        csv_path = os.path.join(os.path.dirname(__file__), 'stocks_data.csv')
        csv_loaded = False
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                if 'market' in df.columns:
                    df = df[df['market'] == market_val]
                st.session_state.cached_data = df.to_dict('records')
                csv_loaded = True
            except Exception as e:
                st.warning(f"CSV load failed: {e}")
        
        if not csv_loaded:
            if market_val == "Taiwan":
                st.session_state.cached_data = [
                    {'symbol': '2330', 'name': 'TSMC', 'sector': 'Technology', 'price': 2030.0, 'pe': 27.5, 'pb': 6.5, 'div_yield': 1.5, 'roe': 35.0, 'debt': 20, 'profit_margin': 35, 'yoy': 5.0, 'eps_growth': 10.0},
                    {'symbol': '2317', 'name': 'Foxconn', 'sector': 'Technology', 'price': 206.0, 'pe': 15.4, 'pb': 1.8, 'div_yield': 3.2, 'roe': 12.0, 'debt': 40, 'profit_margin': 5, 'yoy': 2.0, 'eps_growth': 5.0},
                    {'symbol': '2454', 'name': 'MediaTek', 'sector': 'Technology', 'price': 1925.0, 'pe': 29.1, 'pb': 4.2, 'div_yield': 1.8, 'roe': 18.0, 'debt': 30, 'profit_margin': 20, 'yoy': 8.0, 'eps_growth': 15.0},
                    {'symbol': '2412', 'name': 'CHT', 'sector': 'Telecom', 'price': 137.5, 'pe': 27.6, 'pb': 2.1, 'div_yield': 4.2, 'roe': 10.0, 'debt': 25, 'profit_margin': 15, 'yoy': 1.0, 'eps_growth': 2.0},
                    {'symbol': '2882', 'name': 'E.Sun Fin.', 'sector': 'Finance', 'price': 75.0, 'pe': 10.6, 'pb': 1.2, 'div_yield': 5.5, 'roe': 12.0, 'debt': 50, 'profit_margin': 30, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': '2891', 'name': 'CTBC Fin.', 'sector': 'Finance', 'price': 53.1, 'pe': 12.3, 'pb': 1.5, 'div_yield': 4.8, 'roe': 14.0, 'debt': 45, 'profit_margin': 25, 'yoy': 4.0, 'eps_growth': 6.0},
                    {'symbol': '1301', 'name': 'Formosa Plastics', 'sector': 'Chemical', 'price': 53.4, 'pe': 18.5, 'pb': 2.2, 'div_yield': 3.5, 'roe': 11.0, 'debt': 35, 'profit_margin': 10, 'yoy': -2.0, 'eps_growth': -5.0},
                    {'symbol': '1326', 'name': 'FCF', 'sector': 'Chemical', 'price': 51.0, 'pe': 16.2, 'pb': 1.9, 'div_yield': 4.0, 'roe': 10.0, 'debt': 38, 'profit_margin': 8, 'yoy': -1.0, 'eps_growth': -3.0},
                    {'symbol': '1215', 'name': 'FamilyMart', 'sector': 'Retail', 'price': 142.5, 'pe': 22.0, 'pb': 3.5, 'div_yield': 2.5, 'roe': 18.0, 'debt': 30, 'profit_margin': 6, 'yoy': 3.0, 'eps_growth': 4.0},
                    {'symbol': '3008', 'name': 'Giant', 'sector': 'Consumer', 'price': 2605.0, 'pe': 25.0, 'pb': 4.8, 'div_yield': 1.2, 'roe': 20.0, 'debt': 25, 'profit_margin': 10, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': '2382', 'name': 'Quanta', 'sector': 'Technology', 'price': 285.0, 'pe': 18.0, 'pb': 3.2, 'div_yield': 2.8, 'roe': 22.0, 'debt': 35, 'profit_margin': 5, 'yoy': 6.0, 'eps_growth': 12.0},
                    {'symbol': '2451', 'name': 'Unimicron', 'sector': 'Technology', 'price': 128.0, 'pe': 20.5, 'pb': 2.8, 'div_yield': 2.0, 'roe': 15.0, 'debt': 28, 'profit_margin': 12, 'yoy': 4.0, 'eps_growth': 7.0},
                    {'symbol': '2207', 'name': 'Hotai Motor', 'sector': 'Auto', 'price': 1850.0, 'pe': 15.0, 'pb': 3.5, 'div_yield': 3.0, 'roe': 25.0, 'debt': 50, 'profit_margin': 8, 'yoy': 10.0, 'eps_growth': 15.0},
                    {'symbol': '2308', 'name': 'Delta', 'sector': 'Technology', 'price': 580.0, 'pe': 24.0, 'pb': 5.0, 'div_yield': 1.8, 'roe': 22.0, 'debt': 30, 'profit_margin': 12, 'yoy': 6.0, 'eps_growth': 10.0},
                    {'symbol': '2609', 'name': 'Yang Ming', 'sector': 'Shipping', 'price': 95.0, 'pe': 8.0, 'pb': 1.5, 'div_yield': 3.0, 'roe': 20.0, 'debt': 60, 'profit_margin': 15, 'yoy': -10.0, 'eps_growth': -20.0},
                    {'symbol': '2615', 'name': 'Evergreen', 'sector': 'Shipping', 'price': 180.0, 'pe': 10.0, 'pb': 2.0, 'div_yield': 2.5, 'roe': 25.0, 'debt': 55, 'profit_margin': 20, 'yoy': -5.0, 'eps_growth': -15.0},
                    {'symbol': '2105', 'name': 'Cheng Shin', 'sector': 'Auto', 'price': 48.0, 'pe': 20.0, 'pb': 1.8, 'div_yield': 4.0, 'roe': 10.0, 'debt': 40, 'profit_margin': 8, 'yoy': 1.0, 'eps_growth': 2.0},
                    {'symbol': '8046', 'name': 'Nanya PCB', 'sector': 'Technology', 'price': 120.0, 'pe': 15.0, 'pb': 2.5, 'div_yield': 2.0, 'roe': 18.0, 'debt': 35, 'profit_margin': 10, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': '2474', 'name': 'OBI Pharma', 'sector': 'Pharma', 'price': 85.0, 'pe': 35.0, 'pb': 4.0, 'div_yield': 0.0, 'roe': 12.0, 'debt': 20, 'profit_margin': -10, 'yoy': 10.0, 'eps_growth': 5.0},
                    {'symbol': '2881', 'name': 'Fubon Fin.', 'sector': 'Finance', 'price': 85.0, 'pe': 12.0, 'pb': 1.4, 'div_yield': 3.0, 'roe': 12.0, 'debt': 45, 'profit_margin': 25, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': '2883', 'name': 'Cathay Fin.', 'sector': 'Finance', 'price': 28.0, 'pe': 15.0, 'pb': 1.0, 'div_yield': 2.5, 'roe': 8.0, 'debt': 50, 'profit_margin': 15, 'yoy': 3.0, 'eps_growth': 4.0},
                    {'symbol': '2884', 'name': 'Yuanta Fin.', 'sector': 'Finance', 'price': 45.0, 'pe': 14.0, 'pb': 1.2, 'div_yield': 3.0, 'roe': 10.0, 'debt': 48, 'profit_margin': 20, 'yoy': 4.0, 'eps_growth': 6.0},
                    {'symbol': '2885', 'name': 'Yuanta Fut.', 'sector': 'Finance', 'price': 120.0, 'pe': 18.0, 'pb': 3.0, 'div_yield': 2.0, 'roe': 18.0, 'debt': 30, 'profit_margin': 30, 'yoy': 8.0, 'eps_growth': 10.0},
                    {'symbol': '2886', 'name': 'Mega Fin.', 'sector': 'Finance', 'price': 42.0, 'pe': 16.0, 'pb': 1.3, 'div_yield': 3.5, 'roe': 12.0, 'debt': 45, 'profit_margin': 28, 'yoy': 2.0, 'eps_growth': 3.0},
                    {'symbol': '2887', 'name': 'Taishin Fin.', 'sector': 'Finance', 'price': 25.0, 'pe': 12.0, 'pb': 1.1, 'div_yield': 2.8, 'roe': 10.0, 'debt': 50, 'profit_margin': 18, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': '2888', 'name': 'Shin Kong Fin.', 'sector': 'Finance', 'price': 15.0, 'pe': 20.0, 'pb': 1.0, 'div_yield': 2.0, 'roe': 5.0, 'debt': 60, 'profit_margin': 10, 'yoy': 1.0, 'eps_growth': 2.0},
                    {'symbol': '2889', 'name': 'CTCB Bank', 'sector': 'Finance', 'price': 38.0, 'pe': 14.0, 'pb': 1.2, 'div_yield': 3.2, 'roe': 10.0, 'debt': 42, 'profit_margin': 22, 'yoy': 4.0, 'eps_growth': 6.0},
                    {'symbol': '2890', 'name': 'SinoPac Fin.', 'sector': 'Finance', 'price': 22.0, 'pe': 13.0, 'pb': 1.0, 'div_yield': 3.0, 'roe': 9.0, 'debt': 48, 'profit_margin': 15, 'yoy': 2.0, 'eps_growth': 4.0},
                    {'symbol': '2892', 'name': 'First Fin.', 'sector': 'Finance', 'price': 35.0, 'pe': 15.0, 'pb': 1.3, 'div_yield': 3.0, 'roe': 10.0, 'debt': 44, 'profit_margin': 20, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': '3034', 'name': 'Novatek', 'sector': 'Technology', 'price': 680.0, 'pe': 22.0, 'pb': 5.0, 'div_yield': 1.5, 'roe': 25.0, 'debt': 25, 'profit_margin': 30, 'yoy': 10.0, 'eps_growth': 15.0},
                    {'symbol': '2301', 'name': 'Lite-On', 'sector': 'Technology', 'price': 115.0, 'pe': 18.0, 'pb': 2.5, 'div_yield': 2.5, 'roe': 15.0, 'debt': 35, 'profit_margin': 10, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': '2303', 'name': 'UMC', 'sector': 'Technology', 'price': 52.0, 'pe': 14.0, 'pb': 1.8, 'div_yield': 3.5, 'roe': 15.0, 'debt': 38, 'profit_margin': 25, 'yoy': -5.0, 'eps_growth': -10.0},
                    {'symbol': '2377', 'name': 'MSI', 'sector': 'Technology', 'price': 185.0, 'pe': 16.0, 'pb': 3.0, 'div_yield': 2.0, 'roe': 20.0, 'debt': 30, 'profit_margin': 8, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': '2353', 'name': 'Acer', 'sector': 'Technology', 'price': 42.0, 'pe': 12.0, 'pb': 1.5, 'div_yield': 4.0, 'roe': 12.0, 'debt': 45, 'profit_margin': 5, 'yoy': 2.0, 'eps_growth': 3.0},
                    {'symbol': '2344', 'name': 'Winbond', 'sector': 'Technology', 'price': 35.0, 'pe': 25.0, 'pb': 2.0, 'div_yield': 1.5, 'roe': 8.0, 'debt': 40, 'profit_margin': 10, 'yoy': -3.0, 'eps_growth': -5.0},
                    {'symbol': '2327', 'name': 'Yageo', 'sector': 'Technology', 'price': 520.0, 'pe': 18.0, 'pb': 4.0, 'div_yield': 1.2, 'roe': 22.0, 'debt': 28, 'profit_margin': 25, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': '2315', 'name': 'Foxlink', 'sector': 'Technology', 'price': 180.0, 'pe': 20.0, 'pb': 3.5, 'div_yield': 1.5, 'roe': 18.0, 'debt': 32, 'profit_margin': 12, 'yoy': 6.0, 'eps_growth': 10.0},
                    {'symbol': '2408', 'name': 'Nanya Tech', 'sector': 'Technology', 'price': 85.0, 'pe': 30.0, 'pb': 2.5, 'div_yield': 1.0, 'roe': 8.0, 'debt': 35, 'profit_margin': 15, 'yoy': -8.0, 'eps_growth': -15.0},
                    {'symbol': '2409', 'name': 'AUO', 'sector': 'Technology', 'price': 18.0, 'pe': 40.0, 'pb': 1.0, 'div_yield': 2.0, 'roe': 3.0, 'debt': 50, 'profit_margin': 2, 'yoy': -15.0, 'eps_growth': -25.0},
                    {'symbol': '2413', 'name': 'GlobalWafers', 'sector': 'Technology', 'price': 580.0, 'pe': 15.0, 'pb': 3.5, 'div_yield': 2.0, 'roe': 25.0, 'debt': 30, 'profit_margin': 30, 'yoy': -5.0, 'eps_growth': -10.0},
                    {'symbol': '2420', 'name': 'Zippy', 'sector': 'Technology', 'price': 42.0, 'pe': 16.0, 'pb': 2.0, 'div_yield': 3.0, 'roe': 12.0, 'debt': 35, 'profit_margin': 10, 'yoy': 2.0, 'eps_growth': 4.0},
                    {'symbol': '2421', 'name': 'Sunon', 'sector': 'Technology', 'price': 85.0, 'pe': 18.0, 'pb': 2.5, 'div_yield': 2.5, 'roe': 14.0, 'debt': 32, 'profit_margin': 12, 'yoy': 4.0, 'eps_growth': 6.0},
                    {'symbol': '2439', 'name': 'Merry', 'sector': 'Technology', 'price': 165.0, 'pe': 20.0, 'pb': 4.0, 'div_yield': 1.5, 'roe': 20.0, 'debt': 25, 'profit_margin': 15, 'yoy': 8.0, 'eps_growth': 12.0},
                    {'symbol': '2441', 'name': 'Chol tech', 'sector': 'Technology', 'price': 92.0, 'pe': 22.0, 'pb': 3.0, 'div_yield': 2.0, 'roe': 15.0, 'debt': 28, 'profit_margin': 12, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': '2443', 'name': 'Everlight', 'sector': 'Technology', 'price': 45.0, 'pe': 18.0, 'pb': 1.8, 'div_yield': 3.0, 'roe': 10.0, 'debt': 35, 'profit_margin': 8, 'yoy': 1.0, 'eps_growth': 2.0},
                    {'symbol': '2444', 'name': 'Synnex', 'sector': 'Technology', 'price': 48.0, 'pe': 14.0, 'pb': 2.0, 'div_yield': 4.5, 'roe': 15.0, 'debt': 40, 'profit_margin': 5, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': '2445', 'name': 'AAC', 'sector': 'Technology', 'price': 125.0, 'pe': 20.0, 'pb': 3.2, 'div_yield': 1.8, 'roe': 16.0, 'debt': 30, 'profit_margin': 14, 'yoy': 6.0, 'eps_growth': 9.0},
                    {'symbol': '2002', 'name': 'CSC', 'sector': 'Steel', 'price': 28.0, 'pe': 15.0, 'pb': 1.2, 'div_yield': 4.0, 'roe': 8.0, 'debt': 45, 'profit_margin': 5, 'yoy': -8.0, 'eps_growth': -12.0},
                    {'symbol': '2103', 'name': 'TSRC', 'sector': 'Chemical', 'price': 35.0, 'pe': 20.0, 'pb': 1.5, 'div_yield': 3.0, 'roe': 8.0, 'debt': 38, 'profit_margin': 6, 'yoy': -2.0, 'eps_growth': -5.0},
                ]
            else:
                st.session_state.cached_data = [
                    {'symbol': 'AAPL', 'name': 'Apple', 'sector': 'Technology', 'price': 175.0, 'pe': 28.0, 'pb': 45.0, 'div_yield': 0.5, 'roe': 150.0, 'debt': 50, 'profit_margin': 25, 'yoy': 2.0, 'eps_growth': 5.0},
                    {'symbol': 'MSFT', 'name': 'Microsoft', 'sector': 'Technology', 'price': 380.0, 'pe': 35.0, 'pb': 12.0, 'div_yield': 0.8, 'roe': 40.0, 'debt': 40, 'profit_margin': 35, 'yoy': 10.0, 'eps_growth': 15.0},
                    {'symbol': 'GOOGL', 'name': 'Alphabet', 'sector': 'Technology', 'price': 140.0, 'pe': 25.0, 'pb': 6.0, 'div_yield': 0.0, 'roe': 25.0, 'debt': 30, 'profit_margin': 25, 'yoy': 8.0, 'eps_growth': 12.0},
                    {'symbol': 'NVDA', 'name': 'NVIDIA', 'sector': 'Technology', 'price': 450.0, 'pe': 60.0, 'pb': 40.0, 'div_yield': 0.0, 'roe': 80.0, 'debt': 35, 'profit_margin': 40, 'yoy': 30.0, 'eps_growth': 50.0},
                    {'symbol': 'META', 'name': 'Meta', 'sector': 'Technology', 'price': 320.0, 'pe': 22.0, 'pb': 5.5, 'div_yield': 0.0, 'roe': 30.0, 'debt': 25, 'profit_margin': 30, 'yoy': 12.0, 'eps_growth': 20.0},
                    {'symbol': 'TSLA', 'name': 'Tesla', 'sector': 'Auto', 'price': 250.0, 'pe': 50.0, 'pb': 15.0, 'div_yield': 0.0, 'roe': 25.0, 'debt': 40, 'profit_margin': 15, 'yoy': 15.0, 'eps_growth': -10.0},
                    {'symbol': 'AMZN', 'name': 'Amazon', 'sector': 'Consumer', 'price': 155.0, 'pe': 45.0, 'pb': 8.0, 'div_yield': 0.0, 'roe': 20.0, 'debt': 35, 'profit_margin': 5, 'yoy': 8.0, 'eps_growth': 5.0},
                    {'symbol': 'BRK.B', 'name': 'Berkshire', 'sector': 'Finance', 'price': 360.0, 'pe': 10.0, 'pb': 1.5, 'div_yield': 2.5, 'roe': 10.0, 'debt': 20, 'profit_margin': 25, 'yoy': 3.0, 'eps_growth': 2.0},
                    {'symbol': 'JNJ', 'name': 'J&J', 'sector': 'Healthcare', 'price': 155.0, 'pe': 18.0, 'pb': 5.0, 'div_yield': 3.0, 'roe': 25.0, 'debt': 45, 'profit_margin': 20, 'yoy': 2.0, 'eps_growth': 3.0},
                    {'symbol': 'V', 'name': 'Visa', 'sector': 'Finance', 'price': 280.0, 'pe': 30.0, 'pb': 12.0, 'div_yield': 0.8, 'roe': 50.0, 'debt': 35, 'profit_margin': 50, 'yoy': 8.0, 'eps_growth': 12.0},
                    {'symbol': 'PG', 'name': 'P&G', 'sector': 'Consumer', 'price': 160.0, 'pe': 25.0, 'pb': 7.0, 'div_yield': 2.5, 'roe': 30.0, 'debt': 40, 'profit_margin': 20, 'yoy': 1.0, 'eps_growth': 2.0},
                    {'symbol': 'UNH', 'name': 'UnitedHealth', 'sector': 'Healthcare', 'price': 520.0, 'pe': 22.0, 'pb': 6.0, 'div_yield': 1.5, 'roe': 25.0, 'debt': 50, 'profit_margin': 8, 'yoy': 6.0, 'eps_growth': 8.0},
                    {'symbol': 'HD', 'name': 'Home Depot', 'sector': 'Retail', 'price': 350.0, 'pe': 22.0, 'pb': 50.0, 'div_yield': 2.5, 'roe': 400.0, 'debt': 60, 'profit_margin': 14, 'yoy': 2.0, 'eps_growth': 3.0},
                    {'symbol': 'DIS', 'name': 'Disney', 'sector': 'Entertainment', 'price': 95.0, 'pe': 50.0, 'pb': 2.0, 'div_yield': 0.0, 'roe': 10.0, 'debt': 45, 'profit_margin': 8, 'yoy': 5.0, 'eps_growth': 20.0},
                    {'symbol': 'BAC', 'name': 'Bank of America', 'sector': 'Finance', 'price': 35.0, 'pe': 12.0, 'pb': 1.2, 'div_yield': 2.8, 'roe': 12.0, 'debt': 80, 'profit_margin': 30, 'yoy': 2.0, 'eps_growth': 4.0},
                    {'symbol': 'ADBE', 'name': 'Adobe', 'sector': 'Technology', 'price': 520.0, 'pe': 40.0, 'pb': 10.0, 'div_yield': 0.0, 'roe': 30.0, 'debt': 20, 'profit_margin': 35, 'yoy': 12.0, 'eps_growth': 15.0},
                    {'symbol': 'CRM', 'name': 'Salesforce', 'sector': 'Technology', 'price': 240.0, 'pe': 45.0, 'pb': 8.0, 'div_yield': 0.0, 'roe': 15.0, 'debt': 30, 'profit_margin': 10, 'yoy': 8.0, 'eps_growth': 12.0},
                    {'symbol': 'NFLX', 'name': 'Netflix', 'sector': 'Entertainment', 'price': 450.0, 'pe': 35.0, 'pb': 8.0, 'div_yield': 0.0, 'roe': 25.0, 'debt': 40, 'profit_margin': 20, 'yoy': 5.0, 'eps_growth': 10.0},
                    {'symbol': 'CSCO', 'name': 'Cisco', 'sector': 'Technology', 'price': 50.0, 'pe': 15.0, 'pb': 4.0, 'div_yield': 3.0, 'roe': 30.0, 'debt': 25, 'profit_margin': 25, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': 'INTC', 'name': 'Intel', 'sector': 'Technology', 'price': 45.0, 'pe': 100.0, 'pb': 1.5, 'div_yield': 1.5, 'roe': 8.0, 'debt': 40, 'profit_margin': 5, 'yoy': -5.0, 'eps_growth': -20.0},
                    {'symbol': 'AMD', 'name': 'AMD', 'sector': 'Technology', 'price': 120.0, 'pe': 30.0, 'pb': 5.0, 'div_yield': 0.0, 'roe': 20.0, 'debt': 25, 'profit_margin': 12, 'yoy': 15.0, 'eps_growth': 25.0},
                    {'symbol': 'ORCL', 'name': 'Oracle', 'sector': 'Technology', 'price': 120.0, 'pe': 28.0, 'pb': 15.0, 'div_yield': 1.5, 'roe': 80.0, 'debt': 60, 'profit_margin': 40, 'yoy': 6.0, 'eps_growth': 10.0},
                    {'symbol': 'IBM', 'name': 'IBM', 'sector': 'Technology', 'price': 165.0, 'pe': 22.0, 'pb': 6.0, 'div_yield': 3.5, 'roe': 35.0, 'debt': 50, 'profit_margin': 20, 'yoy': 2.0, 'eps_growth': 4.0},
                    {'symbol': 'QCOM', 'name': 'Qualcomm', 'sector': 'Technology', 'price': 145.0, 'pe': 18.0, 'pb': 8.0, 'div_yield': 2.0, 'roe': 45.0, 'debt': 30, 'profit_margin': 30, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': 'TXN', 'name': 'Texas Instruments', 'sector': 'Technology', 'price': 170.0, 'pe': 25.0, 'pb': 12.0, 'div_yield': 2.8, 'roe': 60.0, 'debt': 35, 'profit_margin': 40, 'yoy': -3.0, 'eps_growth': -5.0},
                    {'symbol': 'AVGO', 'name': 'Broadcom', 'sector': 'Technology', 'price': 880.0, 'pe': 25.0, 'pb': 10.0, 'div_yield': 1.2, 'roe': 45.0, 'debt': 40, 'profit_margin': 35, 'yoy': 10.0, 'eps_growth': 12.0},
                    {'symbol': 'COST', 'name': 'Costco', 'sector': 'Retail', 'price': 580.0, 'pe': 40.0, 'pb': 12.0, 'div_yield': 0.6, 'roe': 30.0, 'debt': 45, 'profit_margin': 3, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': 'NKE', 'name': 'Nike', 'sector': 'Consumer', 'price': 105.0, 'pe': 30.0, 'pb': 10.0, 'div_yield': 1.2, 'roe': 45.0, 'debt': 40, 'profit_margin': 12, 'yoy': 1.0, 'eps_growth': -5.0},
                    {'symbol': 'MCD', 'name': "McDonald's", 'sector': 'Consumer', 'price': 280.0, 'pe': 25.0, 'pb': -1.0, 'div_yield': 2.0, 'roe': -1.0, 'debt': 80, 'profit_margin': 30, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': 'BA', 'name': 'Boeing', 'sector': 'Industrial', 'price': 210.0, 'pe': -1.0, 'pb': -1.0, 'div_yield': 0.0, 'roe': -10.0, 'debt': 90, 'profit_margin': -2, 'yoy': 10.0, 'eps_growth': 15.0},
                    {'symbol': 'CAT', 'name': 'Caterpillar', 'sector': 'Industrial', 'price': 290.0, 'pe': 18.0, 'pb': 8.0, 'div_yield': 1.8, 'roe': 55.0, 'debt': 60, 'profit_margin': 20, 'yoy': 8.0, 'eps_growth': 12.0},
                    {'symbol': 'GE', 'name': 'General Electric', 'sector': 'Industrial', 'price': 125.0, 'pe': 20.0, 'pb': 4.0, 'div_yield': 1.0, 'roe': 20.0, 'debt': 50, 'profit_margin': 10, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': 'JPM', 'name': 'JPMorgan', 'sector': 'Finance', 'price': 180.0, 'pe': 11.0, 'pb': 1.5, 'div_yield': 2.5, 'roe': 15.0, 'debt': 70, 'profit_margin': 40, 'yoy': 4.0, 'eps_growth': 6.0},
                    {'symbol': 'GS', 'name': 'Goldman Sachs', 'sector': 'Finance', 'price': 380.0, 'pe': 14.0, 'pb': 1.2, 'div_yield': 2.5, 'roe': 10.0, 'debt': 75, 'profit_margin': 25, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': 'MS', 'name': 'Morgan Stanley', 'sector': 'Finance', 'price': 95.0, 'pe': 15.0, 'pb': 1.3, 'div_yield': 3.0, 'roe': 12.0, 'debt': 70, 'profit_margin': 25, 'yoy': 2.0, 'eps_growth': 4.0},
                    {'symbol': 'WMT', 'name': 'Walmart', 'sector': 'Retail', 'price': 165.0, 'pe': 28.0, 'pb': 8.0, 'div_yield': 1.4, 'roe': 35.0, 'debt': 50, 'profit_margin': 4, 'yoy': 3.0, 'eps_growth': 6.0},
                    {'symbol': 'CVX', 'name': 'Chevron', 'sector': 'Energy', 'price': 155.0, 'pe': 12.0, 'pb': 1.8, 'div_yield': 4.0, 'roe': 15.0, 'debt': 35, 'profit_margin': 20, 'yoy': -10.0, 'eps_growth': -15.0},
                    {'symbol': 'XOM', 'name': 'Exxon', 'sector': 'Energy', 'price': 105.0, 'pe': 10.0, 'pb': 2.0, 'div_yield': 3.5, 'roe': 20.0, 'debt': 30, 'profit_margin': 25, 'yoy': -5.0, 'eps_growth': -8.0},
                    {'symbol': 'KO', 'name': 'Coca-Cola', 'sector': 'Consumer', 'price': 60.0, 'pe': 25.0, 'pb': 10.0, 'div_yield': 3.0, 'roe': 45.0, 'debt': 55, 'profit_margin': 25, 'yoy': 2.0, 'eps_growth': 4.0},
                    {'symbol': 'PEP', 'name': 'Pepsi', 'sector': 'Consumer', 'price': 170.0, 'pe': 28.0, 'pb': 14.0, 'div_yield': 2.8, 'roe': 55.0, 'debt': 50, 'profit_margin': 15, 'yoy': 3.0, 'eps_growth': 5.0},
                    {'symbol': 'T', 'name': 'AT&T', 'sector': 'Telecom', 'price': 17.0, 'pe': 8.0, 'pb': 1.0, 'div_yield': 6.0, 'roe': 12.0, 'debt': 70, 'profit_margin': 15, 'yoy': -2.0, 'eps_growth': -5.0},
                    {'symbol': 'VZ', 'name': 'Verizon', 'sector': 'Telecom', 'price': 40.0, 'pe': 10.0, 'pb': 1.5, 'div_yield': 6.5, 'roe': 15.0, 'debt': 65, 'profit_margin': 20, 'yoy': 1.0, 'eps_growth': 2.0},
                    {'symbol': 'PFE', 'name': 'Pfizer', 'sector': 'Healthcare', 'price': 28.0, 'pe': 15.0, 'pb': 1.5, 'div_yield': 5.5, 'roe': 12.0, 'debt': 45, 'profit_margin': 25, 'yoy': -5.0, 'eps_growth': -10.0},
                    {'symbol': 'MRK', 'name': 'Merck', 'sector': 'Healthcare', 'price': 110.0, 'pe': 16.0, 'pb': 5.0, 'div_yield': 2.5, 'roe': 35.0, 'debt': 40, 'profit_margin': 30, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': 'ABBV', 'name': 'AbbVie', 'sector': 'Healthcare', 'price': 155.0, 'pe': 35.0, 'pb': 20.0, 'div_yield': 3.5, 'roe': 70.0, 'debt': 60, 'profit_margin': 25, 'yoy': 4.0, 'eps_growth': 6.0},
                    {'symbol': 'TMO', 'name': 'Thermo Fisher', 'sector': 'Healthcare', 'price': 520.0, 'pe': 30.0, 'pb': 5.0, 'div_yield': 0.3, 'roe': 18.0, 'debt': 40, 'profit_margin': 20, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': 'LLY', 'name': 'Eli Lilly', 'sector': 'Healthcare', 'price': 720.0, 'pe': 80.0, 'pb': 40.0, 'div_yield': 0.8, 'roe': 60.0, 'debt': 35, 'profit_margin': 25, 'yoy': 15.0, 'eps_growth': 20.0},
                    {'symbol': 'ABT', 'name': 'Abbott', 'sector': 'Healthcare', 'price': 105.0, 'pe': 25.0, 'pb': 6.0, 'div_yield': 1.8, 'roe': 25.0, 'debt': 40, 'profit_margin': 18, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': 'ACN', 'name': 'Accenture', 'sector': 'Technology', 'price': 320.0, 'pe': 28.0, 'pb': 10.0, 'div_yield': 1.5, 'roe': 35.0, 'debt': 30, 'profit_margin': 15, 'yoy': 5.0, 'eps_growth': 8.0},
                    {'symbol': 'NOW', 'name': 'ServiceNow', 'sector': 'Technology', 'price': 620.0, 'pe': 100.0, 'pb': 20.0, 'div_yield': 0.0, 'roe': 25.0, 'debt': 25, 'profit_margin': 20, 'yoy': 20.0, 'eps_growth': 25.0},
                    {'symbol': 'INTU', 'name': 'Intuit', 'sector': 'Technology', 'price': 580.0, 'pe': 50.0, 'pb': 12.0, 'div_yield': 0.6, 'roe': 25.0, 'debt': 35, 'profit_margin': 30, 'yoy': 10.0, 'eps_growth': 15.0},
                ]
            if not csv_loaded:
                st.caption("使用 Mock Data（請先執行 fetch_data.py 建立真實數據快照）")
    
    df = pd.DataFrame(st.session_state.cached_data)
    st.caption(f"Loaded {len(df)} stocks from {market_val}")
    
    if len(df) == 0:
        st.error(t('fetch_error'))
        if st.button("🔧 Debug"):
            st.write(f"market_val: '{market_val}'")
            st.write(f"current_market: '{st.session_state.get('current_market')}'")
            st.write(f"stocks count: {len(st.session_state.stocks)}")
            st.write(f"first 5 stocks: {st.session_state.stocks[:5]}")
            st.write(f"cached_data: {st.session_state.cached_data}")
        st.stop()
    
    df = df.drop_duplicates(subset=['symbol'], keep='first')
    
    if 'yoy' not in df.columns:
        df['yoy'] = 0
    if 'eps_growth' not in df.columns:
        df['eps_growth'] = 0
    
    if not df.empty:
        st.caption(f"Loaded {len(df)} stocks")
        
        # Toggle between all stocks and filtered
        if 'show_all' not in st.session_state:
            st.session_state.show_all = True  # Default to show all
        
        show_all_toggle = st.checkbox("Show All Stocks", value=st.session_state.show_all, key="show_all_chk")
        st.session_state.show_all = show_all_toggle
        
        if show_all_toggle:
            filtered = df.copy()
            st.caption(f"Showing ALL {len(filtered)} stocks")
        else:
            if strategy == t('value_investing'):
                mask = (df['pe'] > 0) & (df['pe'] <= params['pe']) & (df['pb'] <= params['pb']) & (df['div_yield'] >= params['div_yield']) & (df['yoy'] >= params['yoy_min'])
            elif strategy == t('quality_growth'):
                mask = (df['roe'] >= params['roe']) & (df['debt'] <= params['debt']) & (df['profit_margin'] >= params['profit_margin']) & (df['yoy'] >= params['yoy_min'])
            elif strategy == t('high_dividend'):
                mask = (df['div_yield'] >= params['div_yield']) & (df['yoy'] >= params['yoy_min'])
            elif strategy == t('high_growth'):
                mask = (df['pe'] > 0) & (df['pe'] <= params['pe']) & (df['roe'] >= params['roe']) & (df['yoy'] >= params['yoy_min'])
            elif strategy == t('conservative'):
                mask = (df['pe'] > 0) & (df['pe'] <= params['pe']) & (df['pb'] <= params['pb']) & (df['div_yield'] >= params['div_yield']) & (df['yoy'] >= params['yoy_min'])
            elif strategy == t('tech_growth'):
                mask = (df['pe'] > 0) & (df['pe'] <= params['pe']) & (df['roe'] >= params['roe']) & (df['div_yield'] >= params['div_yield']) & (df['yoy'] >= params['yoy_min'])
            elif strategy == t('value_trap'):
                mask = (df['pb'] > 0) & (df['pb'] <= params['pb']) & (df['pe'] > 0) & (df['pe'] <= params['pe']) & (df['div_yield'] >= params['div_yield']) & (df['yoy'] >= params['yoy_min'])
            else:
                mask = (df['pe'] > 0) & (df['pe'] <= params['pe']) & (df['pb'] <= params['pb']) & (df['div_yield'] >= params['div_yield']) & (df['roe'] >= params['roe']) & (df['yoy'] >= params['yoy_min'])
            filtered = df[mask]
        
        # Debug: show raw data count
        col0, col1 = st.columns([1, 3])
        with col0:
            st.caption(f"Total: {len(df)} | Showing: {len(filtered)}")
        with col1:
            search_term = st.text_input("🔍 Search", placeholder="2330...", label_visibility="collapsed")
            if st.button(t('refresh'), use_container_width=True):
                st.session_state.cached_data = None
                st.rerun()
        
        if search_term:
            search_upper = search_term.upper()
            filtered = df[(df['symbol'].str.upper().str.contains(search_upper)) | 
                         (df['name'].str.upper().str.contains(search_upper))]
            if len(filtered) > 0:
                st.info(f"Showing search results for '{search_term}' (bypassing filters)")
        
        if len(filtered) > 0:
            display_df = filtered[['symbol', 'name', 'sector', 'pe', 'pb', 'div_yield', 'roe', 'price', 'yoy', 'eps_growth']].copy()
            
            display_df = display_df.fillna(0)
            
            display_df['score'] = display_df.apply(calc_score, axis=1)
            
            display_df['warning'] = display_df['eps_growth'].apply(lambda x: '⚠️' if x < -20 else '')
            display_df['name'] = display_df.apply(lambda r: f"{r['name']} {r['warning']}", axis=1)
            
            sort_col = st.selectbox("Sort by", ['score', 'pe', 'pb', 'div_yield', 'roe', 'price', 'yoy', 'eps_growth'], index=0, 
                                    format_func=lambda x: {'score': 'Score', 'pe': 'P/E', 'pb': 'P/B', 'div_yield': 'Dividend Yield', 'roe': 'ROE', 'price': 'Price', 'yoy': 'YoY', 'eps_growth': 'EPS Growth'}[x])
            ascending = st.checkbox("Ascending", value=True)
            
            display_df = display_df.sort_values(sort_col, ascending=ascending)
            
            na_text = "Data Pending" if st.session_state.get('lang') == 'en' else "資料待補"
            display_df['pe'] = display_df['pe'].apply(lambda x: f"{x:.2f}" if x > 0 else na_text)
            display_df['pb'] = display_df['pb'].apply(lambda x: f"{x:.2f}" if x > 0 else na_text)
            display_df['div_yield'] = display_df['div_yield'].apply(lambda x: f"{x:.2f}%" if x > 0 else na_text)
            display_df['roe'] = display_df['roe'].apply(lambda x: f"{x:.2f}%" if x > 0 else na_text)
            display_df['price'] = display_df['price'].apply(lambda x: f"${x:.2f}" if x > 0 else na_text)
            display_df['yoy'] = display_df['yoy'].apply(lambda x: f"{x:.1f}%" if x != 0 else na_text)
            display_df['eps_growth'] = display_df['eps_growth'].apply(lambda x: f"{x:.1f}%" if x != 0 else na_text)
            
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
            if st.session_state.get('lang') == 'en':
                st.info("💡 Tip: Try increasing P/E or P/B limits, or lowering dividend yield requirements.")
            else:
                st.info("💡 提示：試著調高 P/E 或 P/B 上限，或降低殖利率要求。")
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
                    
                    c5, c6, c7, c8 = st.columns(4)
                    c5.metric(t('volatility'), f"{port_metrics.get('volatility', 0):.2f}%")
                    c6.metric("MDD", f"{port_metrics.get('max_drawdown', 0):.2f}%")
                    c7.metric(t('sharpe'), f"{port_metrics.get('sharpe', 0):.2f}")
                    c8.metric(t('sortino'), f"{port_metrics.get('sortino', 0):.2f}")
                    
                    st.subheader(t('cumulative'))
                    fig = go.Figure()
                    
                    # Normalize both to start from 0%
                    port_normalized = (port_ret / port_ret.iloc[0] - 1) * 100 if len(port_ret) > 0 else port_ret * 100
                    bench_normalized = (bench_ret / bench_ret.iloc[0] - 1) * 100 if len(bench_ret) > 0 else bench_ret * 100
                    
                    fig.add_trace(go.Scatter(x=port_ret.index, y=port_normalized, name=t('strategy'), line=dict(color=COLORS['success'], width=2)))
                    fig.add_trace(go.Scatter(x=bench_ret.index, y=bench_normalized, name=t('benchmark'), line=dict(color=COLORS['primary'], width=2)))
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor=COLORS['bg'],
                        plot_bgcolor=COLORS['bg'],
                        xaxis_title=t('date'),
                        yaxis_title=t('return_pct'),
                        yaxis=dict(tickformat=".1f")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show ticker list
                    st.markdown("---")
                    st.subheader(t('ticker_list'))
                    selected_stocks = st.session_state.selected[:50]
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.metric(t('stock_count'), f"{len(selected_stocks)} 檔")
                    with col2:
                        stock_chunks = [selected_stocks[i:i+15] for i in range(0, len(selected_stocks), 15)]
                        for chunk in stock_chunks:
                            st.code(", ".join(chunk), language=None)
                    
                    # Export buttons
                    st.markdown("---")
                    st.subheader(t('export_report'))
                    
                    col_exp1, col_exp2 = st.columns(2)
                    with col_exp1:
                        if st.button("📊 匯出選股清單 (CSV)"):
                            export_df = df[df['symbol'].isin(selected_stocks)][['symbol', 'name', 'sector', 'pe', 'pb', 'div_yield', 'roe', 'price', 'yoy', 'eps_growth']]
                            csv = export_df.to_csv(index=False)
                            st.download_button("下載 CSV", csv, "stock_screener_results.csv", "text/csv")
                    with col_exp2:
                        if st.button("📈 匯出回測報告"):
                            report = f"""# 量化選股回測報告
## 報告日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}

### 策略表現
- 總報酬: {port_metrics.get('total_return', 0):.2f}%
- 年化報酬: {port_metrics.get('annual_return', 0):.2f}%
- 大盤報酬: {bench_metrics.get('total_return', 0):.2f}%
- Alpha: {port_metrics.get('total_return', 0) - bench_metrics.get('total_return', 0):.2f}%
- 波動率: {port_metrics.get('volatility', 0):.2f}%
- MDD: {port_metrics.get('max_drawdown', 0):.2f}%
- 夏普比率: {port_metrics.get('sharpe', 0):.2f}
- 索提諾比率: {port_metrics.get('sortino', 0):.2f}

### 選股清單
{', '.join(selected_stocks)}

---
Generated by Quant Stock Screener
"""
                            st.download_button("下載報告 (TXT)", report, "backtest_report.txt", "text/plain")
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

st.markdown("---")
if st.session_state.get('lang') == 'zh':
    st.markdown("""
### 📖 名詞解釋

| 名詞 | 說明 |
|------|------|
| **P/E (本益比)** | 股價 ÷ 過去12個月 EPS。數值越低 = 可能被低估。 |
| **P/B (股價淨值比)** | 股價 ÷ 每股淨值。小於 1 可能表示被低估。 |
| **殖利率** | 年度股息 ÷ 股價 × 100%。顯示現金回報率。 |
| **ROE (股東權益報酬率)** | 淨利 ÷ 股本。衡量獲利能力。 |
| **營業利益率** | 營業利益 ÷ 營收。顯示每元銷售的獲利率。 |
| **負債比** | 總負債 ÷ 總資產。越高 = 財務槓桿越高。 |
| **YoY (年增率)** | 營收成長率，與去年同期相比。正值 = 成長。 |
| **EPS 成長率** | 季度 EPS 與去年同期相比。顯示獲利動能。 |
| **總報酬** | 期間起始到結束的整體漲跌幅。 |
| **年化報酬 (CAGR)** | 複合年均增長率 — 期間的年化報酬。 |
| **Alpha (超額報酬)** | 超越大盤的報酬。正值 = 表現優於大盤。 |
| **波動率** | 報酬的標準差。越高 = 價格波動越大。 |
| **夏普比率** | (報酬 - 無風險利率) ÷ 波動率。越高 = 風險調整後報酬越好。 |
| **索提諾比率** | 類似夏普，但只計算下行波動。專注在壞風險。 |
| **最大回撤** | 期間內最大谷底跌幅。 |

*數據更新日期：{0}*
""".format(datetime.now().strftime("%Y-%m-%d")))
else:
    st.markdown("""
### 📖 Glossary

| Term | Definition |
|------|------------|
| **P/E (Price-to-Earnings)** | Stock price divided by trailing 12-month EPS. Lower = potentially undervalued. |
| **P/B (Price-to-Book)** | Stock price divided by book value per share. < 1 may indicate undervaluation. |
| **Dividend Yield** | Annual dividends ÷ stock price × 100%. Shows cash return on investment. |
| **ROE (Return on Equity)** | Net income ÷ shareholders' equity. Measures profitability of shareholder capital. |
| **Profit Margin** | Net income ÷ revenue. Shows how much profit is extracted from each dollar of sales. |
| **Debt Ratio** | Total debt ÷ total assets. Higher = more financial leverage/risk. |
| **YoY (Year-over-Year)** | Revenue growth rate compared to same period last year. Positive = growth. |
| **EPS Growth** | Quarterly EPS change vs same quarter last year. Shows earnings momentum. |
| **Total Return** | Overall percentage gain or loss from start to end of period. |
| **Annual Return (CAGR)** | Compound Annual Growth Rate — annualized return over the period. |
| **Alpha** | Excess return above benchmark. Positive alpha = outperformance. |
| **Volatility** | Standard deviation of returns. Higher = more price fluctuation/risk. |
| **Sharpe Ratio** | (Return - Risk-free rate) ÷ Volatility. Higher = better risk-adjusted return. |
| **Sortino Ratio** | Like Sharpe, but only considers downside volatility. Focuses on bad risk. |
| **Max Drawdown** | Largest peak-to-trough decline during the period. |

*Data updated: {0}*
""".format(datetime.now().strftime("%Y-%m-%d")))