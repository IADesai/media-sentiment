"""Extracts media and reddit article titles from the RDS"""

import os
import json
from datetime import datetime
import re

import requests

import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2 import extras

TITLE = "title"

PROMPT = """Generate three words for each story's main topics.
For example, the headline 'Sunak questioned by Police Service of Northern Ireland for vandalism" should return the topics "Politics, Crime, Law", while the headline 'Royal family requests giant pandas to return to China in December' should return "Animals, China, Monarchy".
You must return only one word for each topic. Make sure topics are broad to allow grouping stories by topic easier, for example, if Queen Elizabeth or Prince Harry are mentioned in the story, one of the three output topics should be 'Monarchy', or an output topic may be 'Crime' if the story is about theft. Good topics include but are not limited to: Monarchy, Relationships, Football, War, Shopping, Crime, Law, Politics, Education, Scandal, Finance, Climate, Government, Accident.
The output for each story MUST be in a Python dictionary format where the key corresponds to the INT provided with the story and its paired value being a list of the topics (do not return the title under any circumstances). Here's an example output for two stories: "[{3: ['Weather', 'History', 'Technology']}, {4: ['Health', 'Science', 'Celebrity']}]", output a list of dictionaries for these stories: """

MAX_LIST_SIZE = 75
CURRENT_TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
JSON_FILE = f'responses/{CURRENT_TIMESTAMP}.json'


def create_database_connection() -> psycopg2.extensions.connection | None:
    """Establish connection with the media-sentiment RDS"""

    try:
        return psycopg2.connect(dbname=environ["DATABASE_NAME"],
                                user=environ["DATABASE_USERNAME"],
                                host=environ["DATABASE_ENDPOINT"],
                                password=environ["DATABASE_PASSWORD"],
                                cursor_factory=psycopg2.extras.RealDictCursor)

    except Exception as exc:
        raise psycopg2.DatabaseError("Error connecting to database.") from exc


def get_public_stories(conn) -> list | None:
    """Queries RDS to return story title and id of stories that do not have keywords linked to them"""

    with conn.cursor() as cur:
        cur.execute(
            """SELECT stories.story_id, stories.title FROM stories LEFT JOIN story_keyword_link 
            ON stories.story_id = story_keyword_link.story_id WHERE story_keyword_link.story_id IS NULL ORDER BY RANDOM();"""
        )
        stories = cur.fetchall()
        return stories if stories else None


def separate_stories(stories_list: list) -> None:
    """Stores maximum of 40 stories into lists to be passed into functions"""

    twenty_stories = []
    for story in stories_list:
        twenty_stories.append(dict(story))
        if len(twenty_stories) >= MAX_LIST_SIZE:
            yield twenty_stories
            twenty_stories = []
    yield twenty_stories if twenty_stories else None


def make_openai_request(batch_stories_list):
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


def format_openai_request(all_stories_list: list):
    """Allows openai requests to be made with 40 stories or less at a time"""

    count = 0
    for batch_stories_list in separate_stories(all_stories_list):
        if count == 2:
            return  # remove count after testing
        count += 1
        openai_response = make_openai_request(batch_stories_list)
        create_response_json(openai_response)
        batch_stories_topics = get_story_topics(openai_response)
        create_topic_csv(batch_stories_topics)


def read_response_json():
    """Extracts openai response data from json file"""

    with open(JSON_FILE, 'r') as f:
        existing_response = json.load(f)
    return existing_response


def create_response_json(openai_response: dict) -> None:
    """Stores openai response in a json file"""

    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'a') as f:
            json.dump([openai_response], f, indent=4)
    else:
        existing_response = read_response_json()
        existing_response.append(openai_response)
        with open(JSON_FILE, 'w') as f:
            json.dump(existing_response, f, indent=4)


def create_topic_csv(batch_stories):
    """Stores story topics in a csv file"""

    for story in batch_stories:
        for story_id, story_topics in story.items():
            if isinstance(story_topics, list):
                while len(story_topics) < 3:
                    story_topics.append("UNTAGGED")
                new_row = {'story_id': story_id,
                           'topic_one': story_topics[0], 'topic_two': story_topics[1], 'topic_three': story_topics[2]}
                response_df.loc[len(response_df)] = new_row
    if not os.path.exists(f'topics/{CURRENT_TIMESTAMP}.csv'):
        response_df.to_csv(f'topics/{CURRENT_TIMESTAMP}.csv', index=True)
    else:
        existing_df = pd.read_csv(f'topics/{CURRENT_TIMESTAMP}.csv')
        combined_df = pd.concat([existing_df, response_df], ignore_index=True)
        combined_df.to_csv(f'topics/{CURRENT_TIMESTAMP}.csv', index=True)


# def get_story_topics(response) -> list:
#     """"""
#     all_topics = response['choices'][0]['message']['content']
#     all_dicts = re.findall('\{(.*?)\}', all_topics)
#     cleaned_topics = []

#     for topic in all_dicts:
#         try:
#             topic_split = topic.split(':')
#             cleaned_topics.append({int(topic_split[0]): eval(topic_split[1])})
#         except:
#             continue
#     return cleaned_topics


if __name__ == "__main__":
    load_dotenv()
    environ = os.environ
    response_df = pd.DataFrame(
        columns=['story_id', 'topic_one', 'topic_two', 'topic_three'])

    # connection = create_database_connection()
    # all_stories_list = get_public_stories(connection)
    # format_openai_request(all_stories_list)
    # connection.close()
