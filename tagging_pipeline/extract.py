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
For example, the headline, 'Sunak questioned by Police Service of Northern Ireland for vandalization" should return the topics "Politics,Crime,Law", while the headline 'Royal family requests giant pandas to return to China in December' should return "Animals, International, Monarchy".
You must return only one word for each topic. For example, if Queen Elizabeth and Prince Harry are the main topics, one of the three output topics could be Monarchy. Good topics are but not restricted to: Monarchy, Relationships, Football, War, Shopping, Crime, Law, Politics, Education.
The output for each story MUST be in the format where the key corresponds to the INT provided with the story and its paired value is a list of the topics (do not return the title under any circumstances). Here's an example output for two stories: "[{3: ['Weather', 'History', 'Technology']}, {4: ['Health', 'Science', 'Celebrities']}]", output a list of dictionaries for these stories: """
MAX_LIST_SIZE = 40
CURRENT_TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


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
    """Queries RDS to find stories that do not have keywords linked to them"""
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
    """Allows openai requests to be made with 20 stories or less at a time"""
    count = 0
    for batch_stories_list in separate_stories(all_stories_list):
        if count == 2:
            return  # remove count after testing
        count += 1
        openai_response = make_openai_request(batch_stories_list)
        create_response_json(openai_response)
        batch_stories_topics = get_story_topics(openai_response)
        create_topic_csv(batch_stories_topics)


def create_response_json(openai_response):
    """Stores openai response in a json file"""
    file_name = f'api_response/{CURRENT_TIMESTAMP}.json'
    exists = os.path.exists(file_name)
    with open(file_name, 'a') as f:
        if exists:
            f.write(',')
        json.dump(openai_response, f, indent=4)


def create_topic_csv(batch_stories_topics):
    """Stores story topics in a csv file"""
    response_df = pd.DataFrame(
        columns=['story_id', 'topic_one', 'topic_two', 'topic_three'])
    for story_data in batch_stories_topics:
        for story_id, story_topics in story_data.items():
            if isinstance(story_topics, list):
                while len(story_topics) < 3:  # include an edge case if a list isn't provided
                    story_topics.append("")
                new_row = {'story_id': story_id,
                           'topic_one': story_topics[0], 'topic_two': story_topics[1], 'topic_three': story_topics[2]}
                response_df.loc[len(response_df)] = new_row
    if not os.path.exists(f'topics/{CURRENT_TIMESTAMP}.csv'):
        response_df.to_csv(f'topics/{CURRENT_TIMESTAMP}.csv')
    else:
        existing_df = pd.read_csv(f'topics/{CURRENT_TIMESTAMP}.csv')
        combined_df = pd.concat([existing_df, response_df], ignore_index=True)
        combined_df.to_csv(f'topics/{CURRENT_TIMESTAMP}.csv', index=False)


def get_story_topics(response) -> list:
    """"""
    all_topics = response['choices'][0]['message']['content']
    all_dicts = re.findall('\{(.*?)\}', all_topics)
    cleaned_topics = []

    for topic in all_dicts:
        try:
            topic_split = topic.split(':')
            cleaned_topics.append({int(topic_split[0]): eval(topic_split[1])})
        except:
            continue
    return cleaned_topics


if __name__ == "__main__":
    load_dotenv()
    environ = os.environ

    connection = create_database_connection()
    all_stories_list = get_public_stories(connection)
    format_openai_request(all_stories_list)
    connection.close()

    # print(get_story_topics({
    #     "id": "chatcmpl-7wV97kkLjBYUOlAQVMWmp1veV62bK",
    #     "object": "chat.completion",
    #     "created": 1694177105,
    #     "model": "gpt-3.5-turbo-0613",
    #     "choices": [
    #         {
    #             "index": 0,
    #             "message": {
    #                 "role": "assistant",
    #                 "content": "[{1460: ['Monarchy', 'Relationships', 'General']}, {121: ['Food', 'International', 'General']}, {552: ['Relationships', 'General', 'General']}, {152: ['Sports', 'General', 'General']}, {537: ['Politics', 'General', 'General']}, {237: ['Relationships', 'Gener... 'General']}, {938: ['Relationships', 'General', 'General']}, {44: ['Crime', 'General', 'General']}, {1312: ['Animals', 'General', 'General']}, {208: ['Sports', 'General', 'General']}, {2008: ['Crime', 'General', 'General']}]"
    #             },
    #             "finish_reason": "stop"
    #         }
    #     ],
    #     "usage": {
    #         "prompt_tokens": 1837,
    #         "completion_tokens": 152,
    #         "total_tokens": 1989
    #     }
    # }))
