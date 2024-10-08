from faker import Faker
import requests
import json
import os
import random
import apprise

# Initialize Faker
fake = Faker('en_IN')

# Generate random user info
def generate_user_info():
    first_name = fake.first_name()
    last_name = fake.last_name()
    outlook_email = generate_available_outlook_email(first_name, last_name)
    additional_emails = generate_additional_outlook_emails(outlook_email)
    user_info = {
        "name": f"{first_name} {last_name}",
        "username": generate_available_username(),
        "bio": fake.sentence(nb_words=10),
        "location": fake.city(),
        "company": fake.company(),
        "website": fake.url(),
        "image_url": f"https://picsum.photos/400/400?random={random.randint(1, 10000)}",
        "outlook_email": outlook_email,
        "additional_emails": additional_emails
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

# Check if Outlook email is available
def is_outlook_email_available(email):
    # This is a placeholder function. In reality, you would need to use an API or a service to check email availability.
    # For the purpose of this example, we'll assume all emails are available.
    return True

# Generate an available Outlook email
def generate_available_outlook_email(first_name, last_name):
    for _ in range(10):
        email = f"{first_name.lower()}{last_name.lower()}@outlook.com"
        if is_outlook_email_available(email):
            return email
    # If no available email found, append two random digits
    while True:
        email = f"{first_name.lower()}{last_name.lower()}{random.randint(10, 99)}@outlook.com"
        if is_outlook_email_available(email):
            return email

# Generate additional Outlook emails with random names
def generate_additional_outlook_emails(base_email):
    base_username = base_email.split('@')[0]
    additional_emails = []
    for _ in range(3):
        random_name = fake.first_name().lower()
        email = f"{base_username}+{random_name}@outlook.com"
        additional_emails.append({
            "email": email,
            "github_username": generate_available_username()
        })
    return additional_emails

# Log user info to a file
def log_user_info(user_info):
    with open("user_info_log.txt", "a") as file:
        file.write(json.dumps(user_info) + "\n")

# Send info to Discord using Apprise
def send_to_discord(webhook_url, user_info):
    apobj = apprise.Apprise()
    apobj.add(webhook_url)

    messages = [
        "**Name:**\n\n",
        f"{user_info['name']}\n\n",
        "**Username:**\n\n",
        f"{user_info['username']}\n\n",
        "**Bio:**\n\n",
        f"{user_info['bio']}\n\n",
        "**Location:**\n\n",
        f"{user_info['location']}\n\n",
        "**Company:**\n\n",
        f"{user_info['company']}\n\n",
        "**Website:**\n\n",
        f"{user_info['website']}\n\n",
        "**Outlook Email:**\n\n",
        f"{user_info['outlook_email']}\n\n",
        "**Additional Emails:**\n\n",
        "\n".join([f"{email['email']} (GitHub: {email['github_username']})" for email in user_info['additional_emails']])
    ]
    
    for message in messages:
        apobj.notify(
            body=message,
            title=""
        )
    
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
        log_user_info(user_info)  # Log the user info
        send_to_discord(webhook_url, user_info)
    else:
        print("Discord webhook URL not found in environment variables.")
