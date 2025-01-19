import requests

def fetch_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def main():
    url = "https://www.packtpub.com/free-learning"
    content = fetch_website_content(url)
    if content:
        print(content)

if __name__ == "__main__":
    main() 