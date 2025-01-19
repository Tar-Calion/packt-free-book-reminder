import os
import unittest
from unittest.mock import patch, MagicMock, Mock
import smtplib

# Wir gehen davon aus, dass dein Script "main_script.py" heißt und folgende Funktionen enthält:
#  - fetch_website_content
#  - send_email_via_gmail
#  - main
#
# Und dass "EmailBodyExtractor" in einer separaten Datei "email_body_extractor.py" steckt,
# die wir hier NICHT mocken, sondern real verwenden (so wie gewünscht).

from run_reminder import fetch_website_content, send_email_via_gmail, main

class TestRunReminder(unittest.TestCase):

    def setUp(self):
        """ SetUp wird vor jedem Test aufgerufen. Hier kannst du Umgebungsvariablen mocken. """
        os.environ["GMAIL_USERNAME"] = "testuser@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpassword"
        os.environ["RECIPIENT_EMAIL"] = "recipient@example.com"

    @patch("requests.get")
    def test_fetch_website_content_success(self, mock_get):
        """Testet, ob fetch_website_content korrekt funktioniert, wenn der Request erfolgreich ist."""
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test Content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        url = "https://www.example.com"
        content = fetch_website_content(url)

        # Prüfen, ob requests.get mit der korrekten URL aufgerufen wurde
        mock_get.assert_called_once_with(url)

        # Prüfen, ob die Funktion den HTML-Text zurückgibt
        self.assertEqual(content, "<html><body>Test Content</body></html>")

    @patch("requests.get")
    def test_fetch_website_content_exception(self, mock_get):
        """Testet, ob fetch_website_content None zurückgibt, wenn eine Exception auftritt."""
        mock_get.side_effect = Exception("Test Exception")

        content = fetch_website_content("https://www.example.com")

        # Da eine Exception aufgetreten ist, sollte None zurückgegeben werden.
        self.assertIsNone(content)

    @patch("smtplib.SMTP_SSL")
    def test_send_email_via_gmail(self, mock_smtp_ssl):
        """
        Testet, ob eine E-Mail über Gmail korrekt vorbereitet und "verschickt" wird.
        Wir patchen SMTP_SSL, damit kein echter Versand passiert.
        """
        send_email_via_gmail(subject="Test Subject", html_body="<p>Test Body</p>")

        # mock_smtp_ssl wird aufgerufen mit Host "smtp.gmail.com" und Port 465
        mock_smtp_ssl.assert_called_once_with("smtp.gmail.com", 465, context=unittest.mock.ANY)

        # Den "Server" aus dem Context Manager fischen
        mock_server = mock_smtp_ssl.return_value.__enter__.return_value

        # Prüfen, ob server.login aufgerufen wurde mit den erwarteten Credentials
        mock_server.login.assert_called_once_with("testuser@gmail.com", "testpassword")

        # Prüfen, ob server.sendmail aufgerufen wurde
        mock_server.sendmail.assert_called_once()
        args, kwargs = mock_server.sendmail.call_args

        # sendmail bekommt üblicherweise (from_addr, to_addrs, msg), wir können sie hier prüfen
        self.assertEqual(args[0], "testuser@gmail.com")        # from
        self.assertEqual(args[1], "recipient@example.com")     # to
        self.assertIn("Test Subject", args[2])                 # Betreff sollte in msg stecken
        self.assertIn("Test Body", args[2])                    # Body sollte in msg stecken

    @patch("run_reminder.send_email_via_gmail")
    @patch("requests.get")
    def test_main_integration(self, mock_requests_get, mock_send_email):
        """
        Integrationstest für die main-Funktion, bei dem requests gemockt wird,
        um das HTML aus einer Datei einzuspielen, und send_email_via_gmail gemockt wird,
        um den finalen HTML-Inhalt zu prüfen.
        """
        # Lade das HTML aus einer lokalen Datei test_data.html
        with open("test_website_data.html", "r", encoding="utf-8") as f:
            test_html_content = f.read()

        mock_response = MagicMock()
        mock_response.text = test_html_content
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # main aufrufen
        main()

        # Prüfen, ob send_email_via_gmail aufgerufen wurde
        mock_send_email.assert_called_once()
        # Die Argumente aus dem Funktionsaufruf abholen
        args, kwargs = mock_send_email.call_args

        # send_email_via_gmail(subject=..., html_body=...)
        subject = kwargs.get("subject", "")  # oder args[0] wenn positional
        html_body = kwargs.get("html_body", "")  # oder args[1] wenn positional

        # Subjekt prüfen
        self.assertIn("Tägliches PacktPub Free Learning Buch", subject)

        # Prüfen, ob die gewünschten Strings im generierten HTML stecken
        self.assertIn('<div class="grid product-info main-product">', html_body)
        self.assertIn('<h3 class="product-info__title">Free eBook - Mastering Scientific Computing with R</h3>', html_body)

        print(html_body)
        # Optional: Du kannst auch prüfen, dass der komplette HTML-Aufbau korrekt ist,
        # indem du noch andere Tags/Strukturen prüfst.


if __name__ == "__main__":
    unittest.main()
