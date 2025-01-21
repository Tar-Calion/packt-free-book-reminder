from bs4 import BeautifulSoup
from datetime import datetime
from labeler import Labeler

class EmailBodyBuilder:
    def __init__(self, openai_client):
        self.labeler = Labeler(openai_client)

    def get_email_body(self, website_content):
        """
        Sucht in 'website_content' nach einem parent div mit class='product__info'
        und darin nach dem Child div mit class='main-product'.
        Gibt diesen Ausschnitt als HTML-String zurück.
        """
        soup = BeautifulSoup(website_content, "html.parser")

        snippet = ""
        title = author = publication_year = description = "Nicht verfügbar"
        
        parent_div = soup.find("div", class_="product__info")
        if parent_div:
            main_product_div = parent_div.find("div", class_="main-product")
            if main_product_div:
                snippet = str(main_product_div)  # HTML-String des div

                # Extract additional information
                title_tag = main_product_div.find("h3", class_="product-info__title")
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    title = title.removeprefix("Free eBook - ")

                author_tag = main_product_div.find("span", class_="product-info__author")
                if author_tag:
                    author = author_tag.get_text(strip=True)
                    author = author.removeprefix("By").strip()

                publication_date_tag = main_product_div.find("div", class_="free_learning__product_pages_date")
                if publication_date_tag:
                    publication_year = publication_date_tag.get_text(strip=True).split()[-1]  # Extract year

                description_tag = main_product_div.find("div", class_="free_learning__product_description")
                if description_tag:
                    description = description_tag.get_text(strip=True)

        # Falls snippet leer ist, geben wir einen kleinen Hinweis
        if not snippet:
            snippet = "<p>Leider kein passender Ausschnitt gefunden.</p>"

        # Get today's date in the format 'dd.mm.yyyy'
        today_date = datetime.now().strftime("%d.%m.%Y")

        # Get labels using the Labeler
        labels = self.labeler.get_labels(title, author, description)
        
        details_line = f"{title}\t{author}\t{publication_year}\t{description}\t{labels}\tPackt\tEPUB, PDF, MOBI\t{today_date}\tPackt Giveaway\t0" 

        email_html = f"""
        <html>
          <head>
            <style>
              table {{
                border-collapse: collapse;
                width: 100%;
              }}
              th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
              }}
              th {{
                background-color: #f2f2f2;
              }}
              tr:nth-child(even) {{
                background-color: #f9f9f9;
              }}
              tr:hover {{
                background-color: #ddd;
              }}
            </style>
          </head>
          <body>
            <h2><a href="https://www.packtpub.com/free-learning">Heute bei PacktPub Free Learning:</a></h2>
            {snippet}
            <table>
              <tr>
                <th>Title</th>
                <th>Author</th>
                <th>Publication Year</th>
                <th>Description</th>
                <th>Labels</th>
                <th>Publisher</th>
                <th>Formats</th>
                <th>Date</th>
                <th>Source</th>
                <th>Price</th>
              </tr>
              <tr>
                <td>{title}</td>
                <td>{author}</td>
                <td>{publication_year}</td>
                <td>{description}</td>
                <td>{labels}</td>
                <td>Packt</td>
                <td>EPUB, PDF, MOBI</td>
                <td>{today_date}</td>
                <td>Packt Giveaway</td>
                <td>0</td>
              </tr>
            </table>

            <p/>
            <textarea rows="5" cols="150">{details_line}</textarea>

          </body>
        </html>
        """
        return email_html 