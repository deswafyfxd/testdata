from faker import Faker
import requests
import json
import os
import random

# Initialize Faker
fake = Faker('en_IN')
fake_global = Faker()

# Generate random user info
def generate_user_info():
    user_info = {
        "name": fake.name(),
        "username": generate_available_username(),
        "bio": fake.sentence(nb_words=10),
        "location": fake.city(),
        "company": fake.company(),
        "website": generate_website(),
        "image_url": f"https://picsum.photos/400/400?random={random.randint(1, 10000)}"
    }
    return user_info

# Generate a website URL
def generate_website():
    website = fake.url()
    if not website:
        website = fake_global.url()
    return website

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
        "**Name:**\n\n",
        f"`{user_info['name']}`\n\n",
        "**Username:**\n\n",
        f"`{user_info['username']}`\n\n",
        "**Bio:**\n\n",
        f"`{user_info['bio']}`\n\n",
        "**Location:**\n\n",
        f"`{user_info['location']}`\n\n",
        "**Company:**\n\n",
        f"`{user_info['company']}`\n\n",
        "**Website:**\n\n",
        f"`{user_info['website']}`\n\n"
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
