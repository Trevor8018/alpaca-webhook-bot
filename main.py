from flask import Flask, request
import alpaca_trade_api as tradeapi
import os
import math

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = 'https://paper-api.alpaca.markets'

app = Flask(__name__)
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action = data.get("action")
    symbol = data.get("symbol")
    percent = data.get("percent", 10)  # Default to 10% if not provided

    if not action or not symbol:
        return {"status": "Missing action or symbol"}

    # Get account balance
    account = api.get_account()
    cash_balance = float(account.cash)
    budget = (percent / 100) * cash_balance

    # Get current price
    bar = api.get_latest_bar(symbol)
    price = bar.c
    qty = math.floor(budget / price)

    if qty < 1:
        return {"status": f"Not enough funds to buy at least 1 share of {symbol}"}

    if action.upper() == "BUY":
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side="buy",
            type="market",
            time_in_force="gtc",
            extended_hours=True
        )
        return {"status": f"BUY order placed: {qty} shares of {symbol}"}

    elif action.upper() == "SELL":
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side="sell",
            type="market",
            time_in_force="gtc",
            extended_hours=True
        )
        return {"status": f"SELL order placed: {qty} shares of {symbol}"}

    return {"status": "Invalid action"}

@app.route('/')
def home():
    return "Alpaca Auto-Trading Bot is Running!"
