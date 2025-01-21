import os
import unittest
from unittest.mock import patch, MagicMock
import smtplib
from run_reminder import fetch_website_content, send_email_via_gmail, main



class TestRunReminder(unittest.TestCase):

    def setUp(self):
        """ SetUp is called before each test. Here you can mock environment variables. """
        os.environ["GMAIL_USERNAME"] = "testuser@gmail.com"
        os.environ["GMAIL_APP_PASSWORD"] = "testpassword"
        os.environ["RECIPIENT_EMAIL"] = "recipient@example.com"
        os.environ["OPENAI_API_KEY"] = "test_openai_api_key"

    @patch("requests.get")
    def test_fetch_website_content_success(self, mock_get):
        """Tests if fetch_website_content works correctly when the request is successful."""
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test Content</body></html>"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        url = "https://www.example.com"
        content = fetch_website_content(url)

        # Check if requests.get was called with the correct URL
        mock_get.assert_called_once_with(url)

        # Check if the function returns the HTML text
        self.assertEqual(content, "<html><body>Test Content</body></html>")

    @patch("requests.get")
    def test_fetch_website_content_exception(self, mock_get):
        """Tests if fetch_website_content raises an exception when an exception occurs."""
        mock_get.side_effect = Exception("Test Exception")

        with self.assertRaises(Exception) as context:
            fetch_website_content("https://www.example.com")

        # Check if the exception contains the expected message
        self.assertEqual(str(context.exception), "Test Exception")

    @patch("smtplib.SMTP_SSL")
    def test_send_email_via_gmail(self, mock_smtp_ssl):
        """
        Tests if an email is correctly prepared and "sent" via Gmail.
        We patch SMTP_SSL so that no real sending occurs.
        """
        send_email_via_gmail(subject="Test Subject", html_body="<p>Test Body</p>")

        # mock_smtp_ssl is called with host "smtp.gmail.com" and port 465
        mock_smtp_ssl.assert_called_once_with("smtp.gmail.com", 465, context=unittest.mock.ANY)

        # Fetch the "server" from the context manager
        mock_server = mock_smtp_ssl.return_value.__enter__.return_value

        # Check if server.login was called with the expected credentials
        mock_server.login.assert_called_once_with("testuser@gmail.com", "testpassword")

        # Check if server.sendmail was called
        mock_server.sendmail.assert_called_once()
        args, kwargs = mock_server.sendmail.call_args

        # sendmail usually gets (from_addr, to_addrs, msg), we can check them here
        self.assertEqual(args[0], "testuser@gmail.com")        # from
        self.assertEqual(args[1], "recipient@example.com")     # to
        self.assertIn("Test Subject", args[2])                 # Subject should be in msg
        self.assertIn("Test Body", args[2])                    # Body should be in msg

    @patch("run_reminder.OpenAI")  # Mock the OpenAI client
    @patch("run_reminder.send_email_via_gmail")
    @patch("requests.get")
    def test_main_integration(self, mock_requests_get, mock_send_email, mock_openai):
        """
        Integration test for the main function, where requests is mocked
        to load the HTML from a file, and send_email_via_gmail is mocked
        to check the final HTML content.
        """
        # Load the HTML from a local file test_data.html
        with open("test_website_data.html", "r", encoding="utf-8") as f:
            test_html_content = f.read()

        mock_response = MagicMock()
        mock_response.text = test_html_content
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # Mock the OpenAI client to avoid real API calls
        mock_openai_instance = MagicMock()
        mock_openai.return_value = mock_openai_instance

        # Call main
        main()

        # Check if send_email_via_gmail was called
        mock_send_email.assert_called_once()
        # Fetch the arguments from the function call
        args, kwargs = mock_send_email.call_args

        # send_email_via_gmail(subject=..., html_body=...)
        subject = kwargs.get("subject", "")  # or args[0] if positional
        html_body = kwargs.get("html_body", "")  # or args[1] if positional

        # Check subject
        self.assertIn("Daily PacktPub Free Learning Book Reminder", subject)

        # Check if the desired strings are in the generated HTML
        self.assertIn('<div class="grid product-info main-product">', html_body)
        self.assertIn('<h3 class="product-info__title">Free eBook - Mastering Scientific Computing with R</h3>', html_body)

        print(html_body)
        # Optional: You can also check that the complete HTML structure is correct
        # by checking other tags/structures.

if __name__ == "__main__":
    unittest.main()
