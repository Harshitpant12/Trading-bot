# Simplified Binance Futures Testnet Trading Bot

A simple Python bot to place Market, Limit, and Stop orders on the **Binance Futures Testnet**.

---

## Requirements
- Python 3.8+
- Binance Testnet account: [https://testnet.binancefuture.com](https://testnet.binancefuture.com)

Install dependencies:
```bash
pip install -r requirements.txt
```
# Usage

1. Generate API Key & Secret from Binance Futures Testnet.
2. Put them inside bot.py (or export as environment variables).
3. Run:
```
python bot.py
```
#Features

-Place Market orders (BUY/SELL)
-Place Limit orders (BUY/SELL)
-Place Stop-Market orders (for stop-loss)
-Check account balance
-Logging of all API requests, responses, and errors in bot.log
