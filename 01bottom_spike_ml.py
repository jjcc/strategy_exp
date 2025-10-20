# ML Notebook Structure for Bottom Spike Reversal Classifier

import pandas as pd
import yfinance as yf
import ta
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt

# ✅ Step 1: Define Ticker List and Download Data
tickers = ['TGT', 'DHI', 'LEN', 'NVR', 'PHM']
start = '2024-07-01'
end = '2025-07-02'
data = yf.download(tickers, start=start, end=end, group_by='ticker', auto_adjust=True)

# ✅ Step 2: Feature Engineering Function
def generate_features(df, gamma_flip=None):
    df = df.copy()
    df['Return'] = df['Close'].pct_change()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['Volatility'] = df['Close'].rolling(5).std()
    df['Max_High'] = df['Close'].cummax()
    df['Drop'] = (df['Close'] - df['Max_High']) / df['Max_High']
    df['BB_H'] = ta.volatility.BollingerBands(df['Close']).bollinger_hband()
    df['BB_L'] = ta.volatility.BollingerBands(df['Close']).bollinger_lband()
    df['BB_Dist'] = (df['Close'] - df['BB_L']) / (df['BB_H'] - df['BB_L'])
    df['Volume_Change'] = df['Volume'].pct_change()
    if gamma_flip:
        df['GEX_Flip_Dist'] = df['Close'] - gamma_flip
        df['In_Positive_GEX'] = (df['Close'] > gamma_flip).astype(int)
    else:
        df['GEX_Flip_Dist'] = 0
        df['In_Positive_GEX'] = 0
    return df.dropna()

# ✅ Step 3: Labeling Function (Manual pattern tagging)
def create_labels(df, positive_dates):
    '''
    Set labels based on manually identified spike days.
    positive_dates: List of dates where a spike is expected.'''
    df = df.copy()
    df['Label'] = 0
    df.loc[df.index.isin(positive_dates), 'Label'] = 1
    return df

# ✅ Step 4: Build Dataset
# These are manually identified spike days (before/around breakout)
spike_dates = {
    'TGT': ['2025-07-01'],
    'DHI': ['2025-07-01'],
    'LEN': ['2025-07-01'],
    'NVR': ['2025-07-01'],
    'PHM': ['2025-07-01']
}

# Provide manually identified gamma flip levels
gamma_flip_levels = {
    'TGT': 96.37,
    'DHI': 123.92,
    'LEN': 115.27,
    'NVR': 9500,  # hypothetical
    'PHM': 105.12
}

data_rows = []

for ticker in tickers:
    df = data[ticker].copy()
    gflip = gamma_flip_levels.get(ticker, None)
    df = generate_features(df, gamma_flip=gflip)
    pos_dates = pd.to_datetime(spike_dates.get(ticker, []))
    df = create_labels(df, pos_dates)
    df['Ticker'] = ticker
    data_rows.append(df)

combined_df = pd.concat(data_rows)

# ✅ Step 5: Add negative samples from other dates
negatives = combined_df[combined_df['Label'] == 0].sample(n=100, random_state=42)
positives = combined_df[combined_df['Label'] == 1]
dataset = pd.concat([positives, negatives])

# ✅ Step 6: Prepare Features and Labels
features = ['RSI', 'Volatility', 'Drop', 'BB_Dist', 'Volume_Change', 'GEX_Flip_Dist', 'In_Positive_GEX']
X = dataset[features]
y = dataset['Label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# ✅ Step 7: Train Model
model = GradientBoostingClassifier()
model.fit(X_train, y_train)

# ✅ Step 8: Evaluate Model
y_pred = model.predict(X_test)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))
print("ROC AUC:", roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))

# ✅ Step 9: Feature Importance
plt.figure(figsize=(8,5))
feat_imp = pd.Series(model.feature_importances_, index=features)
feat_imp.sort_values().plot(kind='barh')
plt.title('Feature Importance')
plt.tight_layout()
plt.show()
