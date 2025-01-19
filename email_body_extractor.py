from bs4 import BeautifulSoup

class EmailBodyExtractor:
    def get_email_body(self, website_content):
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