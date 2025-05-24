#!/usr/bin/env python3
import time
import logging
import traceback  # Import traceback module
from HyperFetch import DataFetcher
import pandas as pd
from TradingSignalGenerator import TradingSignalGenerator
from PositionLogger import PositionLogger
import os
from Coin_fetcher import coin_fetcher

# Configure logging
logging.basicConfig(filename="error_logs.log",
                    level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

MAX_RETRIES = 5  # Maximum number of retries before giving up
BASE_DELAY = 2  # Initial delay in seconds
coins = coin_fetcher()

if __name__ == "__main__":
    data_fetcher = DataFetcher(coins)  # pass in "all" to get all pairs
    signal_generator = TradingSignalGenerator()
    position_logger = PositionLogger()

    retry_count = 0
    count = 0

    while True:
        try:
            data_fetcher.fetch_ohlc()
            signal_generator.process_csv_files('./crypto_data')

            # remove bottom while deploying for improved accuracy
            if os.path.getsize("./signal_data/positions.csv") != 0:
                position_logger.store_data("./signal_data/positions.csv")


            retry_count = 0  # Reset retries

        except Exception as e:
            logging.error("An error occurred: %s", e)
            logging.error("Traceback:\n%s", traceback.format_exc())

            retry_count += 1
            if retry_count > MAX_RETRIES:
                logging.error("Max retries reached. Exiting...")
                break

