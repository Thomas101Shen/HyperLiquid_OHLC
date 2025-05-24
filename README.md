# Hyperliquid OHLC Data Fetcher

This script fetches OHLC (Open, High, Low, Close) data for a all cryptocurrency trading pairs using HL's API in real-time.

---

## Features

- Real time data from HyperLiquid
- Generates trading signals and sends notifications
- Retrieves OHLC data for the specified trading pair and interval.
- Logs errors to a file (`error_log.txt`) for debugging. (Only errors in main.py errors in the websocket connection still need some work to log, but they show up in the console)
- Test data to test TradingSignalGenerator
- TrainingSignalGenerator to generate signals and notifications (via telegram)
- Coin_fetcher which will fetch coins using leverage as a filter
- HyperFetch, containing DataFetcher which will fetch and generate OHLC data (pass in )
- sample .env file
- And more!

---

## Requirements

- Dependencies are included in the requirements.txt file
- HL api key and secret
- Telegram bot token and chatids

---

## Setup

1. Clone this repository or copy the script to your local environment.
2. Install the required Python packages:
   `pip install -r requirements.txt`
It is recomended to use a venv
```
Python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```
Warning: I used python 3.10, 3.8 or higher might work, after 3.10 won't work since pandas-ta is used (but that library causes more harm than good here,
maybe manually calcululating indicators will make this program more robust)
(Note: HL uses UTC for timestamps)
Have fun!

## Biggest problems to be explored:
Tradingsignalgenerator performs dataframe-wide operations every time, when it's only needed on the first operation or if the program is restarted. It also removes all previous data on run (process_csv_files will override all previous data.)

Position logger stopped working some updates ago, and there are problems with the program restarting and the positions being incorrect (although the program runs fine regardless, be warned the error logs might be full of position logging errors)

If the telegram bot for position logger is different from the trade notification one, then you must adjust the .env file accordingly