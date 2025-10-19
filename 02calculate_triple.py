
"""
Calculate profit from triplet transactions: Sell, Buy, Payment in Lieu for YieldMax etfs.
Input: CSV file with grouped trades from IB trade log
"""
import pandas as pd

#df = pd.read_csv("data/ib_trades_grouped.csv")
df = pd.read_csv("data/ib_trades_grouped_Nov_earlyJan.csv")
df["Date"] = pd.to_datetime(df["Date"])

# 1. Keep only rows that are part of these three types
df = df[df["Transaction Type"].isin(["Buy", "Sell", "Payment in Lieu"])].copy()

# 2. Sort by symbol and date
df = df.sort_values(["Symbol", "Date"])

# 3. Identify possible triplets
triplets = []

for sym, g in df.groupby("Symbol"):
    g = g.sort_values("Date").reset_index(drop=True)

    # find a sell followed by a buy then a lieu (within few days)
    for i in range(len(g) - 2):
        sell = g.iloc[i]
        buy  = g.iloc[i+1]
        lieu = g.iloc[i+2]
        quantity = sell["Quantity"] * (-1)
        price = sell["Gross Amount"] / sell["Quantity"] if sell["Quantity"] != 0 else 0
        if (
            sell["Transaction Type"] == "Sell"
            and buy["Transaction Type"] == "Buy"
            and lieu["Transaction Type"] == "Payment in Lieu"
            and (0 < (buy["Date"] - sell["Date"]).days <= 2)
            and (0 <= (lieu["Date"] - buy["Date"]).days <= 3)
        ):
            quantity = sell["Quantity"] * (-1) 
            if sell["Quantity"] * (-1) != buy["Quantity"]:
                print(f"Warning: Quantity mismatch for {sym} on {sell['Date']}, sell qty: {sell['Quantity']}, buy qty: {buy['Quantity']}")
                if sell["Quantity"] * (-1) < buy["Quantity"]:
                    print("#Very strange: sell quantity less than buy quantity, ignoring")
                    continue
                else:
                    adj_sell_net = sell["Net Amount"] * (quantity/sell["Quantity"] * -1 )
                    # Adjust quantity
                    quantity = buy["Quantity"]
                    profit = adj_sell_net + buy["Net Amount"] + lieu["Net Amount"]

            else:
                adj_quantity = quantity
                profit = sell["Net Amount"] + buy["Net Amount"] + lieu["Net Amount"]
                adj_sell_net = sell["Net Amount"]
            profit_rate = profit / abs(adj_sell_net) if adj_sell_net != 0 else 0
            profit_rate = profit_rate.round(2)
            triplets.append({
                "Symbol": sym,
                "Sell_Date": sell["Date"],
                "Buy_Date": buy["Date"],
                "Lieu_Date": lieu["Date"],
                "Sell_Net": adj_sell_net,
                "Buy_Net": buy["Net Amount"],
                "Lieu_Net": lieu["Net Amount"],
                "Profit": profit,
                "Profit_rate": profit_rate,
                "Price": price,
                "Quantity": quantity
            })

triplet_df = pd.DataFrame(triplets)

print(triplet_df)

triplet_df["Profit"] = triplet_df["Profit"].round(2)
sum_profit = triplet_df["Profit"].sum()
print(f"Total Profit from triplets: ${sum_profit:.2f}")
triplet_df.to_csv("data/ib_trades_triplets_Nov_earlyJan_2.csv", index=False)
