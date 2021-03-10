import tweepy
import os
import logging


logger = logging.getLogger()

def create_twitter_api():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(os.getenv('TWITTER_BOT_CONSUMER_KEY'), os.getenv('TWITTER_BOT_CONSUMER_SECRET'))
    auth.set_access_token(os.getenv('TWITTER_BOT_ACCESS_KEY'), os.getenv('TWITTER_BOT_ACCESS_SECRET'))

    api = tweepy.API(auth, wait_on_rate_limit=True, 
            wait_on_rate_limit_notify=True)

    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error during authentication")
        raise e
    logger.info("Authentication OK")
    return api