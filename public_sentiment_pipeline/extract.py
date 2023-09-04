"""Contains the functions required to extract the titles and comments for Reddit posts."""

import requests
from dotenv import dotenv_values

REDDIT_URL = "https://www.reddit.com/r/"


def get_subreddit_json(config: dict) -> dict:
    """Returns the JSON for a subreddit endpoint."""
    subreddit = config["REDDIT_TOPIC"]
    response = requests.get(f"{REDDIT_URL}{subreddit}.json")
    if response.status_code != 200:
        raise ConnectionError(
            f"Unexpected non-200 status code returned. Code: {response.status_code}")
    return response.json()


def create_pages_list(reddit_json: dict) -> list[dict]:
    """Creates a list containing the links for each page."""
    pages_list = []
    for page in reddit_json["data"]["data"]:
        try:
            page_dict = {}
            page_dict["title"] = page["title"]
            page_dict["subreddit_url"] = page["url"]
            page_dict["article_url"] = page["article_url"]
            pages_list.append(page_dict)
        except AttributeError:
            print("Missing attribute. Skipping entry.")
    return pages_list


if __name__ == "__main__":  # pragma: no cover
    configuration = dotenv_values()
    reddit_json = get_subreddit_json(configuration)
    list_of_json = create_pages_list(reddit_json)
    print(list_of_json)
