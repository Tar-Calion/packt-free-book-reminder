import unittest
from email_body_builder import EmailBodyBuilder
from datetime import datetime
import re

class TestEmailBodyBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = EmailBodyBuilder()

    def test_get_email_body_with_valid_content(self):
        # Simulate a valid HTML content with the expected structure
        website_content = """
        <html>
            <body>
                <div class="product__info">
                    <div class="main-product">
                        <p>Expected content</p>
                    </div>
                </div>
            </body>
        </html>
        """
        expected_snippet = "<div class=\"main-product\">\n<p>Expected content</p>\n</div>"
        email_body = self.builder.get_email_body(website_content)
        self.assertIn(expected_snippet, email_body)

    def test_get_email_body_with_no_main_product(self):
        # Simulate HTML content without the main-product div
        website_content = """
        <html>
            <body>
                <div class="product__info">
                    <div class="other-product">
                        <p>Other content</p>
                    </div>
                </div>
            </body>
        </html>
        """
        expected_message = "<p>Leider kein passender Ausschnitt gefunden.</p>"
        email_body = self.builder.get_email_body(website_content)
        self.assertIn(expected_message, email_body)

    def test_get_email_body_with_no_product_info(self):
        # Simulate HTML content without the product__info div
        website_content = """
        <html>
            <body>
                <div class="other-info">
                    <p>Other content</p>
                </div>
            </body>
        </html>
        """
        expected_message = "<p>Leider kein passender Ausschnitt gefunden.</p>"
        email_body = self.builder.get_email_body(website_content)
        self.assertIn(expected_message, email_body)

    def test_details_line_from_file(self):
        # Load the complete website content from test_website_data.html
        with open('test_website_data.html', 'r', encoding='utf-8') as file:
            website_content = file.read()

        # Get today's date in the format 'dd.mm.yyyy'
        today_date = datetime.now().strftime("%d.%m.%Y")

        # Expected details line pattern
        expected_details_line = (
            "Mastering Scientific Computing with R\t"
            "Paul Gerrard\t"
            "2015\t"
            "How to master Scientific Computing with R\t\t"
            "Packt\t"
            "EPUB, PDF, MOBI\t"
            f"{today_date}\t"
            "Packt Giveaway\t"
            "0"
        )

        email_body = self.builder.get_email_body(website_content)
        self.assertIn(expected_details_line, email_body)

if __name__ == "__main__":
    unittest.main() 