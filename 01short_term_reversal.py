# This is one of the better strategies for swing trading, focusing on short-term reversals based on RSI and volume spikes.
# It scans the S&P 500 for stocks that have a low RSI, significant price drop
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load S&P 500 tickers
sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
tickers = sp500['Symbol'].str.replace('.', '-', regex=False).tolist()

# RSI Function
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Scan for reversal candidates
results = []

for ticker in tickers[:50]:  # For quick test
    try:
        df = yf.download(ticker, period="1mo", interval="1d", progress=False)
        if len(df) < 15:
            continue
        df['RSI'] = compute_rsi(df['Close'])
        df['3D_Change'] = df['Close'].pct_change(3) * 100
        df['Volume_MA'] = df['Volume'].rolling(10).mean()
        df['Volume_Surge'] = df['Volume'] > 1.5 * df['Volume_MA']

        latest = df.iloc[-1]
        if latest['RSI'] < 30 and latest['3D_Change'] < -5 and latest['Volume_Surge']:
            results.append({
                'Ticker': ticker,
                'Date': df.index[-1].date(),
                'RSI': round(latest['RSI'], 2),
                '3D_Pct_Change': round(latest['3D_Change'], 2),
                'Volume': int(latest['Volume']),
            })
    except Exception as e:
        continue

# Display results
reversal_df = pd.DataFrame(results)
print(reversal_df)
