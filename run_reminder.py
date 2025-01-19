import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from bs4 import BeautifulSoup
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

def get_email_body(website_content):
    """
    Sucht in 'website_content' nach einem parent div mit class='product__info'
    und darin nach dem Child div mit class='main-product'.
    Gibt diesen Ausschnitt als HTML-String zurück.
    """
    soup = BeautifulSoup(website_content, "html.parser")

    snippet = ""
    parent_div = soup.find("div", class_="product__info")
    if parent_div:
        main_product_div = parent_div.find("div", class_="main-product")
        if main_product_div:
            snippet = str(main_product_div)  # HTML-String des div

    # Falls snippet leer ist, geben wir einen kleinen Hinweis
    if not snippet:
        snippet = "<p>Leider kein passender Ausschnitt gefunden.</p>"

    email_html = f"""
    <html>
      <head></head>
      <body>
        <h2>Heute bei PacktPub Free Learning:</h2>
        {snippet}
      </body>
    </html>
    """
    return email_html

def send_email_via_gmail(subject, html_body):
    gmail_user = os.environ["GMAIL_USERNAME"]
    gmail_password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ["RECIPIENT_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipient, msg.as_string())

def main():
    url = "https://www.packtpub.com/free-learning"
    website_content = fetch_website_content(url)

    if website_content:
        email_body = get_email_body(website_content)
        send_email_via_gmail(
            subject="Tägliches PacktPub Free Learning Buch",
            html_body=email_body
        )
        print("Email wurde versendet.")
    else:
        print("Konnte den Seiteninhalt nicht abrufen.")

if __name__ == "__main__":
    main()
