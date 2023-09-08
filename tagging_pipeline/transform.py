"""Makes POST requests to the openai API to find three main topics relating to the article title"""

import os
import re

import pandas as pd
from dotenv import load_dotenv
from nltk.corpus import wordnet, stopwords
from gensim.models import word2vec
import spacy
import numpy as np

RESPONSE_TOPICS = ['Menopause', 'Treatments', 'NHS', 'Charged', 'Diabetic', 'Ozempic', 'Shortages',
                   'Hospital', 'Campaign', 'Woke', 'Gender', 'Meat', 'Scientists', 'Contraception', 'Misinformation', 'Face']

GENERAL_TOPICS = ['Animal','International', 'Finance', 'Science', 'Sports', 'Gaming', 'Culture', 'Health', 'Crime', 'Entertainment', 'Transport', 'Monarchy', 'Education', 'Business', 'Technology',
                  'Environment', 'Family', 'Miscellaneous', 'Food', 'Travel', 'Home', 'Events', 'Music', 'Art', 'Celebrities', 'Locations']


def read_topics_csv():
    """Returns most recent csv file in topics folder"""
    csv_files = os.listdir('topics')
    topics_df = pd.read_csv(f'topics/{sorted(csv_files)[0]}')
    return topics_df


def get_topics_list(topics_df):
    topics_list = []
    topics = topics_df[['topic_one', 'topic_two',
                        'topic_three']].values.tolist()
    for sublist in topics:
        for topic in sublist:
            topic = re.sub("[^a-zA-Z]", " ", topic, re.I)
            topics_list.append(topic.lower().strip())
    return topics_list


def get_relevant_topics_list(topics_list):
    stops = set(stopwords.words("english"))
    relevant_topics = [
        word for word in topics_list if not word in stops]
    return relevant_topics


def find_synset_for_topic(topic):
    synonyms = set()
    for syn in wordnet.synsets(topic):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms


def find_syn_testing(response_topics):
    for topic in response_topics:
        print(find_synset_for_topic(topic))


def match_similar_topics(relevant_topics):
    nlp_topics = [nlp(topic) for topic in relevant_topics]
    grouped = {}
    for i in nlp_topics:
        if i not in grouped:
            for j in nlp_topics:
                if j not in grouped:
                    if i.similarity(j) >= 0.7 and not i.similarity(j) == 1:
                        grouped[i] = j
    return grouped


def matching_tests(response_topics, general_topics):
    general_topics = [nlp(topic) for topic in general_topics]
    response_topics = [nlp(topic) for topic in response_topics]
    grouped = {}
    for topic in response_topics:
        for general in general_topics:
            if topic.similarity(general) >= 4:
                grouped[general] = topic
    return grouped


def loop_relevant_topics(relevant_topics):
    for topic in relevant_topics:
        return find_synset_for_topic(topic)


if __name__ == "__main__":
    load_dotenv()
    nlp = spacy.load('en_core_web_lg')
    # topics_df = read_topics_csv()
    # topics_list = (get_topics_list(topics_df))
    # relevant_topics = (get_relevant_topics_list(topics_list))
    # print(match_similar_topics(relevant_topics))
    # print(matching_tests(RESPONSE_TOPICS, GENERAL_TOPICS))
    print(matching_tests(['Health']))

# Make sure to put print statements all over to see the logs (time taken for each api request, etc )
# make some edge cases incase the numbers are replaced with title headlines
