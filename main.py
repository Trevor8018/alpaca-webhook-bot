from flask import Flask, request
import alpaca_trade_api as tradeapi
import os

app = Flask(__name__)

# Load API keys from environment variables
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = 'https://paper-api.alpaca.markets'

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action = data.get("action")
    symbol = data.get("symbol", "AAPL")  # Default to AAPL if not specified

    try:
        account = api.get_account()
        buying_power = float(account.buying_power)

        # Set max percent of buying power to use (example: 10%)
        percent_to_use = 0.1
        amount_to_invest = buying_power * percent_to_use

        latest_price = float(api.get_last_trade(symbol).price)
        qty = int(amount_to_invest / latest_price)

        if qty < 1:
            return {"status": f"Not enough buying power to purchase {symbol}."}

        if action == "BUY":
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side="buy",
                type="market",
                time_in_force="gtc",
                extended_hours=True  # Enable pre/post-market
            )
            return {"status": f"BUY {qty} shares of {symbol} placed."}

        elif action == "SELL":
            api.submit_order(
                symbol=symbol,
                qty=qty,
                side="sell",
                type="market",
                time_in_force="gtc",
                extended_hours=True
            )
            return {"status": f"SELL {qty} shares of {symbol} placed."}

        return {"status": "Unknown action."}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/balance')
def balance():
    try:
        account = api.get_account()
        return {
            "cash": account.cash,
            "buying_power": account.buying_power,
            "portfolio_value": account.portfolio_value
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def home():
    return "Alpaca Bot is Running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
