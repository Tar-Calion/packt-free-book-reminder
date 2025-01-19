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

def send_email_via_gmail(subject, body, recipient):
    gmail_user = os.environ["GMAIL_USERNAME"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient, msg.as_string())

def main():
    url = "https://www.packtpub.com/free-learning"
    content = fetch_website_content(url)
    if content:
        # Im einfachsten Fall einfach den kompletten HTML-Inhalt verschicken
        email_body = f"Hier ist der aktuelle Free-Learning-Buch-Link:\n\n{content}"

        # Empfängeradresse aus Environment
        recipient = os.environ["RECIPIENT_EMAIL"]

        send_email_via_gmail(
            subject="Tägliches PacktPub Free Learning Buch",
            body=email_body,
            recipient=recipient
        )
    else:
        print("Konnte den Seiteninhalt nicht abrufen.")

if __name__ == "__main__":
    main()
