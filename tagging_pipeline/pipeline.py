from os import environ
import time

import pandas as pd
from dotenv import load_dotenv
import psycopg2
import spacy
from psycopg2 import extras

from extract import get_public_stories, separate_stories, make_openai_request, create_response_json, read_response_json
from transform import get_story_topics, create_topic_csv
from load import create_keywords_df, load_keywords_df_into_rds


def database_connection() -> psycopg2.extensions.connection | None:
    """Establish connection with the media-sentiment RDS"""

    try:
        return psycopg2.connect(dbname=environ["DATABASE_NAME"],
                                user=environ["DATABASE_USERNAME"],
                                host=environ["DATABASE_ENDPOINT"],
                                password=environ["DATABASE_PASSWORD"],
                                cursor_factory=psycopg2.extras.RealDictCursor)

    except Exception as exc:
        raise psycopg2.DatabaseError("Error connecting to database.") from exc


def run_pipeline(conn):
    start = time.time()
    print("Starting pipeline...")
    all_stories_list = get_public_stories(conn)
    request_count = 1
    stories_count = 0
    count = 0  # remove count after testing
    for batch_stories_list in separate_stories(all_stories_list):
        print(
            f"OpenAI request {request_count} made for {len(batch_stories_list)} stories in {time.time()-start:.2f} seconds")
        if count == 1:  # remove count after testing or use if stories_count > 200:
            break  # remove count after testing
        count += 1  # remove count after testing
        openai_response = make_openai_request(batch_stories_list)
        create_response_json(openai_response)
        print(
            f"Response from request {request_count} added to JSON file in {time.time()-start:.2f} seconds")
        request_count += 1
        stories_count += len(batch_stories_list)
    responses_list = read_response_json()
    valid_stories = get_story_topics(responses_list)
    create_topic_csv(valid_stories)
    print(
        f"Added {stories_count} stories to CSV in {time.time()-start:.2f} seconds")
    keywords_df = create_keywords_df()
    load_keywords_df_into_rds(connection, keywords_df)
    print(f"Keywords added to RDS in {time.time() - start:.2f} seconds")


def lambda_handler(event=None, context=None):
    # Discussion required to use ECS or Lambda
    pass


if __name__ == "__main__":
    load_dotenv()
    nlp = spacy.load('en_core_web_lg')

    response_df = pd.DataFrame(
        columns=['story_id', 'topic_one', 'topic_two', 'topic_three'])
    connection = database_connection()
    run_pipeline(connection)
    connection.close()
