"""Contains the functions required to extract the titles and comments for Reddit posts."""

import json
from datetime import datetime
import re
import os

import requests
from dotenv import dotenv_values
from boto3 import client
from pytz import timezone

MAX_REDDIT_PAGES = 40
MAX_REDDIT_COMMENTS = 500

REDDIT_URL = "https://oauth.reddit.com/r/"
SUBREDDIT_URL = "https://oauth.reddit.com/"
REDDIT_ACCESS_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"

REDDIT_TITLE_KEY = "title"
REDDIT_SUBREDDIT_URL = "subreddit_url"
REDDIT_ARTICLE_URL = "article_url"
REDDIT_ARTICLE_DOMAIN = "article_domain"
REDDIT_ARTICLE_SCORE = "score"
REDDIT_UPVOTE_RATIO = "upvote_ratio"
REDDIT_POST_COMMENTS = "comment_count"
REDDIT_INCLUDED_COMMENTS = "included_comment_count"
REDDIT_CREATED_UTC = "creation_timestamp"
REDDIT_COMMENTS = "comments"


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
    return response.json()["access_token"]


def get_subreddit_json(config: dict, reddit_access_token: str) -> dict:
    """Returns the JSON for a subreddit endpoint."""
    subreddit = config["REDDIT_TOPIC"]
    print(f"Fetching data from the {subreddit} subreddit.")
    auth_headers = {"Authorization": f"bearer {reddit_access_token}",
                    "User-Agent": "Media-Sentiment/0.1 by Media-Project"}
    parameters = {"limit": MAX_REDDIT_PAGES}

    response = requests.get(f"{REDDIT_URL}{subreddit}/new",
                            headers=auth_headers, params=parameters)
    if response.status_code != 200:
        raise ConnectionError(
            f"Unexpected non-200 status code returned. Code: {response.status_code}")
    print("Successfully fetched subreddit data.")
    return response.json()


def create_pages_list(reddit_json: dict) -> list[dict]:
    """Creates a list containing the links for each page."""
    pages_list = []
    for page in reddit_json["data"]["children"]:
        try:
            page_dict = {}
            page_dict[REDDIT_TITLE_KEY] = page["data"]["title"]
            page_dict[REDDIT_SUBREDDIT_URL] = page["data"]["permalink"]
            page_dict[REDDIT_ARTICLE_URL] = page["data"]["url"]
            page_dict[REDDIT_ARTICLE_DOMAIN] = page["data"]["domain"]
            page_dict[REDDIT_ARTICLE_SCORE] = page["data"]["score"]
            page_dict[REDDIT_UPVOTE_RATIO] = page["data"]["upvote_ratio"]
            page_dict[REDDIT_POST_COMMENTS] = page["data"]["num_comments"]
            page_dict[REDDIT_CREATED_UTC] = datetime.strftime(
                datetime.fromtimestamp(page["data"]["created_utc"]), "%Y-%m-%d %H:%M:%S")
            pages_list.append(page_dict)
        except KeyError:
            print("Missing attribute. Skipping entry.")
    return pages_list


def create_json_filename(reddit_title: str) -> str:
    """Returns a JSON filename using a title."""
    forbidden_characters = (" ", "-", "\"", ".", ",")
    for character in forbidden_characters:
        reddit_title = reddit_title.replace(character, "_")
    if len(reddit_title) > 30:
        reddit_title = reddit_title[:30]
    current_timestamp = datetime.strftime(datetime.now(
        tz=timezone("Europe/London")), "%Y_%m_%d-%H_%M")
    return f"{current_timestamp}-{reddit_title}.json"


def save_json_to_file(json_contents: dict, json_filename: str) -> None:  # pragma: no cover
    """Writes the contents of a dictionary to a JSON file."""
    with open(json_filename, "w", encoding="utf-8") as f_obj:
        json.dump(json_contents, f_obj, sort_keys=True,
                  indent=4, separators=(",", ": "))


def upload_json_s3(config: dict, json_filename: str) -> None:  # pragma: no cover
    """Uploads a JSON file to an S3 bucket."""
    s3_client = client("s3", aws_access_key_id=config["ACCESS_KEY"],
                       aws_secret_access_key=config["SECRET_KEY"])
    s3_client.upload_file(
        json_filename, config["REDDIT_JSON_BUCKET_NAME"], json_filename)


def get_json_from_request(subreddit_url: str, reddit_access_token: str) -> dict:
    """Returns the contents of a subreddit page GET request."""
    auth_headers = {"Authorization": f"bearer {reddit_access_token}",
                    "User-Agent": "Media-Sentiment/0.1 by Media-Project"}
    parameters = {"limit": MAX_REDDIT_COMMENTS, "show": "all"}

    response = requests.get(
        subreddit_url, headers=auth_headers, params=parameters)
    if response.status_code != 200:
        raise ConnectionError(
            f"Unexpected non-200 status code returned for the url: {subreddit_url}. " +
            f"Code: {response.status_code}")
    return response.json()


def read_json_as_text(json_filename: str) -> list[str]:  # pragma: no cover
    """Returns the contents of a JSON file as a list of strings."""
    with open(json_filename, "r") as f_obj:
        return f_obj.readlines()


def remove_unrecognised_formatting(comment: str) -> str:
    """Removes formatting not recognised by Vader."""
    characters_to_remove = ("\n", "\\n", "#x200B;",
                            "\\u2013", "&gt;", "\\u2026")
    for text in characters_to_remove:
        comment = comment.replace(text, "")

    characters_to_replace = (
        {"&amp;": "&", "\\u2018": "'", "\\u2019": "'", "\\u00a": "£", "\\u201c": "\"", "\\u201d": "\""})

    for text in characters_to_replace:
        comment = comment.replace(text, characters_to_replace[text])

    comment = re.sub(r"\[(.+)\]\(.+\)", "\\1", comment)

    return comment


def clean_reddit_comments(comment: str) -> str | bool:
    """Returns a comment in a format supported by Vader.

    If a comment is unsuitable to be used False is returned."""
    comment = remove_unrecognised_formatting(comment)
    if (comment not in {"[removed]", "[deleted]"}
        and "**Removed/tempban**" not in comment
            and "**Removed/warning**" not in comment):
        return comment
    return False


def get_comments_list(json_filename: str) -> list[str]:
    """Returns a list of comments from a file."""
    comment_list = []
    json_content = read_json_as_text(json_filename)
    for line in json_content:
        line = line.strip()
        find_comment = re.search(r"\"body\": \"(.+)\",", line)
        if find_comment:
            comment = find_comment.group(1)
            cleaned_comment = clean_reddit_comments(comment)
            if cleaned_comment:
                comment_list.append(cleaned_comment)
    return comment_list


def process_each_reddit_page(pages_list: list[dict], reddit_access_token: str, config: dict) -> list[dict]:
    """Iterates through the list of Reddit pages.

    Fetches the JSON, uploads to S3 and processes it.
    """
    print("Commencing fetch of subreddit pages.")
    response_list = []
    for page in pages_list:
        try:
            json_filename = create_json_filename(page[REDDIT_TITLE_KEY])
            page_json = get_json_from_request(
                SUBREDDIT_URL+page[REDDIT_SUBREDDIT_URL], reddit_access_token)
            save_json_to_file(page_json, json_filename)
            upload_json_s3(config, json_filename)
            page[REDDIT_COMMENTS] = get_comments_list(json_filename)
            page[REDDIT_INCLUDED_COMMENTS] = len(page[REDDIT_COMMENTS])
            response_list.append(page)
        except (ConnectionError, AttributeError) as err:
            print(err)
    print("Fetch of each subreddit page complete.")
    return response_list


def run_extract() -> list[dict]:  # pragma: no cover
    """Returns a list of dictionaries for each page in a subreddit."""
    configuration = os.environ
    reddit_token = get_reddit_access_token(configuration)
    reddit_json = get_subreddit_json(configuration, reddit_token)
    list_of_json = create_pages_list(reddit_json)
    return process_each_reddit_page(
        list_of_json, reddit_token, configuration)


if __name__ == "__main__":  # pragma: no cover
    configuration = dotenv_values()
    reddit_token = get_reddit_access_token(configuration)
    reddit_json = get_subreddit_json(configuration, reddit_token)
    list_of_json = create_pages_list(reddit_json)
    list_of_page_dict = process_each_reddit_page(
        list_of_json, reddit_token, configuration)

    print(list_of_page_dict)

    save_json_to_file(list_of_page_dict, "with_comments_2.json")
