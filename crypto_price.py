import logging
import time
import json
import os
from multiprocessing import Process
from requests import Request, Session
from config import create_twitter_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

crypto_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
twitter_api = create_twitter_api()

def get_coin_data():
    try:
        parameters = {
            'symbol':'BTC,ETH',
            'convert':'USD'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': os.getenv('COIN_MARKET_CAP_API_KEY'),
        }
        session = Session()
        session.headers.update(headers)
        response = session.get(crypto_url, params=parameters)
        data = json.loads(response.text)
        bitcoin = data['data']['BTC'][0]
        ethereum = data['data']['ETH'][0]
        return [bitcoin, ethereum]
    except (ConnectionError, Timeout, TooManyRedirects) as e:
            logger.error("Error while getting crypto price")
            raise e

def get_hourly_crypto_price():
    while True:
        logger.info("Checking Hourly Crypto Price...")
        coins = get_coin_data()
        if coins:
            for coin in coins:
                price_direction = 'up ' if coin['quote']['USD']['percent_change_1h'] > 0 else 'down '
                summary = coin['name'] + ' (' + coin['symbol'] + ')' + ' is ' + price_direction + '{:.2f}%'.format(abs(coin['quote']['USD']['percent_change_1h'])) + ' in the last hour'
                logger.info(summary)
                twitter_api.update_status(summary)
        time.sleep(60 * 60)

def get_daily_crypto_price():
    while True:
        logger.info("Checking Daily Crypto Price...")
        coins = get_coin_data()
        if coins:
            for coin in coins:
                price_direction = 'up ' if coin['quote']['USD']['percent_change_24h'] > 0 else 'down '
                summary = coin['name'] + ' (' + coin['symbol'] + ')' + ' is ' + price_direction + '{:.2f}%'.format(abs(coin['quote']['USD']['percent_change_24h'])) + ' in the last day'
                logger.info(summary)
                twitter_api.update_status(summary)
        time.sleep(24 * 60 * 60)

def main():
    p1 = Process(target = get_hourly_crypto_price)
    p2 = Process(target = get_daily_crypto_price)
    p1.start()
    p2.start()
    

if __name__ == "__main__":
    main()