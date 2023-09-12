"""Makes POST requests to the openai API to find three main topics relating to the article title"""

import re
from datetime import datetime
import json

import pandas as pd

CURRENT_TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
JSON_FILE = f'response.json'


def read_response_json() -> list[dict]:
    """Extracts openai response data from json file."""

    with open(JSON_FILE, 'r') as f:
        response_list = json.load(f)
    return response_list


def get_story_topics(response_list: list[dict]) -> list[dict]:
    """Extracts dictionaries containing each story id and associated topics from the openai response."""
    valid_stories = []

    all_stories_data = response_list['choices'][0]['message']['content']
    stories_dict = re.findall('\{(.*?)\}', all_stories_data)
    for story in stories_dict:
        try:
            topic_split = story.split(':')
            valid_stories.append(
                {int(topic_split[0]): eval(topic_split[1])})
        except:
            continue
    return valid_stories


def create_topic_csv(valid_stories: list[dict], table: str, id: str) -> None:
    """Stores media story topics in a csv file"""
    response_df = pd.DataFrame(
        columns=[id, 'topic_one', 'topic_two', 'topic_three'])
    for story_dict in valid_stories:
        for story_id, story_topics in story_dict.items():
            if isinstance(story_topics, list):
                while len(story_topics) < 3:
                    story_topics.append("UNTAGGED")
                new_row = {id: story_id,
                           'topic_one': story_topics[0], 'topic_two': story_topics[1], 'topic_three': story_topics[2]}
                response_df.loc[len(response_df)] = new_row
    response_df.to_csv(f'{table}.csv', index=False)


def create_reddit_topic_csv(valid_stories: list[dict]) -> None:
    """Stores reddit story topics in a csv file"""
    response_df = pd.DataFrame(
        columns=['re_article_id', 'topic_one', 'topic_two', 'topic_three'])
    for story_dict in valid_stories:
        for story_id, story_topics in story_dict.items():
            if isinstance(story_topics, list):
                while len(story_topics) < 3:
                    story_topics.append("UNTAGGED")
                new_row = {'re_article_id': story_id,
                           'topic_one': story_topics[0], 'topic_two': story_topics[1], 'topic_three': story_topics[2]}
                response_df.loc[len(response_df)] = new_row
    response_df.to_csv(f'reddit.csv', index=False)
