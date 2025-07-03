from flask import Flask, request
import alpaca_trade_api as tradeapi
import os
import math

# Load credentials from environment variables
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = "https://paper-api.alpaca.markets"  # Change to live URL for live trading

# Trading settings
SYMBOL = "AAPL"             # Set your stock symbol here
SPEND_PER_TRADE = 100       # How much USD to spend per trade

# Initialize Flask app and Alpaca API
app = Flask(__name__)
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version="v2")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    action = data.get("action")

    if not action:
        return {"status": "Missing action in webhook"}

    try:
        # Get latest trade price
        latest_trade = api.get_latest_trade(SYMBOL)
        price = latest_trade.price
        qty = math.floor(SPEND_PER_TRADE / price)

        if qty < 1:
            return {"status": "Not enough to buy even one share."}

        # Submit the order
        if action == "BUY":
            api.submit_order(
                symbol=SYMBOL,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="gtc",
                extended_hours=True
            )
            return {"status": f"BUY {qty} shares of {SYMBOL} at ~${price}"}

        elif action == "SELL":
            api.submit_order(
                symbol=SYMBOL,
                qty=qty,
                side="sell",
                type="market",
                time_in_force="gtc",
                extended_hours=True
            )
            return {"status": f"SELL {qty} shares of {SYMBOL} at ~${price}"}

        else:
            return {"status": "Invalid action"}

    except Exception as e:
        return {"status": f"Error: {str(e)}"}

@app.route("/")
def home():
    return "✅ Alpaca Bot is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
