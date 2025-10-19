"""
Calculate profit from triplet transactions: Sell, Buy, Payment in Lieu, none YieldMax.
"""
import pandas as pd

#df = pd.read_csv("data/ib_trades_grouped.csv")
df = pd.read_csv("data/ib_trades_grouped_Nov_earlyJan.csv")
df["Date"] = pd.to_datetime(df["Date"])

df_ym_result = pd.read_csv("data/ib_trades_triplets_Nov_earlyJan.csv")
syms_ym = df_ym_result["Symbol"].unique().tolist()

# filter non-YieldMax symbols
df = df[~df["Symbol"].isin(syms_ym)].copy()


# 1. Keep only rows that are part of these three types
df = df[df["Transaction Type"].isin(["Buy", "Sell", "Payment in Lieu"])].copy()

# 2. Sort by symbol and date
df = df.sort_values(["Symbol", "Date"])

# 3. Identify possible triplets
doubles = []

for sym, g in df.groupby("Symbol"):
    g = g.sort_values("Date").reset_index(drop=True)

    offset = 2
    if sym == "MFIC":
        print(g)
        offset = 3

    # find a sell followed by a buy then a lieu (within few days)
    for i in range(len(g) - offset):
        if sym == "MFIC":
            sell = g.iloc[i]
            buy  = g.iloc[i+1]
            sell2  = g.iloc[i+2]
            # combine two sells before buy and lieu

            lieu = g.iloc[i+3]
            quantity = sell["Quantity"] * (-1) + sell2["Quantity"] * (-1)
            i += 1
        else:
            sell = g.iloc[i]
            buy  = g.iloc[i+1]
            lieu = g.iloc[i+2]
            quantity = sell["Quantity"] * (-1)
        price = sell["Gross Amount"] / sell["Quantity"] if sell["Quantity"] != 0 else 0
        if (
            sell["Transaction Type"] == "Sell"
            and buy["Transaction Type"] == "Buy"
            and lieu["Transaction Type"] == "Payment in Lieu"
            and (0 < (buy["Date"] - sell["Date"]).days <= 2) if sym != "MFIC" else (0 < (buy["Date"] - sell["Date"]).days <= 5)
            #and (0 <= (lieu["Date"] - buy["Date"]).days <= 3)
        ):
            gain = sell["Net Amount"] + buy["Net Amount"] + lieu["Net Amount"] if sym != "MFIC" else sell["Net Amount"] + sell2["Net Amount"] + buy["Net Amount"] + lieu["Net Amount"]
            #triplets.append({
            doubles.append({
                "Symbol": sym,
                "Sell_Date": sell["Date"],
                "Buy_Date": buy["Date"],
                "Lieu_Date": lieu["Date"],
                "Sell_Net": sell["Net Amount"] if sym != "MFIC" else sell["Net Amount"] + sell2["Net Amount"],
                "Buy_Net": buy["Net Amount"],
                "Lieu_Net": lieu["Net Amount"],
                "Gain": gain,
                "Price": price,
                "Quantity": quantity
            })

triplet_df = pd.DataFrame(doubles)

print(triplet_df)

triplet_df["Gain"] = triplet_df["Gain"].round(2)
sum_of_gains = triplet_df["Gain"].sum()
print(f"Sum of Gains (non-YieldMax): {sum_of_gains}")
triplet_df.to_csv("data/ib_trades_triples_Nonym_Nov_earlyJan.csv", index=False)
