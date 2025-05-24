import time
import pandas as pd
from datetime import datetime, timedelta
from hyperliquid.info import Info
from hyperliquid.utils.constants import MAINNET_API_URL
import warnings
import re
import os

warnings.filterwarnings("ignore")

class DataFetcher:
    def __init__(self, coins=["BTC", "ETH", "SOL"]):


        # Initialize the Info class
        self.info = Info(MAINNET_API_URL, skip_ws=True)

        if coins == "all":
            available_coins = self.info.all_mids()
            # print(available_coins)
            self.coins = [re.sub(r'[<>:"/\\|?*]', '_',coin) for coin in available_coins.keys() if coin[0] != '@']
        else:
            # Define list of coins to track
            self.coins = coins


        # Placeholder for OHLC data
        self.ohlc_data = {coin: [] for coin in self.coins}
        # print("PURR_USDC" in self.ohlc_data.keys())
        # print(self.ohlc_data.keys())

    # Fetch mid-prices at intervals to build OHLC manually
    def fetch_prices(self, ohlc_data, interval_seconds=1, duration_minutes=1):
        start_time = datetime.utcnow().replace(second=0, microsecond=0)

        while datetime.utcnow() < start_time + timedelta(minutes=1):
            mids = self.info.all_mids()
            timestamp = datetime.now()

            for coin in self.coins:
                price = float(mids.get(coin, 0))
                if price > 0:
                    ohlc_data[coin].append({'timestamp': timestamp, 'price': price})

            time.sleep(interval_seconds)  # Sleep for the interval duration

    # Aggregating prices into OHLC
    def generate_ohlc(self, df):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        ohlc = df.resample('1T').agg({
            'price': ['first', 'max', 'min', 'last']
        })

        # Rename the columns to remove the multi-level structure created by agg()
        ohlc.columns = ohlc.columns.droplevel(0)  # Drops first leve (price)
        ohlc = ohlc.rename(columns={'first': 'Open', 'max': 'High', 'min': 'Low', 'last': 'Close'})
        return ohlc


    # def fetch_ohlc(self):
    #     self.fetch_prices(self.ohlc_data)
    #     # print(self.ohlc_data)

    #     # Convert into a DataFrame and generate OHLC
    #     for coin in self.coins:
    #         df = pd.DataFrame(self.ohlc_data[coin])
    #         if df.empty:
    #             continue
    #         file_path = f"crypto_data/{coin}_data.csv"
    #         if os.path.exists(file_path):
    #             prev_data = pd.read_csv(file_path)
    #             prev_data.set_index('timestamp', inplace=True)
    #             # if "timestamp" in prev_data.columns:
    #             #     prev_data['timestamp'] = pd.to_datetime(prev_data['timestamp'])
    #             #     prev_data.set_index('timestamp', inplace=True)
    #         else:
    #             prev_data = pd.DataFrame()

    #         self.ohlc_data[coin] = []
    #         new_data = self.generate_ohlc(df)
    #         updated_data = pd.concat([prev_data, new_data])

    #         # if updated_data.iloc[:-1].index == datetime.utcnow().replace(second=0, microsecond=0):
    #         # updated_data = updated_data.iloc[:-1]
    #         # if len(updated_data) != updated_data["timestamp"]
    #         updated_data = updated_data.iloc[-142:]

    #         # print(updated_data.columns)

    #         # print(f"\nOHLC data for {coin}:\n")
    #         # print(updated_data)
    #         # if coin=="PURR_USDC":
    #         #     print(updated_data)

    #         updated_data.to_csv(file_path)

    def fetch_ohlc(self):
        self.fetch_prices(self.ohlc_data)
        cur_time = datetime.now().replace(second=0, microsecond=0)

        for coin in self.coins:
            df = pd.DataFrame(self.ohlc_data[coin])
            if df.empty:
                continue

            file_path = f"crypto_data/{coin}_data.csv"
            if os.path.exists(file_path):
                prev_data = pd.read_csv(file_path)
                prev_data.set_index('timestamp', inplace=True)
            else:
                prev_data = pd.DataFrame()

            self.ohlc_data[coin] = []
            new_data = self.generate_ohlc(df)
            updated_data = pd.concat([prev_data, new_data])
            last_timestamp = pd.to_datetime(updated_data.index[-1])
            if last_timestamp == cur_time:
                updated_data = updated_data.iloc[:-1]

            # Remove duplicates, keeping the last entry per timestamp
            # updated_data = updated_data.drop_duplicates(subset='timestamp', keep='last')
            
            updated_data = updated_data.iloc[-142:]

            updated_data.to_csv(file_path, index=True)
            # Potential problem with pairs traded coins ex: PURR/USDC which should be PURR_USDC_data.csv


"""
from HyperFetch import DataFetcher
data_fetcher = DataFetcher()
while True:
    data_fetcher.fetch_ohlc()

Idea: instead of checking if path exists have a cache or statetime variable

class DataProcessor:
    def __init__(self):
        self.state = {
            'initialized_files': set(),
            'last_processed': {}
        }

    def process_data(self, coin, data):
        file_path = f"crypto_data/{coin}_data.csv"
        if file_path not in self.state['initialized_files']:
            self.initialize_file(file_path)
            self.state['initialized_files'].add(file_path)
        
        # Proceed with data processing
        # Update last processed timestamp

        self.state['last_processed'][coin] = data['timestamp'].max()
        # Reccomend opening data with a read and parse_dates="timestamp"

    def initialize_file(self, file_path):
        # File initialization logic here
        pass

"""        





