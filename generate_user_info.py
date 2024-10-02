from faker import Faker
import requests
import json

# Initialize Faker
fake = Faker('en_IN')

# Generate random user info
def generate_user_info():
    user_info = {
        "name": fake.name(),
        "username": fake.user_name(),
        "bio": fake.sentence(nb_words=10),
        "location": fake.city(),
        "company": fake.company(),
        "website": fake.url()
    }
    return user_info

# Send info to Discord
def send_to_discord(webhook_url, user_info):
    data = {
        "content": json.dumps(user_info, indent=4)
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code == 204:
        print("Successfully sent to Discord")
    else:
        print(f"Failed to send to Discord: {response.status_code}")

if __name__ == "__main__":
    webhook_url = "YOUR_DISCORD_WEBHOOK_URL"
    user_info = generate_user_info()
    send_to_discord(webhook_url, user_info)
