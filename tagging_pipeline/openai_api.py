"""Makes POST requests to the openai API to find three main topics relating to the article title"""

from os import environ

from dotenv import load_dotenv
import requests
from nltk.corpus import wordnet
import pandas as pd

PROMPT = """Generate three keywords each article's main topics. Good topics include country, famous individuals, an organization, or a particular action. 
For example, the headline, 'RAAC crisis: Sunak defends school record after cowboy-builder jibe" should return the topics "Sunak,Education,Jibe', while the headline 'Sir Gavin Williamson apologises over bullying texts' should return 'Sir Gavin Williamson, Bully, Apologise'.
You should return only one word per topic (famous names are an exception). Between articles, if any words have similar meanings, switch them with one general word to make grouping articles easier. Using this example: "[{3: 'Burger, 'Advert', 'Appearance'}, {4: 'Zoo', 'Panda', 'China'}]", output the words with the corresponding story id for this list of articles: """


def make_openai_request(command):
    openapi_url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {environ['OPENAI_API_KEY']}"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": command}],
        "temperature": 0.3
    }
    response = requests.post(openapi_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Unable to make request")
        print(response.status_code)


def get_three_article_topics(response) -> list:
    all_topics = response['choices'][0]['message']['content']
    return eval(all_topics)


def find_synset_for_topic(topic):
    for syn in wordnet.synsets(topic):
        for lemma in syn.lemmas():
            print(lemma.name())


def populate_keywords_table(conn, topics):
    for topic in topics:
        return find_synset_for_topic(topic)


if __name__ == "__main__":
    load_dotenv()
    article_title = []
    article_title.append(
        "My husband makes £100,000 more than me but wants be to be a stay-at-home mother so we don't have to pay for nursery - people say I should divorce him")
    article_title.append("Woody Allen, 87, is booed by critics as he arrives with wife Soon-Yi Previn, 52, - who is his ex-girlfriend's adopted daughter - and their children at the controversial director's Coup De Chance screening in Venice")
    article_title.append("Why your burger may not always look like the advert")
    article_title.append(
        "Edinburgh Zoo's giant pandas to return to China in December")
    # command = f'Using this example formatting, "Appearance, advertising, reality", List three general single-word topics for this article with your response strictly being three words: {article_title}'

    response = make_openai_request(PROMPT + f"{article_title}")
    # response = {'id': 'chatcmpl-7w8b5FjQh33IR9WJsyXkvFjwNlCxV', 'object': 'chat.completion', 'created': 1694090427, 'model': 'gpt-3.5-turbo-0613', 'choices': [{'index': 0, 'message': {
    #     'role': 'assistant', 'content': '[{"1": "Divorce", "2": "Income", "3": "Nursery"}, {"1": "Woody Allen", "2": "Critics", "3": "Screening"}, {"1": "Burger", "2": "Advert", "3": "Appearance"}, {"1": "Edinburgh Zoo", "2": "Pandas", "3": "China"}]'}, 'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 298, 'completion_tokens': 86, 'total_tokens': 384}}
    print(response)
    # formatted = (get_three_article_topics(response))
    # print(formatted)
    # find_synset_for_topic('bullying')


# Make sure to put print statements all over to see the logs (time taken for each api request, etc )
# make some edge cases incase the numbers are replaced with title headlines
