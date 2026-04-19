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

def fetch_one(symbol, market):
    ticker = f"{symbol}.TW" if market == "Taiwan" else symbol
    try:
        t = yf.Ticker(ticker)
        info = t.info
        time.sleep(0.1)
        
        price = info.get('currentPrice') or info.get('regularMarketPrice')
        
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
            'pe': info.get('trailingPE') or 0,
            'pb': info.get('priceToBook') or 0,
            'div_yield': div_yield,
            'roe': min((info.get('returnOnEquity') or 0) * 100, 100),
            'debt': info.get('debtToEquity') or 0,
            'profit_margin': (info.get('profitMargins') or 0) * 100,
            'yoy': (info.get('revenueGrowth') or 0) * 100,
            'eps_growth': (info.get('earningsGrowth') or 0) * 100,
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