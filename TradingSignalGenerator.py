import requests
import os
import ast
import pandas as pd
import pandas_ta as ta
import numpy as np
from load_env import load_env
from filelock import FileLock


class TradingSignalGenerator:
    def __init__(self, data_dir="test_data"):
        # Load environment variables
        load_env()
        os.makedirs("./signal_data", exist_ok=True)
        self.bot_token = os.getenv("bot_token")
        self.chat_ids = os.getenv("chat_ids")
        self.data_dir = data_dir
        self.long_positions = pd.DataFrame(columns=["symbol", "timestamp", "close"])
        self.positions_path = "signal_data/positions.csv"
        self.lock = FileLock("./signal_data/positions.lock")

        # Convert chat_ids string to a Python list
        if self.chat_ids:
            self.chat_ids = ast.literal_eval(self.chat_ids)

        # Dynamically create position tracking dictionary based on files in the directory
        self.is_long = self.initialize_position_tracking()

    def initialize_position_tracking(self):
        """Initialize the is_long dictionary based on the files in the directory."""
        is_long_dict = {}
        for file in os.listdir(self.data_dir):
            if file.endswith("_data.csv"):
                coin = file.replace("_data.csv", "")
                is_long_dict[coin] = False  # Default to not in a position
        # pd.DataFrame(is_long_dict).to_csv("./fetcher_positions.csv")
        return is_long_dict

    def send_telegram_notification(self, message, df=None, max_attempts=3):
        """Send a notification to Telegram chat when a signal is generated."""
        if not self.chat_ids or not isinstance(self.chat_ids, list):
            print("No valid chat IDs provided.")
            return

        for chat_id in self.chat_ids:
            success = False
            attempts = 0

            while not success and attempts < max_attempts:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

                # Format message with DataFrame row if provided
                if df is not None:
                    df_text = df.to_string()  # Convert current observation to text
                    message += f"\n\nLatest Data:\n<pre>{df_text}</pre>"

                payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
                response = requests.post(url, data=payload)
                attempts += 1

                if response.status_code == 200:
                    # print(f"Notification sent successfully to chat_id {chat_id} on attempt {attempts}.")
                    success = True
                else:
                    print(f"Attempt {attempts} failed for chat_id {chat_id}. Error: {response.text}")
                    if attempts < max_attempts:
                        print("Retrying...")

    def calculate_rsi(self, close, rsi_length=14):
        """Calculate Relative Strength Index (RSI)."""
        return ta.rsi(close, length=rsi_length)

    def generate_signals(self, rsi, rsiOversold, rsiOverbought):
        """Generate buy and sell signals based on WaveTrend and RSI conditions."""
        buy_signals = (rsi <= rsiOversold)
        sell_signals = (rsi >= rsiOverbought)
        return buy_signals, sell_signals

    def create_indicators(self, df):

        # May want to implement combine_first down the line to ensure it only updates new values instead of the whole df
        df['rsi'] = self.calculate_rsi(df['Close'])
        return df


    def enter_long(self, coin, latest_data, buy_signals):
        message = f"Buy Signal for {coin}"
        self.send_telegram_notification(message, latest_data)
        self.is_long[coin] = True  # Update position status
        save_path = os.path.join("./signal_data", f"{coin}_buy.csv")

        if os.path.exists(save_path):
            old_data = pd.read_csv(save_path)
            new_data = pd.concat([old_data, latest_data])
            new_data.set_index("timestamp", inplace=True)
            new_data.to_csv(save_path)
        else:
            latest_data.to_csv(save_path)

        # if os.path.exists(save_path):
        #     old_signal = pd.read_csv(save_path)
        #     new_signal = pd.concat([old_signal, buy_signals])
        #     new_signal.set_index("timestamp", inplace=True)
        #     new_signal.to_csv(save_path)
        # else:
        #     buy_signals.to_csv(save_path)

        latest_data["symbol"] = coin
        with self.lock:
            self.long_positions = pd.concat([self.long_positions, latest_data])
            self.long_positions.to_csv("./position_data.csv", index=False)
        return

    def exit_long(self, coin, latest_data, sell_signals):
        message = f"Sell Signal for {coin}"
        self.send_telegram_notification(message, latest_data)
        self.is_long[coin] = False  # Update position status
        save_path = os.path.join("./signal_data", f"{coin}_sell.csv")

        if os.path.exists(save_path):
            old_data = pd.read_csv(save_path)
            new_data = pd.concat([old_data, latest_data])
            new_data.set_index("timestamp", inplace=True)
            new_data.to_csv(save_path)
        else:
            latest_data.to_csv(save_path)

        # if os.path.exists(save_path):
        #     old_signal = pd.read_csv(save_path)
        #     new_signal = pd.concat([old_signal, sell_signals])
        #     new_signal.set_index("timestamp", inplace=True)
        #     new_signal.to_csv(save_path)
        # else:
        #     sell_signals.to_csv(save_path)

        with self.lock:
            self.long_positions = self.long_positions[self.long_positions["symbol"]!=coin]
            self.long_positions.to_csv("./position_data.csv", index=False)
        return

    def process_csv_files(self, data_dir="./test_data", timestamp_col="timestamp"):
        """Iterate through all CSV files in the directory, filter valid data, and generate signals."""
        for file in os.listdir(data_dir):
            if file.endswith(".csv"):  # and os.path.getsize(file) > 0: Figure out why it only works if data dir is empty particularly crypto_data
                coin = file.replace("_data.csv", "")
                file_path = os.path.join(data_dir, file)

                if os.path.getsize(file_path) < 0:  # rethink this logic
                    continue

                df = pd.read_csv(file_path)
                if len(df) < 60:
                    continue

                # df[timestamp_col] = pd.to_datetime(df[timestamp_col], format="%Y-%m-%d %H:%M:%S", errors="coerce")
                df.index = pd.to_datetime(df[timestamp_col])
                df = df.sort_index(ascending=True)

                # May implement a way to only process new information when calcuating indicators if neccessary

                # file_path = f"signal_data/{coin}_signal.csv"
                df = self.create_indicators(df)

                # if os.path.isfile(file_path):
                #     Try to read existing data in signal instead of overriding, main problem is conserving timestamps
                #     signal_data = pd.read_csv(file_path)
                #     df = pd.concat([signal_data, df.iloc[-1:]]).head(142)
                # Timestamp issue shoulnd't be as big of a problem anymore, next step is to optimize computation power
                # by only calculating when neccessary.

                # print(df.columns)
                buy_signals, sell_signals = self.generate_signals(df['rsi'], 30, 70)
                # print(df)

                latest_data = df.iloc[-1:].copy()  # Get the latest row of data
                # print(latest_data)
                # print(df.columns)
                # print(df.head())
                df.to_csv(f"./signal_data/{coin}_signal.csv", index=False)

                # Check if a buy signal occurs and update position status
                if buy_signals.iloc[-1]:
                    if not self.is_long.get(coin, False):  # Only send signal if not already in a long
                        self.enter_long(coin, latest_data, buy_signals)

                # Check if a sell signal occurs and update position status
                if sell_signals.iloc[-1]:
                    if self.is_long.get(coin, False):  # Only send signal if not already in a short
                        self.exit_long(coin, latest_data, sell_signals)

# Instantiate and execute
if __name__ == "__main__":
    signal_generator = TradingSignalGenerator()
    signal_generator.process_csv_files()