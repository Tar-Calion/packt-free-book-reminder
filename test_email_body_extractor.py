import unittest
from email_body_extractor import EmailBodyExtractor

class TestEmailBodyExtractor(unittest.TestCase):

    def setUp(self):
        self.extractor = EmailBodyExtractor()

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
        email_body = self.extractor.get_email_body(website_content)
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
        email_body = self.extractor.get_email_body(website_content)
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
        email_body = self.extractor.get_email_body(website_content)
        self.assertIn(expected_message, email_body)

if __name__ == "__main__":
    unittest.main() 