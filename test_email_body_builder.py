import unittest
from unittest.mock import MagicMock
from email_body_builder import EmailBodyBuilder
from datetime import datetime

class TestEmailBodyBuilder(unittest.TestCase):

    def setUp(self):
        # Mock the OpenAI client and Labeler
        mock_openai_client = MagicMock()
        self.builder = EmailBodyBuilder(mock_openai_client)
        self.builder.labeler.get_labels = MagicMock(return_value="Label 1, Label 2, Label 3")

    def test_get_email_body_with_valid_content(self):
        # Simulate a valid HTML content with the expected structure
        website_content = """
        <html>
            <body>
                <div class="product__info">
                    <div class="main-product">
                        <h3 class="product-info__title">Free eBook - Sample Title</h3>
                        <span class="product-info__author">By Sample Author            
                        ,                 Author 2</span>
                        <div class="free_learning__product_pages_date">Published: 2023</div>
                        <div class="free_learning__product_description">Sample Description Line 1
                        Sample Description Line 2</div>
                    </div>
                </div>
            </body>
        </html>
        """
        today_date = datetime.now().strftime("%d.%m.%Y")
        expected_snippet = "<div class=\"main-product\">\n<h3 class=\"product-info__title\">Free eBook - Sample Title</h3>\n<span class=\"product-info__author\">By Sample Author            \n                        ,                 Author 2</span>\n<div class=\"free_learning__product_pages_date\">Published: 2023</div>\n<div class=\"free_learning__product_description\">Sample Description Line 1\n                        Sample Description Line 2</div>\n</div>"
        expected_table_row = f"""
              <tr>
                <td>Sample Title</td>
                <td>Sample Author, Author 2</td>
                <td>2023</td>
                <td>Sample Description Line 1 Sample Description Line 2</td>
                <td>Label 1, Label 2, Label 3</td>
                <td>Packt</td>
                <td>EPUB, PDF, MOBI</td>
                <td>{today_date}</td>
                <td>Packt Giveaway</td>
                <td>0</td>
              </tr>
        """
        email_body = self.builder.get_email_body(website_content)
        self.assertIn(expected_snippet, email_body)
        self.assertIn(expected_table_row.strip(), email_body)

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
        expected_message = "<p>Unfortunately, no matching snippet found.</p>"
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
        expected_message = "<p>Unfortunately, no matching snippet found.</p>"
        email_body = self.builder.get_email_body(website_content)
        self.assertIn(expected_message, email_body)

    def test_full_website(self):
        # Load the complete website content from test_website_data.html
        with open('test_website_data.html', 'r', encoding='utf-8') as file:
            website_content = file.read()

        # Get today's date in the format 'dd.mm.yyyy'
        today_date = datetime.now().strftime("%d.%m.%Y")

        # Expected table row pattern with regex for flexible whitespace
        expected_table_row_pattern = (
            r"<tr>\s*"
            r"<td>Mastering Scientific Computing with R</td>\s*"
            r"<td>Paul Gerrard</td>\s*"
            r"<td>2015</td>\s*"
            r"<td>How to master Scientific Computing with R</td>\s*"
            r"<td>Label 1, Label 2, Label 3</td>\s*"
            r"<td>Packt</td>\s*"
            r"<td>EPUB, PDF, MOBI</td>\s*"
            r"<td>{}</td>\s*"
            r"<td>Packt Giveaway</td>\s*"
            r"<td>0</td>\s*"
            r"</tr>"
        ).format(today_date)

        email_body = self.builder.get_email_body(website_content)
        self.assertRegex(email_body, expected_table_row_pattern)

        self.assertIn("https://www.packtpub.com/images/star--100-white.svg", email_body)

    def test_get_email_body_with_openai_exception(self):
        # Simulate a valid HTML content with the expected structure
        website_content = """
        <html>
            <body>
                <div class="product__info">
                    <div class="main-product">
                        <h3 class="product-info__title">Free eBook - Sample Title</h3>
                        <span class="product-info__author">By Sample Author</span>
                        <div class="free_learning__product_pages_date">Published: 2023</div>
                        <div class="free_learning__product_description">Sample Description</div>
                    </div>
                </div>
            </body>
        </html>
        """
        today_date = datetime.now().strftime("%d.%m.%Y")
        expected_snippet = "<div class=\"main-product\">\n<h3 class=\"product-info__title\">Free eBook - Sample Title</h3>\n<span class=\"product-info__author\">By Sample Author</span>\n<div class=\"free_learning__product_pages_date\">Published: 2023</div>\n<div class=\"free_learning__product_description\">Sample Description</div>\n</div>"
        expected_table_row = f"""
              <tr>
                <td>Sample Title</td>
                <td>Sample Author</td>
                <td>2023</td>
                <td>Sample Description</td>
                <td></td>
                <td>Packt</td>
                <td>EPUB, PDF, MOBI</td>
                <td>{today_date}</td>
                <td>Packt Giveaway</td>
                <td>0</td>
              </tr>
        """

        # Mock the labeler to raise an exception
        self.builder.labeler.get_labels.side_effect = Exception("OpenAI client error")

        email_body = self.builder.get_email_body(website_content)
        self.assertIn(expected_snippet, email_body)
        self.assertIn(expected_table_row.strip(), email_body)

if __name__ == "__main__":
    unittest.main()