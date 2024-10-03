from faker import Faker
import requests
import json
import os
import random
import apprise
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Initialize Faker
fake = Faker('en_IN')
fake_en = Faker('en_US')  # Additional Faker instance for English text

# Generate random user info
def generate_user_info():
    first_name = fake.first_name()
    last_name = fake.last_name()
    outlook_email = generate_available_outlook_email(first_name, last_name)
    additional_emails = generate_additional_outlook_emails(outlook_email)
    user_info = {
        "name": f"{first_name} {last_name}",
        "username": generate_available_username(),
        "bio": fake_en.text(max_nb_chars=100),  # Generate bio in English
        "location": fake.city(),
        "company": fake.company(),
        "website": fake.url(),
        "image_url": f"https://picsum.photos/400/400?random={random.randint(1, 10000)}",
        "outlook_email": outlook_email,
        "additional_emails": additional_emails
    }
    return user_info

# Validate user info
def validate_user_info(user_info):
    required_fields = ["name", "username", "bio", "location", "company", "website", "image_url", "outlook_email", "additional_emails"]
    for field in required_fields:
        if not user_info.get(field):
            return False
    return True

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

# Generate an available Outlook email without dots
def generate_available_outlook_email(first_name, last_name):
    base_email = f"{first_name.lower()}{last_name.lower()}@outlook.com"
    if is_outlook_email_available(base_email):
        return base_email
    # If no available email found, append two random digits
    while True:
        email = f"{first_name.lower()}{last_name.lower()}{random.randint(10, 99)}@outlook.com"
        if is_outlook_email_available(email):
            return email

# Generate additional Outlook emails with random names without dots
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

# Log user info to a uniquely named file
def log_user_info(user_info):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"user_info_{user_info['username']}_{timestamp}.txt"
    with open(file_name, "w") as file:
        file.write(json.dumps(user_info, indent=4))
    return file_name

# Send info to Discord using Apprise
def send_to_discord(webhook_url, user_info, include_image_info=True):
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

    if include_image_info:
        messages.extend([
            "**Image Name:**\n\n",
            "Random Image\n\n",
            "**Image Description:**\n\n",
            "This image is randomly generated from Picsum Photos.\n\n",
            "**Image URL:**\n\n",
            f"{user_info['image_url']}\n\n"
        ])
    else:
        messages.append(f"**Image URL:**\n\n{user_info['image_url']}\n\n")

    for message in messages:
        apobj.notify(
            body=message,
            title=""
        )

# Send email with user info using OAuth2 (Gmail)
def send_email_with_oauth2(user_info, recipient_email, attachment_path):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEMultipart()
    message['to'] = recipient_email
    message['subject'] = "Generated User Information"
    body = json.dumps(user_info, indent=4)
    message.attach(MIMEText(body, 'plain'))

    # Attach the file
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(attachment_path)}",
        )
        message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw}

    try:
        message = (service.users().messages().send(userId="me", body=message).execute())
        print(f"Message Id: {message['id']}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Send email with user info using Outlook
def send_email_with_outlook(user_info, recipient_email, attachment_path):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")  # Use the app password here

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Generated User Information"

    body = json.dumps(user_info, indent=4)
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(attachment_path)}",
        )
        msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    telegram_enabled = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    logging_enabled = os.getenv("LOGGING_ENABLED", "false").lower() == "true"
    email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    recipient_email = os.getenv("RECIPIENT_EMAIL")
    include_image_info = os.getenv("INCLUDE_IMAGE_INFO", "true").lower() == "true"
    email_service = os.getenv("EMAIL_SERVICE", "gmail").lower()  # Default to Gmail

    if webhook_url:
        user_info = generate_user_info()
        
        if validate_user_info(user_info):
            if logging_enabled:
                attachment_path = log_user_info(user_info)  # Log the user info and get the file path
            
            send_to_discord(webhook_url, user_info, include_image_info)
            
            if telegram_enabled and telegram_bot_token and telegram_chat_id:
                send_to_telegram(telegram_bot_token, telegram_chat_id, user_info)
            
            if email_enabled and recipient_email:
                if email_service == "gmail":
                    send_email_with_oauth2(user_info, recipient_email, attachment_path)
                elif email_service == "outlook":
                    send_email_with_outlook(user_info, recipient_email, attachment_path)
                else:
                    print(f"Unsupported email service: {email_service}")
        else:
            print("User info validation failed. Some fields are missing.")
    else:
        print("Discord webhook URL not found in environment variables.")
