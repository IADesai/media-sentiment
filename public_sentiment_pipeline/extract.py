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


if __name__ == "__main__":  # pragma: no cover
    configuration = dotenv_values()
    reddit_json = get_subreddit_json(configuration)
