import unittest

import pandas as pd
import numpy as np



class TestDataProcessor(unittest.TestCase):
    """Unit tests for data processing functions.
    """

    def setUp(self):
        # Sample data for testing
        pass

    def test_group_data(self):
        """
        Test grouping and summing data by Date, Transaction Type, and Symbol.
        """
        file = "data/ib_trades_lateDec_earlyJan.csv"
        file2 = "data/ib_trades_Nov_midDec.csv"
        
        df1 = pd.read_csv(file, delimiter="\t")
        df2 = pd.read_csv(file2, delimiter="\t")
        df = pd.concat([df1, df2], ignore_index=True)
        
        # 1) Columns we want to sum
        sum_cols = ["Quantity", "Gross Amount", "Commission", "Net Amount"]
        
        # 2) Make Date a date (not datetime if you want pure “by day”)
        df["Date"] = pd.to_datetime(df["Date"]).dt.date
        
        # 3) Coerce numeric columns:
        #    - remove commas and dollar signs
        #    - turn "–" or "-" placeholders into NaN
        def to_num(s):
            # work on strings, strip separators/currency marks
            s = s.astype(str).str.strip()
            s = s.replace({"-": np.nan, "–": np.nan})  # placeholders -> NaN
            s = s.str.replace(r"[\$,]", "", regex=True)  # drop $ and commas
            return pd.to_numeric(s, errors="coerce")
        
        for c in sum_cols:
            df[c] = to_num(df[c])
        
        # 4) (Optional) drop rows with no Symbol if you only want real tickers
        #    Comment this line out if you DO want those rows included.
        df = df[df["Symbol"].notna() & (df["Symbol"] != "-")]
        
        # 5) Group by Date, Transaction Type, Symbol and sum
        agg = (
            df
            .groupby(["Date", "Transaction Type", "Symbol"], as_index=False)[sum_cols]
            .sum(min_count=1)   # keeps NaN if an entire group is missing data
            .sort_values(["Date", "Transaction Type", "Symbol"])
        )
        print(agg)
        agg.to_csv("data/ib_trades_grouped_Nov_earlyJan.csv", index=False)

