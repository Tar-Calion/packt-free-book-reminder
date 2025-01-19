import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv

load_dotenv()

def fetch_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def send_email_via_gmail(subject, body):
    gmail_user = os.environ["GMAIL_USERNAME"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient, msg.as_string())

def get_email_body(website_content):
    email_body = f"Hier ist der aktuelle Free-Learning-Buch-Link:\n\n{website_content}"
    return email_body

def main():
    url = "https://www.packtpub.com/free-learning"
    website_content = fetch_website_content(url)

    if website_content:
        email_body = get_email_body(website_content)

        send_email_via_gmail(
            subject="Tägliches PacktPub Free Learning Buch",
            body=email_body
        )
        print("Email wurde versendet")
    else:
        print("Konnte den Seiteninhalt nicht abrufen.")

if __name__ == "__main__":
    main()
