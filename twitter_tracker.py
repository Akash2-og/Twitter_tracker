import requests
import time
import os

# Load environment variables for security
TWITTER_BEARER_TOKEN = os.getenv("AAAAAAAAAAAAAAAAAAAAADXn0AEAAAAARNEdqjtophCXMf0oHPUsac8e1HQ%3Dg15V4Appps6D9cjbGyw4utu9TS9cfwRgMe0lWBCmXnbKz7VtVx")
DISCORD_WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1354951442850382108/t92OOdADNthSiXAShIdi-o6y4EaZqgj4dTf9OBhIiW3mDb4MVcfmjuApndovf8-tF4Cn")

# Target usernames to track
TARGET_USERNAMES = ["Kawshik56", "elonmusk"]

# Store last seen tweets to avoid duplicates
LAST_TWEET_IDS = {}

# Function to get user ID from username
def get_user_id(username):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["data"]["id"]
    elif response.status_code == 429:
        handle_rate_limit(response)
    else:
        print(f"Failed to fetch user ID for {username}: {response.status_code}, {response.text}")
        return None

# Function to get latest tweets for a user ID
def get_latest_tweets(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        handle_rate_limit(response)
    else:
        print(f"Failed to fetch tweets for {user_id}: {response.status_code}, {response.text}")
        return None

# Function to handle rate limits dynamically
def handle_rate_limit(response):
    print("Rate limit reached. Checking headers for wait time...")
    reset_time = int(response.headers.get("x-rate-limit-reset", time.time()))  # Get reset time
    sleep_time = max(reset_time - int(time.time()), 60)  # Wait until reset (default 60s if unknown)
    print(f"Sleeping for {sleep_time} seconds to avoid being blocked...")
    time.sleep(sleep_time)

# Function to send a message to Discord
def send_to_discord(message):
    payload = {"content": message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

    if response.status_code == 204:
        print("Successfully sent message to Discord.")
    else:
        print(f"Failed to send message to Discord: {response.status_code}, {response.text}")

# Function to track tweets from multiple accounts
def track_tweets():
    for username in TARGET_USERNAMES:
        user_id = get_user_id(username)
        if not user_id:
            continue

        tweet_data = get_latest_tweets(user_id)
        if tweet_data and "data" in tweet_data:
            for tweet in tweet_data["data"]:
                tweet_id = tweet["id"]
                tweet_text = tweet["text"]

                # Avoid duplicate notifications
                if LAST_TWEET_IDS.get(username) == tweet_id:
                    continue  

                # Save latest tweet ID
                LAST_TWEET_IDS[username] = tweet_id

                message = f"🟢 New tweet from {username}: {tweet_text}\n🔗 Link: https://twitter.com/{username}/status/{tweet_id}"
                send_to_discord(message)

# Main loop to track tweets every 5 minutes
if __name__ == "__main__":
    while True:
        track_tweets()
        print("✅ Waiting 5 minutes before checking again...")
        time.sleep(300)  # Wait for 5 minutes
