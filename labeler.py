# This class can find labels from a book description. It uses the ChatGPT API in order to do it.
from openai import OpenAI
import os


class Labeler:

    def __init__(self, openai_client: OpenAI, simulate: bool = False):
        self.simulate = simulate
        self.openai_client = openai_client

    def get_labels(self, title, author, description) -> str:
        print("Getting labels for the book:\n" +
              f"Title: {title}\n" +
              f"Author: {author}\n" +
              f"Description: {description}")

        if self.simulate:
            print("Simulating the labeler...")
            return "Label 1, Label 2, Label 3"

        chat_completion = self.openai_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": ("Analyze the book data provided and suggest 1 to 3 labels or themes that best characterize the book. "
                                "Consider the title and the description to determine the overarching theme discussed in the book. "
                                "If the theme can be described in a specific and a generic term, provide only the specific term. "
                                "Valid responses may look like 'Java' or 'Algorithms, Data Structures'."
                                )
                },
                {
                    "role": "user",
                    "content": "Title: {}\nAuthor: {}\nDescription: {}""".format(title, author, description)
                }
            ],
            model=os.environ.get("OPENAI_MODEL"),
        )

        print("Used model: {}".format(chat_completion.model))

        response = chat_completion.choices[0].message.content

        print("Received response: {}".format(response))

        return response
