import unittest
from unittest.mock import patch, MagicMock
from labeler import Labeler


class TestLabeler(unittest.TestCase):

    def setUp(self):
        self.title ="Test Title"
        self.author = "Test Author"
        self.description = "Test Description"
        self.labeler = Labeler(openai_client=None, simulate=False)

    def test_get_labels(self):
        with patch.object(self.labeler, 'openai_client', new_callable=MagicMock) as mock_openai_client:
            mock_openai_client.chat.completions.create.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content="Label 1, Label 2, Label 3"))])
            labels = self.labeler.get_labels(self.title, self.author, self.description)
            self.assertEqual(labels, "Label 1, Label 2, Label 3")

            # Assert that 'create' was called with the correct parameters
            expected_messages = [
                {
                    "role": "system",
                    "content": ("Analyze the book data provided and suggest 1 to 3 labels or themes that best characterize the book. "
                                "Consider the title and the description to determine the overarching theme discussed in the book. "
                                "If the theme can be described in a specific and a generic term, provide only the specific term. "
                                "Valid responses may look like 'Java' or 'Algorithms, Data Structures'.")
                },
                {
                    "role": "user",
                    "content": "Title: {}\nAuthor: {}\nDescription: {}".format(self.title, self.author, self.description)
                }
            ]
            mock_openai_client.chat.completions.create.assert_called_with(
                messages=expected_messages,
                model=unittest.mock.ANY
            )

    def test_get_labels_simulation(self):
        self.labeler.simulate = True
        labels = self.labeler.get_labels(self.title, self.author, self.description)
        self.assertEqual(labels, "Label 1, Label 2, Label 3")


if __name__ == '__main__':
    unittest.main()
