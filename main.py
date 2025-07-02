from flask import Flask, request
import alpaca_trade_api as tradeapi
import os

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")
BASE_URL = 'https://paper-api.alpaca.markets'

app = Flask(__name__)
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action = data.get("action")

    if action == "BUY":
        api.submit_order(symbol="AAPL", qty=1, side="buy", type="market", time_in_force="gtc")
        return {"status": "BUY placed"}
    elif action == "SELL":
        api.submit_order(symbol="AAPL", qty=1, side="sell", type="market", time_in_force="gtc")
        return {"status": "SELL placed"}

    return {"status": "Unknown action"}

@app.route('/')
def home():
    return "Alpaca Bot is Running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
