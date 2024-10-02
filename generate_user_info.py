from faker import Faker
import requests
import json
import os
import random

# Initialize Faker
fake = Faker('en_IN')

# Generate random user info
def generate_user_info():
    user_info = {
        "name": fake.name(),
        "username": generate_available_username(),
        "bio": fake.sentence(nb_words=10),
        "location": fake.city(),
        "company": fake.company(),
        "website": fake.url(),
        "image_url": f"https://picsum.photos/400/400?random={random.randint(1, 10000)}"
    }
    return user_info

# Check if GitHub username is available
def is_github_username_available(username):
    response = requests.get(f"https://api.github.com/users/{username}")
    return response.status_code == 404

# Generate an available GitHub username
def generate_available_username():
    for _ in range(10):
        username = fake.user_name()
        if is_github_username_available(username):
            return username
    # If no available username found, append two random digits
    while True:
        username = f"{fake.user_name()}{random.randint(10, 99)}"
        if is_github_username_available(username):
            return username

# Send info to Discord
def send_to_discord(webhook_url, user_info):
    messages = [
        f"**Name:**\n`{user_info['name']}`",
        f"**Username:**\n`{user_info['username']}`",
        f"**Bio:**\n`{user_info['bio']}`",
        f"**Location:**\n`{user_info['location']}`",
        f"**Company:**\n`{user_info['company']}`",
        f"**Website:**\n`{user_info['website']}`"
    ]
    
    for message in messages:
        data = {
            "content": message
        }
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            print(f"Failed to send to Discord: {response.status_code}")
    
    # Send the image as an embed
    embed_data = {
        "embeds": [
            {
                "title": user_info["name"],
                "description": user_info["bio"],
                "image": {
                    "url": user_info["image_url"]
                }
            }
        ]
    }
    response = requests.post(webhook_url, json=embed_data)
    if response.status_code == 204:
        print("Successfully sent to Discord")
    else:
        print(f"Failed to send to Discord: {response.status_code}")

if __name__ == "__main__":
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if webhook_url:
        user_info = generate_user_info()
        send_to_discord(webhook_url, user_info)
    else:
        print("Discord webhook URL not found in environment variables.")
