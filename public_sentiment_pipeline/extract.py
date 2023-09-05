"""Contains the functions required to extract the titles and comments for Reddit posts."""

import json
from datetime import datetime

import requests
from dotenv import dotenv_values
from boto3 import client
from pytz import timezone

REDDIT_URL = "https://www.reddit.com/r/"
SUBREDDIT_URL = "https://www.reddit.com/"
REDDIT_ACCESS_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"


def get_reddit_access_token(config: dict) -> dict:
    """Obtains the access token dictionary from Reddit using a POST request."""
    print("Fetching access token from Reddit.")
    client_auth = requests.auth.HTTPBasicAuth(
        config["REDDIT_CLIENT_SECRET"], config["REDDIT_SECRET_KEY"])
    key_data = {"grant_type": "password",
                "username": config["REDDIT_USERNAME"], "password": config["REDDIT_PASSWORD"]}
    key_headers = {"User-Agent": "Media-Sentiment/0.1 by Media-Project"}

    response = requests.post(REDDIT_ACCESS_TOKEN_URL,
                             auth=client_auth, data=key_data, headers=key_headers)

    if response.status_code != 200:
        raise ConnectionError(
            f"Unexpected non-200 status code returned. Code: {response.status_code}")
    print("Successfully obtained Reddit access token.")
    return response.json()


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


def create_json_filename(reddit_title: str) -> str:
    """Returns a JSON filename using a title."""
    reddit_title = reddit_title.replace(" ", "_")
    if len(reddit_title) > 30:
        reddit_title = reddit_title[:30]
    current_timestamp = datetime.strftime(datetime.now(
        tz=timezone("Europe/London")), "%Y_%m_%d-%H_%M")
    return f"{reddit_title}-{current_timestamp}.json"


def save_json_to_file(json_contents: dict, json_filename: str) -> None:
    """Writes the contents of a dictionary to a JSON file."""
    with open(json_filename, "w", encoding="utf-8") as f_obj:
        json.dump(json_contents, f_obj, sort_keys=True,
                  indent=4, separators=(",", ": "))


def upload_json_s3(config: dict, json_filename: str) -> None:
    """Uploads a JSON file to an S3 bucket."""
    s3_client = client("s3", aws_access_key_id=config["ACCESS_KEY_ID"],
                       aws_secret_access_key=config["SECRET_ACCESS_KEY"])
    s3_client.upload_file(
        json_filename, config["REDDIT_JSON_BUCKET_NAME"], json_filename)


def get_json_for_request(subreddit_url: str, json_filename: str):
    """Saves the contents of a GET request to a JSON file."""
    response = requests.get(subreddit_url)
    if response.status_code != 200:
        raise ConnectionError(
            f"Unexpected non-200 status code returned for the url: {subreddit_url}. Code: {response.status_code}")
    save_json_to_file(response.json(), json_filename)


if __name__ == "__main__":  # pragma: no cover
    configuration = dotenv_values()
    reddit_json = get_subreddit_json(configuration)
    list_of_json = create_pages_list(reddit_json)
    print(list_of_json)
