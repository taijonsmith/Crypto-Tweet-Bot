import tweepy
import logging
import time
import json
import os
from multiprocessing import Process
from requests import Request, Session
from config import create_twitter_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
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
twitter_api = create_twitter_api()

def get_coin_data():
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    bitcoin = data['data']['BTC'][0]
    ethereum = data['data']['ETH'][0]
    return [bitcoin, ethereum]

def get_hourly_crypto_price():
    while True:
        try:
            logger.info("Checking Hourly Crypto Price...")
            coins = get_coin_data()
            for coin in coins:
                price_direction = 'up ' if coin['quote']['USD']['percent_change_1h'] > 0 else 'down '
                summary = coin['name'] + ' (' + coin['symbol'] + ')' + ' is ' + price_direction + '{:.2f}%'.format(abs(coin['quote']['USD']['percent_change_1h'])) + ' in the last hour'
                logger.info(summary)
                twitter_api.update_status(summary)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            logger.error("Error while getting hourly crypto price")
            raise e
        time.sleep(60 * 60)

def get_daily_crypto_price():
    while True:
        try:
            logger.info("Checking Daily Crypto Price...")
            coins = get_coin_data()
            for coin in coins:
                price_direction = 'up ' if coin['quote']['USD']['percent_change_24h'] > 0 else 'down '
                summary = coin['name'] + ' (' + coin['symbol'] + ')' + ' is ' + price_direction + '{:.2f}%'.format(abs(coin['quote']['USD']['percent_change_24h'])) + ' in the last day'
                logger.info(summary)
                twitter_api.update_status(summary)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            logger.error("Error while getting daily crypto price")
            raise e
        time.sleep(24 * 60 * 60)

def main():
    t1 = Process(target = get_hourly_crypto_price)
    t2 = Process(target = get_daily_crypto_price)
    t1.start()
    t2.start()
    

if __name__ == "__main__":
    main()