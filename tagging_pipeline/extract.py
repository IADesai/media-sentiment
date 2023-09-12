"""Extracts media and reddit article titles from the RDS"""

from os import environ
from os.path import exists
import json
from datetime import datetime

import requests

TITLE = "title"
PROMPT = """Generate three words for each story's main topics.
For example, the headline 'Sunak questioned by Police Service of Northern Ireland for vandalism" should return the topics "Politics, Crime, Law", while the headline 'Royal family requests giant pandas to return to China in December' should return "Animals, China, Monarchy".
You must return only one word for each topic. Make sure topics are broad to allow grouping stories by topic easier, for example, if Queen Elizabeth or Prince Harry are mentioned in the story, one of the three output topics should be 'Monarchy', or an output topic may be 'Crime' if the story is about theft. Good topics include but are not limited to: Monarchy, Relationships, Football, War, Shopping, Crime, Law, Politics, Education, Scandal, Finance, Climate, Government, Accident.
The output for each story MUST be in a Python dictionary format where the key corresponds to the INT provided with the story and its paired value being a list of the topics (do not return the title under any circumstances). Here's an example output for two stories: "[{3: ['Weather', 'History', 'Technology']}, {4: ['Health', 'Science', 'Celebrity']}]", output a list of dictionaries for these stories: """
MAX_LIST_SIZE = 50
CURRENT_TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
JSON_FILE = f'response.json'


def get_media_stories(conn) -> list | None:
    """Queries RDS to return story title and id that do not have keywords linked to them"""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT stories.story_id, stories.title FROM stories LEFT JOIN story_keyword_link 
            ON stories.story_id = story_keyword_link.story_id WHERE story_keyword_link.story_id IS NULL ORDER BY RANDOM();"""
        )
        stories = cur.fetchall()
        return stories if stories else None


def get_reddit_stories(conn) -> list | None:
    """Queries RDS to return reddit story title and id that do not have keywords linked to them"""
    with conn.cursor() as cur:
        cur.execute(
            """SELECT reddit_article.re_article_id, reddit_article.re_title FROM reddit_article LEFT JOIN reddit_keyword_link 
            ON reddit_article.re_article_id = reddit_keyword_link.re_article_id WHERE reddit_keyword_link.re_article_id IS NULL ORDER BY RANDOM();"""
        )
        re_stories = cur.fetchall()
        return re_stories if re_stories else None


def separate_stories(stories_list: list) -> None:
    """Stores maximum of 50 stories into lists to be passed into functions"""
    twenty_stories = []
    for story in stories_list:
        twenty_stories.append(dict(story))
        if len(twenty_stories) >= MAX_LIST_SIZE:
            yield twenty_stories
            twenty_stories = []
    yield twenty_stories if twenty_stories else None


def make_openai_request(batch_stories_list: list[dict]) -> None:
    """Makes POST request to openai to retrieve three general topics per story"""
    openapi_url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {environ['OPENAI_API_KEY']}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": PROMPT + f"{batch_stories_list}"}],
        "temperature": 0.1
    }
    response = requests.post(openapi_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise ConnectionError("Unable to make request", response.status_code)


def read_response_json(table: str):
    """Extracts openai response data from json file"""
    with open(f"{table}-{JSON_FILE}", 'r') as f:
        existing_response = json.load(f)
    return existing_response


def create_response_json(openai_response: dict, table: str) -> None:
    """Stores openai response in a json file"""
    with open(f"{table}-{JSON_FILE}", 'w') as f:
        json.dump(openai_response, f, indent=4)
