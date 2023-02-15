from flask import Flask, render_template
import time
import json
import requests
from binance.client import Client as BinanceClient
from kucoin.client import Client as KuCoinClient

app = Flask(__name__)

# Initialize Binance and KuCoin clients with your API keys
binance_api_key = 'YOUR_BINANCE_API_KEY'
binance_api_secret = 'YOUR_BINANCE_API_SECRET'
binance_client = BinanceClient(binance_api_key, binance_api_secret)

kucoin_api_key = 'YOUR_KUCOIN_API_KEY'
kucoin_api_secret = 'YOUR_KUCOIN_API_SECRET'
kucoin_client = KuCoinClient(kucoin_api_key, kucoin_api_secret)

# Define the trading pairs to scan for arbitrage opportunities
binance_symbol = 'ETHUSDT'
kucoin_symbol = 'ETH-USDT'

# Define the minimum profit percentage you're interested in
min_profit_percent = 0.5

# Define the minimum volume you're interested in (in USD)
min_volume = 1000

# Define the trading fees on both exchanges
binance_taker_fee = 0.001
kucoin_taker_fee = 0.001

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/arbitrage")
def arbitrage():
    try:
        # Get the latest market prices and volume on both exchanges
        binance_price = float(binance_client.get_symbol_ticker(symbol=binance_symbol)['price'])
        binance_volume = float(binance_client.get_ticker(symbol=binance_symbol)['quoteVolume'])
        kucoin_price = float(kucoin_client.get_symbol_ticker(symbol=kucoin_symbol)['price'])
        kucoin_volume = float(kucoin_client.get_24hr_stats(symbol=kucoin_symbol)['volValue'])

        # Calculate the potential profit from buying on KuCoin and selling on Binance
        profit = (binance_price / (1 - binance_taker_fee)) - (kucoin_price / (1 + kucoin_taker_fee))
        profit_percent = profit / (kucoin_price / (1 + kucoin_taker_fee)) * 100

        # Check if the profit is above the minimum threshold and the volume is above the minimum threshold
        if profit_percent > min_profit_percent and kucoin_volume > min_volume:
            message = f"Potential arbitrage opportunity: Buy on KuCoin ({kucoin_symbol}) at {kucoin_price:.8f}, sell on Binance ({binance_symbol}) at {binance_price:.2f}."
            message += f"Potential profit: {profit:.2f} ({profit_percent:.2f}%)."
        else:
            message = f"No arbitrage opportunity found. (Profit: {profit:.2f} ({profit_percent:.2f}%), Volume: {kucoin_volume:.2f})"

    except Exception as e:
        message = f"Error occurred: {str(e)}"

    return render_template("arbitrage.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)
