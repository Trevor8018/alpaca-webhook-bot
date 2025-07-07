from flask import Flask, request
import alpaca_trade_api as tradeapi
import os
import math

# Load API credentials from environment variables
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = 'https://paper-api.alpaca.markets'  # Use 'https://api.alpaca.markets' for live trading

# Initialize app and Alpaca API
app = Flask(__name__)
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action = data.get("action")
    symbol = data.get("symbol")
    percent = float(data.get("percent", 10))  # Default 10%

    print(f"📩 Webhook received: {data}")

    # Check for missing info
    if not action or not symbol:
        print("❌ Missing action or symbol")
        return {"status": "Missing action or symbol"}, 400

    try:
        # Get account balance
        account = api.get_account()
        cash_balance = float(account.cash)
        budget = (percent / 100) * cash_balance
        print(f"💰 Cash: ${cash_balance}, Budget for this trade: ${budget}")

        # Get latest price
        try:
            bar = api.get_latest_bar(symbol)
            price = bar.c
            print(f"📈 Latest price for {symbol}: ${price}")
        except Exception as e:
            print(f"❌ Failed to get latest price for {symbol}: {e}")
            return {"status": f"Failed to get latest price for {symbol}"}, 500

        # Calculate quantity
        qty = math.floor(budget / price)
        if qty < 1:
            print(f"⚠️ Not enough budget to buy 1 share of {symbol}")
            return {"status": f"Not enough budget to buy 1 share of {symbol}"}, 200

        # Submit order
        order = api.submit_order(
            symbol=symbol,
            qty=qty,
            side=action.lower(),
            type="market",
            time_in_force="gtc",
            extended_hours=True
        )

        print(f"✅ {action.upper()} order placed for {qty} share(s) of {symbol} at ~${price}")
        return {"status": f"{action.upper()} order placed for {qty} share(s) of {symbol}"}, 200

    except Exception as e:
        print(f"❌ Error placing order: {str(e)}")
        return {"status": f"Error placing order: {str(e)}"}, 500

@app.route('/')
def home():
    return "✅ Alpaca Auto-Trading Bot is Live!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
