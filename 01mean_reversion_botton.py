import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ta
import yfinance as yf

def detect_bottom_spike(ticker, start="2025-01-01", drop_threshold=-0.3, spike_threshold=0.05):
    # Load data
    df = yf.download(ticker, start=start, end="2025-07-02")
    df = df.xs('TGT', level=1, axis=1)
    df = df.dropna()

    # Technicals
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['BB_Low'] = ta.volatility.BollingerBands(df['Close']).bollinger_lband()
    df['BB_Upper'] = ta.volatility.BollingerBands(df['Close']).bollinger_hband()
    df['Volatility'] = df['Close'].rolling(5).std()
    df['Return'] = df['Close'].pct_change()

    # 30-day rolling drop
    df['Roll_Max'] = df['Close'].rolling(30).max()
    df['Drop'] = (df['Close'] - df['Roll_Max']) / df['Roll_Max']

    # Spike condition
    df['Spike'] = (df['Return'] > spike_threshold) & (df['Drop'] < drop_threshold)

    return df

def plot_signals(df, ticker):
    plt.figure(figsize=(14, 6))
    plt.plot(df['Close'], label='Close Price')
    plt.plot(df['BB_Low'], linestyle='--', alpha=0.3, label='Lower BB')
    plt.plot(df['BB_Upper'], linestyle='--', alpha=0.3, label='Upper BB')

    # Mark spikes
    spikes = df[df['Spike']]
    plt.scatter(spikes.index, spikes['Close'], color='red', label='Spike Signal', zorder=5)

    plt.title(f"{ticker} - Bottom Spike Detection")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # === Run for TGT ===
    ticker = "TGT"
    df = detect_bottom_spike(ticker)
    plot_signals(df, ticker)
