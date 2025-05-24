import time
import pandas as pd
from datetime import datetime
from hyperliquid.info import Info
from hyperliquid.utils.constants import MAINNET_API_URL
import warnings
import os

"""
This was previous working data fetch code until I turned it into a class
"""
warnings.filterwarnings("ignore")

# Initialize the Info class
info = Info(MAINNET_API_URL, skip_ws=True)

# Define list of pairs to track
pairs = ["BTC", "ETH", "SOL"]

# Placeholder for OHLC data
ohlc_data = {pair: [] for pair in pairs}

# for pair in pairs:
#     df = pd.DataFrame(ohlc_data[pair])
#     # df.drop(columns=[f"{pair}"], inplace=True)  # Check if need to do this everytime concat to df (at bottom)
#     df.to_csv(f"{pair}_ohlc.csv", index=False)

# Fetch mid-prices at intervals to build OHLC manually
def fetch_prices(ohlc_data, interval_seconds=1, duration_minutes=1):
    start_time = time.time()
    till_next_min = 60 - start_time % 60

    while time.time() < start_time + till_next_min - 0.2:
        mids = info.all_mids()
        timestamp = datetime.now()

        for pair in pairs:
            price = float(mids.get(pair, 0))
            if price > 0:
                ohlc_data[pair].append({'timestamp': timestamp, 'price': price})

        time.sleep(interval_seconds/2)  # Sleep for the interval duration

# Aggregating prices into OHLC
def generate_ohlc(df):
    # df.set_index('timestamp', inplace=True)

    ohlc = df.resample('1T', on="timestamp").agg({
        'price': ['first', 'max', 'min', 'last']
    })

    # Rename the columns to remove the multi-level structure created by agg()
    ohlc.columns = ohlc.columns.droplevel(0)  # Drops first leve (price)
    ohlc = ohlc.rename(columns={'first': 'Open', 'max': 'High', 'min': 'Low', 'last': 'Close'})
    # print("Genrate ohlc output:")
    # print(ohlc)
    return ohlc


if __name__ == "__main__":
    # cur_time = time.time()
    # till_next_min = 60 - cur_time % 60
    # print(f"Seconds till program starts: {till_next_min}")
    # time.sleep(till_next_min)
    # Fetch data
    while True:
        fetch_prices(ohlc_data)

        # Convert into a DataFrame and generate OHLC
        for pair in pairs:
            file_path = f"{pair}_ohlc.csv"
            if os.path.exists(file_path):
                prev_data = pd.read_csv(file_path)
                prev_data.set_index('timestamp', inplace=True)
            else:
                prev_data = pd.DataFrame()
            df = pd.DataFrame(ohlc_data[pair])
            new_data = generate_ohlc(df)
            updated_data = pd.concat([prev_data, new_data])
            updated_data = updated_data.iloc[:-1]

            # print(updated_data.columns)

            # print(f"\nOHLC data for {pair}:\n")
            # print(updated_data)

            updated_data.to_csv(file_path)
            ohlc_data[pair] = []