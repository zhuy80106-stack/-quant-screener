import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime

TAIWAN_STOCKS = [
    '2330', '2317', '2454', '2412', '2882', '2891', '1301', '1326', '1215', '3008',
    '2382', '2451', '2207', '2308', '2609', '2615', '2105', '8046', '2474', '2881',
    '2883', '2884', '2885', '2886', '2887', '2888', '2889', '2890', '2892', '3034',
    '2301', '2303', '2377', '2353', '2344', '2327', '2315', '2408', '2409', '2413',
    '2420', '2421', '2439', '2441', '2443', '2444', '2445', '2002', '2103'
]

USA_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK.B', 'JNJ', 'V',
    'PG', 'MA', 'UNH', 'HD', 'DIS', 'BAC', 'ADBE', 'CRM', 'NFLX', 'CSCO',
    'INTC', 'AMD', 'ORCL', 'IBM', 'QCOM', 'TXN', 'AVGO', 'COST', 'NKE', 'MCD',
    'BA', 'CAT', 'GE', 'JPM', 'GS', 'MS', 'WMT', 'CVX', 'XOM', 'KO',
    'PEP', 'T', 'VZ', 'MRK', 'PFE', 'ABBV', 'LLY', 'UNH', 'ISRG', 'BDX'
]

def get_val(info, *keys, default=0):
    for key in keys:
        val = info.get(key)
        if val is not None and val != default:
            return val
    return default

def fetch_one(symbol, market):
    ticker = f"{symbol}.TW" if market == "Taiwan" else symbol
    try:
        t = yf.Ticker(ticker)
        
        hist = t.history(period="1d", auto_adjust=True)
        if not hist.empty:
            price = hist['Close'].iloc[-1]
            info = t.info
        else:
            info = t.info
            price = get_val(info, 'currentPrice', 'regularMarketPrice', 'previousClose', default=0)
        
        time.sleep(0.2)
        
        dividend_yield = info.get('dividendYield')
        if isinstance(dividend_yield, (int, float)) and dividend_yield > 0:
            div_yield = dividend_yield if dividend_yield >= 1 else dividend_yield * 100
        else:
            dividend_rate = info.get('dividendRate') or info.get('lastDividendValue') or 0
            if isinstance(dividend_rate, (int, float)) and dividend_rate > 0 and price:
                div_yield = (dividend_rate / price) * 100
            else:
                div_yield = 0
        
        if div_yield > 20:
            div_yield = 0
        
        return {
            'symbol': symbol,
            'name': info.get('shortName', symbol),
            'sector': info.get('sector') or 'Unknown',
            'price': price,
            'pe': (get_val(info, 'trailingPE', 'forwardPE', 'PEG') or 0) if 0 < (get_val(info, 'trailingPE', 'forwardPE') or 0) < 200 else 0,
            'pb': get_val(info, 'priceToBook', 'bookValue') or 0,
            'div_yield': div_yield,
            'roe': min((get_val(info, 'returnOnEquity') or 0) * 100, 100),
            'debt': get_val(info, 'debtToEquity', 'totalDebt') or 0,
            'profit_margin': (get_val(info, 'profitMargins', 'profitMargin') or 0) * 100,
            'yoy': (get_val(info, 'revenueGrowth', 'revenue growth') or 0) * 100,
            'eps_growth': (get_val(info, 'earningsGrowth', 'epsGrowth') or 0) * 100,
            'market': market
        }
    except Exception as e:
        return {'symbol': symbol, 'market': market, 'error': str(e)}

def fetch_all():
    results = []
    
    print("Fetching Taiwan stocks...")
    with ThreadPoolExecutor(max_workers=10) as ex:
        results.extend(list(ex.map(lambda s: fetch_one(s, "Taiwan"), TAIWAN_STOCKS)))
    
    print("Fetching USA stocks...")
    with ThreadPoolExecutor(max_workers=10) as ex:
        results.extend(list(ex.map(lambda s: fetch_one(s, "USA"), USA_STOCKS)))
    
    df = pd.DataFrame(results)
    df = df[df['price'].notna()]
    df['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv('stocks_data.csv', index=False)
    print(f"Saved {len(df)} stocks to stocks_data.csv")

if __name__ == "__main__":
    fetch_all()