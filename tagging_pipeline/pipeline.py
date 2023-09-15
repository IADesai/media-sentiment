from os import environ
import time

import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2 import extras

from extract import get_media_stories, separate_stories, make_openai_request, create_response_json, read_response_json, get_reddit_stories
from transform import get_story_topics, create_topic_csv
from load import create_keywords_df, load_media_keywords_df_into_rds, load_reddit_keywords_df_into_rds


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


def create_batch_json(start: float, stories_list: list, table: str, id: str) -> None:
    """Creates JSON files for responses made to openai """
    print("Starting pipeline...")
    for batch_stories_list in separate_stories(stories_list):

        print(
            f"OpenAI request made for {len(batch_stories_list)} {table} stories in {time.time()-start:.2f} seconds")
        openai_response = make_openai_request(batch_stories_list)
        create_response_json(openai_response, table)
        media_responses = read_response_json(table)
        valid_stories = get_story_topics(media_responses)
        create_topic_csv(valid_stories, table, id)
        print(
            f"Created {table} CSV file for {len(valid_stories)} stories in {time.time()-start:.2f} seconds")
        keywords_df = create_keywords_df(table)
        if table == 'public':
            load_media_keywords_df_into_rds(connection, keywords_df)
        elif table == 'reddit':
            load_reddit_keywords_df_into_rds(connection, keywords_df)
        print(
            f"Keywords loaded for {table} stories in {time.time()-start:.2f} seconds")


def run_public_and_media_scripts(conn) -> None:
    """Run script to populate tables associated with public and media keywords"""
    start = time.time()
    reddit_stories_list = get_reddit_stories(conn)
    media_stories_list = get_media_stories(conn)
    if reddit_stories_list:
        create_batch_json(start, reddit_stories_list,
                          'reddit', 're_article_id')
    if media_stories_list:
        create_batch_json(start, media_stories_list, 'public', 'story_id')


if __name__ == "__main__":
    load_dotenv()
    response_df = pd.DataFrame(
        columns=['story_id', 'topic_one', 'topic_two', 'topic_three'])
    connection = database_connection()
    run_public_and_media_scripts(connection)
    connection.close()
