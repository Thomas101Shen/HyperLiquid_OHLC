# HyperLiquid OHLC Fetcher

This project fetches real-time OHLC (Open, High, Low, Close) data for all cryptocurrency trading pairs listed on the HyperLiquid exchange. It includes tools for signal generation, position logging, and Telegram alerts to support systematic trading research and execution.

---

## Features

- Real-time data streaming from HyperLiquid API
- Generates RSI-based trading signals
- Sends trade notifications via Telegram
- Modular structure (data fetcher, signal generator, coin filter, logger)
- Handles leveraged coin filtering
- Includes test data and signal output for verification
- Logs errors to `error_log.txt`
- Configurable via `.env` file

---

## Requirements

- Python 3.8 or 3.10 (pandas-ta may cause issues with newer versions)
- `.env` file containing credentials (example below)
- A persistent runtime environment (cloud VM or long-running process recommended)

```text
api_key=YOUR_HYPERLIQUID_API_KEY
api_secret=YOUR_SECRET
bot_token=YOUR_TELEGRAM_BOT_TOKEN
chat_ids=YOUR_TELEGRAM_CHAT_ID
positions_token=SECOND_BOT_TOKEN_IF_USED
```

Install dependencies:

```bash
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Quick Start

1. **Test the Trading Signal Generator**:

```bash
python TradingSignalGenerator.py
```

Inspect the `signal_data/` folder. Each file shows RSI signals applied to OHLC data.

2. **Create config.json file**

Refer to HL's official sdk documentation [here][https://github.com/hyperliquid-dex/hyperliquid-python-sdk]

3. **Create HL account**

4. **Crate Telegram Bot and start a chat with it**
[Reference][https://core.telegram.org/bots/api]

5. **Populate .env and config.json with HL addresses and Telegram bot info**

6. **Start Live Data Fetching and Alerts**:

```bash
python main.py
```

Live trade and signal updates will be printed and pushed via Telegram.

---

## Project Structure

- `main.py` — Entry point for live trading system
- `HyperFetch.py` — OHLC data generator and fetcher
- `TradingSignalGenerator.py` — Computes signals and generates alerts
- `Coin_fetcher.py` — Filters coins by leverage
- `error_log.txt` — Captures runtime errors from main process
- `test_data/` — Example CSV files for validation

---

## Known Limitations

- Signal generator reprocesses full dataset every run. Optimization planned.
- `process_csv_files()` overwrites existing signal files.
- Position logger occasionally desynchronizes; alerts may fail without affecting core data fetch. I disabled and stopped working on it, this is one of the reasons why. If using second bot token must modify positions.py.
- Multiple Telegram bots require separate tokens in `.env`.
- The use of `pandas-ta` limits performance and flexibility since it applies operations across the entire DataFrame. Consider replacing with a custom TA implementation for greater control and efficiency.

---

## Notes

- Timestamp is in **UTC**, per HyperLiquid's format.
- You may experience compatibility issues with `pandas-ta`. A future release may include manually implemented indicators.
- The code is littered with commented code. These are past attempts to fix problems and you may take these as suggestions :)

---

## Feedback

Issues and suggestions welcome via GitHub Issues or direct message on LinkedIn.
