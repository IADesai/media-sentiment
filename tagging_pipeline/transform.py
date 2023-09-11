"""Makes POST requests to the openai API to find three main topics relating to the article title"""

from os import environ, listdir
from os.path import exists
import re
from datetime import datetime
import json

import pandas as pd
from dotenv import load_dotenv
from nltk.corpus import wordnet, stopwords
from gensim.models import word2vec
import spacy
import numpy as np

CURRENT_TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
JSON_FILE = f'{CURRENT_TIMESTAMP}.json'


def read_response_json() -> list[dict]:
    """Extracts openai response data from json file."""

    with open(JSON_FILE, 'r') as f:
        responses_list = json.load(f)
    return responses_list


def get_story_topics(responses_list: list[dict]) -> list[dict]:
    """Extracts dictionaries containing each story id and associated topics from the openai response."""
    valid_stories = []
    for response in responses_list:
        all_stories_data = response['choices'][0]['message']['content']
        stories_dict = re.findall('\{(.*?)\}', all_stories_data)
        for story in stories_dict:
            try:
                topic_split = story.split(':')
                valid_stories.append(
                    {int(topic_split[0]): eval(topic_split[1])})
            except:
                continue
    return valid_stories


def create_topic_csv(valid_stories,table,id):
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
    response_df.to_csv(f'{table}-{CURRENT_TIMESTAMP}.csv', index=False)


def create_reddit_topic_csv(valid_stories):
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
    response_df.to_csv(f'reddit-{CURRENT_TIMESTAMP}.csv', index=False)


# def read_topics_csv():
#     """Returns most recent csv file in topics folder"""
#     csv_files = listdir('topics')
#     topics_df = pd.read_csv(f'topics/{sorted(csv_files)[0]}')
#     return topics_df


# def get_topics_list(topics_df):
#     topics_list = []
#     topics = topics_df[['topic_one', 'topic_two',
#                         'topic_three']].values.tolist()
#     for sublist in topics:
#         for topic in sublist:
#             topic = re.sub("[^a-zA-Z]", " ", topic, re.I)
#             topics_list.append(topic.lower().strip())
#     return topics_list


# def get_relevant_topics_list(topics_list):
#     stops = set(stopwords.words("english"))
#     relevant_topics = [
#         word for word in topics_list if not word in stops]
#     return relevant_topics


# def find_synset_for_topic(topic):
#     synonyms = set()
#     for syn in wordnet.synsets(topic):
#         for lemma in syn.lemmas():
#             synonyms.add(lemma.name())
#     return synonyms


# def find_syn_testing(response_topics):
#     for topic in response_topics:
#         print(find_synset_for_topic(topic))


# def match_similar_topics(relevant_topics):
#     nlp_topics = [nlp(topic) for topic in relevant_topics]
#     grouped = {}
#     for i in nlp_topics:
#         if i not in grouped:
#             for j in nlp_topics:
#                 if j not in grouped:
#                     if i.similarity(j) >= 0.7 and not i.similarity(j) == 1:
#                         grouped[i] = j
#     return grouped


# def matching_tests(response_topics, general_topics):
#     # general_topics = [nlp(topic) for topic in general_topics]
#     # response_topics = [nlp(topic) for topic in response_topics]
#     grouped = {}
#     for topic in response_topics:
#         for general in general_topics:
#             if topic.similarity(general) >= 4:
#                 grouped[general] = topic
#     return grouped


# def loop_relevant_topics(relevant_topics):
#     for topic in relevant_topics:
#         return find_synset_for_topic(topic)

if __name__ == "__main__":
    nlp = spacy.load('en_core_web_lg')
    print(nlp('Abuse').similarity(nlp('Animal Abuse')))

    # topics_df = read_topics_csv()
    # topics_list = (get_topics_list(topics_df))
    # relevant_topics = (get_relevant_topics_list(topics_list))
    # print(match_similar_topics(relevant_topics))
    # print(matching_tests(RESPONSE_TOPICS, GENERAL_TOPICS))


# Make sure to put print statements all over to see the logs (time taken for each api request, etc )
# make some edge cases incase the numbers are replaced with title headlines
