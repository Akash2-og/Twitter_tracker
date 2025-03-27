import requests
import time

# Your Twitter API Bearer Token
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAADXn0AEAAAAARNEdqjtophCXMf0oHPUsac8e1HQ%3Dg15V4Appps6D9cjbGyw4utu9TS9cfwRgMe0lWBCmXnbKz7VtVx"

# Your Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1354951442850382108/t92OOdADNthSiXAShIdi-o6y4EaZqgj4dTf9OBhIiW3mDb4MVcfmjuApndovf8-tF4Cn"

# List of target usernames to track
TARGET_USERNAMES = ["Kawshik56", "elonmusk"]

# Function to get the latest tweets for each target user
def get_latest_tweet(username):
    url = f"https://api.twitter.com/2/tweets?ids={username}"  # Adjust URL if needed
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 429:
        print(f"Rate limit reached. Waiting before retrying...")
        reset_time = int(response.headers.get('x-rate-limit-reset'))  # Get reset time from headers
        sleep_time = reset_time - int(time.time())  # Calculate how long to sleep before retry
        if sleep_time > 0:
            time.sleep(sleep_time)  # Sleep until the rate limit is reset
        return None

    if response.status_code == 200:
        return response.json()  # Returns tweet data
    else:
        print(f"Failed to fetch tweets for {username}: {response.status_code}")
        return None

# Function to get replies to a tweet
def get_replies(tweet_id):
    url = f"https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{tweet_id}"  # Search replies based on conversation ID
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Returns reply data
    else:
        print(f"Failed to fetch replies for tweet {tweet_id}: {response.status_code}")
        return []

# Function to send a message to Discord
def send_to_discord(message):
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

    if response.status_code == 204:
        print("Successfully sent message to Discord.")
    else:
        print(f"Failed to send message to Discord: {response.status_code}")

# Function to track tweets from multiple accounts
def track_tweets():
    for username in TARGET_USERNAMES:
        tweet_data = get_latest_tweet(username)
        
        if tweet_data:
            # Get the text of the latest tweet (adjust according to your response data structure)
            tweet_text = tweet_data['data'][0]['text']
            tweet_id = tweet_data['data'][0]['id']  # Get tweet ID to track replies
            message = f"New tweet from {username}: {tweet_text}"
            send_to_discord(message)
            
            # Now fetch replies to this tweet
            replies = get_replies(tweet_id)
            for reply in replies.get('data', []):
                reply_text = reply['text']
                reply_user = reply['author_id']  # Adjust as needed to get the username
                reply_message = f"Reply from {reply_user}: {reply_text}"
                send_to_discord(reply_message)

# Main loop to track tweets continuously (run every 30 seconds)
if __name__ == "__main__":
    while True:
        track_tweets()
        time.sleep(30)  # Wait for 30 seconds before checking again
