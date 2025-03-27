import tweepy
import requests
import time

# Twitter API credentials (replace with your own)
TWITTER_BEARER_TOKEN = "your_twitter_bearer_token"

# Discord Webhook URL (replace with your own)
DISCORD_WEBHOOK_URL = "your_discord_webhook_url"

# Target Twitter account (username)
TARGET_USERNAME = "target_account"

# Tweepy client
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

def get_user_id(username):
    """Fetch the user ID of the Twitter account."""
    user = client.get_user(username=username)
    return user.data.id if user.data else None

def send_discord_notification(content):
    """Send a notification to Discord."""
    payload = {"content": content}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)

def track_tweets(user_id, last_tweet_id):
    """Track new tweets and send Discord notifications."""
    tweets = client.get_users_tweets(user_id, since_id=last_tweet_id, tweet_fields=["created_at"])
    if tweets.data:
        for tweet in tweets.data:
            tweet_url = f"https://twitter.com/{TARGET_USERNAME}/status/{tweet.id}"
            send_discord_notification(f"New tweet by {TARGET_USERNAME}: {tweet_url}")
        return tweets.data[0].id
    return last_tweet_id

if __name__ == "__main__":
    user_id = get_user_id(TARGET_USERNAME)
    if not user_id:
        print("User not found!")
        exit()

    last_tweet_id = None
    
    while True:
        last_tweet_id = track_tweets(user_id, last_tweet_id)
        time.sleep(60)  # Check every minute
