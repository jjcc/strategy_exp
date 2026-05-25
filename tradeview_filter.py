"""
Test for tradeview filter.
"""
import pandas as pd
from tradingview_screener import Query, Column

q = Query().select(
    'name',
    'close',
    'EMA5',
    'EMA12',
    'EMA26'
#).set_markets('america').set_timeframe(Interval.INTERVAL_1_DAY
).where(
    # EMA alignment
    Column('EMA5') > Column('EMA12'),
    Column('EMA12') > Column('EMA26'),
)
count, results = q.get_scanner_data()
df = pd.DataFrame(results)

# Convergence filter in pandas (column arithmetic not supported in screener)
if not df.empty:
    df = df[
        (abs(df['EMA5'] - df['EMA12']) / df['close'] > 0.01) &
        (abs(df['EMA12'] - df['EMA26']) / df['close'] > 0.01)&
        (abs(df['EMA5'] - df['EMA12']) / df['close'] < 0.03) &
        (abs(df['EMA12'] - df['EMA26']) / df['close'] < 0.03)
    ]
    df = df[~df['name'].str.contains('/')]
    df = df[~df['ticker'].str.contains('OTC')]

print(f"Total stocks found: {len(df)}")
print(df)