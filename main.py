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
    percent = float(data.get("percent", 10))  # default to 10%

    if not action or not symbol:
        return {"status": "Missing action or symbol"}

    try:
        account = api.get_account()
        cash_balance = float(account.cash)
        budget = (percent / 100) * cash_balance

        barset = api.get_latest_bar(symbol)
        price = barset.c

        qty = math.floor(budget / price)

        if qty < 1:
            return {"status": f"Not enough funds to buy 1 share of {symbol}"}

        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=action.lower(),
            type="market",
            time_in_force="gtc",
            extended_hours=True
        )

        return {"status": f"{action.upper()} order placed for {qty} share(s) of {symbol}"}

    except Exception as e:
        return {"status": f"Error: {str(e)}"}

@app.route('/')
def home():
    return "✅ Alpaca Auto-Trading Bot is Live!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
