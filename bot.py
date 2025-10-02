"""
bot.py - Simplified Binance Futures Testnet Trading Bot (starter)

Requirements:
    pip install python-binance

Usage:
    1) Put your TESTNET API_KEY and API_SECRET below (or set environment variables).
    2) Run: python bot.py
"""

import os
import time
import logging
from typing import Optional, Dict, Any

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

# ---------------------------
# CONFIG - Put your keys here
# ---------------------------
API_KEY = "ea29ece2f69ce47ff12db435f61c84fc7f3a62a272c55f5fdd64608486d96865"
API_SECRET = "111b0740ef6b880e695cc9e8c2918f04ac85fec385acf388beb20253049fd340"

# or you can set environment variables and uncomment:
# API_KEY = os.getenv("BINANCE_TEST_API_KEY")
# API_SECRET = os.getenv("BINANCE_TEST_API_SECRET")

# ---------------------------
# Logging setup
# ---------------------------
LOG_FILE = "bot.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BasicBot")


# ---------------------------
# BasicBot class
# ---------------------------
class BasicBot:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        if not api_key or not api_secret:
            raise ValueError("API key and secret must be provided.")
        # init client
        # Use python-binance Client and override FUTURES_URL for testnet
        self.client = Client(api_key, api_secret, testnet=testnet)
        # Ensure futures endpoint points to testnet base URL
        # (This attribute override is commonly used for python-binance with futures testnet)
        if testnet:
            # REST base for futures testnet
            self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"
        logger.info("Initialized Binance client (testnet=%s)", testnet)

    # ---- utility ----
    def _log_api_call(self, name: str, params: Dict[str, Any], resp: Any = None, err: Optional[Exception] = None):
        """Structured logging for requests/responses/errors"""
        logger.info("API CALL: %s | params: %s", name, params)
        if resp is not None:
            logger.info("API RESP: %s", resp)
        if err is not None:
            logger.error("API ERR: %s", repr(err))

    # ---- account / balance ----
    def get_futures_balance(self) -> Dict[str, Any]:
        """Returns futures account balance (list of assets with balance)."""
        try:
            params = {}
            resp = self.client.futures_account_balance()
            self._log_api_call("futures_account_balance", params, resp)
            return resp
        except (BinanceAPIException, BinanceRequestException) as e:
            self._log_api_call("futures_account_balance", {}, err=e)
            raise

    # ---- market data ----
    def get_symbol_price(self, symbol: str) -> float:
        """Get latest mark/price for a symbol (USDT pairs e.g., BTCUSDT)."""
        try:
            params = {"symbol": symbol}
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            self._log_api_call("futures_symbol_ticker", params, ticker)
            return float(ticker["price"])
        except Exception as e:
            self._log_api_call("futures_symbol_ticker", {"symbol": symbol}, err=e)
            raise

    # ---- orders ----
    def place_market_order(self, symbol: str, side: str, quantity: float, reduce_only: bool = False, recv_window: Optional[int] = None):
        """
        Place a market order on futures.
        side: 'BUY' or 'SELL'
        quantity: float (contract quantity / lots - be careful with symbol's lot size)
        """
        try:
            params = {
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": quantity,
                "reduceOnly": reduce_only
            }
            if recv_window:
                params["recvWindow"] = recv_window
            resp = self.client.futures_create_order(**params)
            self._log_api_call("futures_create_order(MARKET)", params, resp)
            return resp
        except Exception as e:
            self._log_api_call("futures_create_order(MARKET)", {"symbol": symbol, "side": side, "quantity": quantity}, err=e)
            raise

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float, timeInForce: str = "GTC"):
        """Place LIMIT order (Futures)."""
        try:
            params = {
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "timeInForce": timeInForce,
                "quantity": quantity,
                "price": price
            }
            resp = self.client.futures_create_order(**params)
            self._log_api_call("futures_create_order(LIMIT)", params, resp)
            return resp
        except Exception as e:
            self._log_api_call("futures_create_order(LIMIT)", params, err=e)
            raise

    def place_stop_market(self, symbol: str, side: str, quantity: float, stopPrice: float, closePosition: bool = False):
        """
        Place STOP_MARKET (used for stop-loss).
        closePosition True -> close the entire position (useful for stop-loss).
        """
        try:
            params = {
                "symbol": symbol,
                "side": side,
                "type": "STOP_MARKET",
                "stopPrice": stopPrice,
                "closePosition": str(closePosition).lower()
            }
            # If quantity is required (not closing full position), include it
            if not closePosition:
                params["quantity"] = quantity
            resp = self.client.futures_create_order(**params)
            self._log_api_call("futures_create_order(STOP_MARKET)", params, resp)
            return resp
        except Exception as e:
            self._log_api_call("futures_create_order(STOP_MARKET)", params, err=e)
            raise

    def place_take_profit_market(self, symbol: str, side: str, quantity: float, stopPrice: float, closePosition: bool = False):
        """
        Place TAKE_PROFIT_MARKET (used for take-profit).
        """
        try:
            params = {
                "symbol": symbol,
                "side": side,
                "type": "TAKE_PROFIT_MARKET",
                "stopPrice": stopPrice,
                "closePosition": str(closePosition).lower()
            }
            if not closePosition:
                params["quantity"] = quantity
            resp = self.client.futures_create_order(**params)
            self._log_api_call("futures_create_order(TAKE_PROFIT_MARKET)", params, resp)
            return resp
        except Exception as e:
            self._log_api_call("futures_create_order(TAKE_PROFIT_MARKET)", params, err=e)
            raise

    def get_order(self, symbol: str, orderId: Optional[int] = None, origClientOrderId: Optional[str] = None):
        """Query order status."""
        try:
            params = {"symbol": symbol}
            if orderId:
                params["orderId"] = orderId
            if origClientOrderId:
                params["origClientOrderId"] = origClientOrderId
            resp = self.client.futures_get_order(**params)
            self._log_api_call("futures_get_order", params, resp)
            return resp
        except Exception as e:
            self._log_api_call("futures_get_order", params, err=e)
            raise

    def cancel_order(self, symbol: str, orderId: Optional[int] = None, origClientOrderId: Optional[str] = None):
        """Cancel an active order."""
        try:
            params = {"symbol": symbol}
            if orderId:
                params["orderId"] = orderId
            if origClientOrderId:
                params["origClientOrderId"] = origClientOrderId
            resp = self.client.futures_cancel_order(**params)
            self._log_api_call("futures_cancel_order", params, resp)
            return resp
        except Exception as e:
            self._log_api_call("futures_cancel_order", params, err=e)
            raise


# ---------------------------
# Example usage (simple CLI)
# ---------------------------
def main():
    print("Starting BasicBot (Binance Futures Testnet starter)")
    # Use keys from the top of file or environment variables
    api_key = API_KEY
    api_secret = API_SECRET
    if not api_key or not api_secret:
        print("ERROR: Please set API_KEY and API_SECRET in the script or via environment variables.")
        return

    bot = BasicBot(api_key, api_secret, testnet=True)

    # Example: print balance
    try:
        balance = bot.get_futures_balance()
        print("Futures balance snapshot (first few entries):")
        for asset in balance[:5]:
            print(asset)
    except Exception as e:
        print("Could not fetch balance - check logs:", e)

    # Example interactive flow (simple)
    while True:
        print("\nOptions: [1] Place Market Order  [2] Place Limit Order  [3] Place Stop Loss  [4] Exit")
        choice = input("Choice: ").strip()
        if choice == "1":
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            side = input("Side (BUY/SELL): ").strip().upper()
            qty = float(input("Quantity (contracts): ").strip())
            try:
                resp = bot.place_market_order(symbol, side, qty)
                print("Order response:", resp)
            except Exception as e:
                print("Error placing market order:", e)
        elif choice == "2":
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            side = input("Side (BUY/SELL): ").strip().upper()
            qty = float(input("Quantity (contracts): ").strip())
            price = float(input("Price: ").strip())
            try:
                resp = bot.place_limit_order(symbol, side, qty, price)
                print("Order response:", resp)
            except Exception as e:
                print("Error placing limit order:", e)
        elif choice == "3":
            symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
            side = input("Side the stop order should act as (BUY/SELL): ").strip().upper()
            qty = float(input("Quantity (contracts): ").strip())
            stop = float(input("Stop price: ").strip())
            close_pos = input("Close position (true/false)?: ").strip().lower() == "true"
            try:
                resp = bot.place_stop_market(symbol, side, qty, stopPrice=stop, closePosition=close_pos)
                print("Stop order response:", resp)
            except Exception as e:
                print("Error placing stop order:", e)
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Unknown choice.")

if __name__ == "__main__":
    main()
