"""Contains the functions required to insert rows to the reddit_article table."""

import sys
import time

from dotenv import dotenv_values
from psycopg2 import connect

from transform import run_transform

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
REDDIT_SENTIMENT_MEAN = "mean_sentiment"
REDDIT_SENTIMENT_ST_DEV = "st_dev_sentiment"
REDDIT_SENTIMENT_MEDIAN = "median_sentiment"


def establish_database_connection(config: dict):  # pragma: no cover
    """Establishes a connection with the PostgreSQL RDS database."""
    try:
        return connect(
            user=config['DATABASE_USERNAME'],
            password=config['DATABASE_PASSWORD'],
            host=config['DATABASE_ENDPOINT'],
            port=config['DATABASE_PORT'],
            database=config['DATABASE_NAME'])
    except ValueError as err:
        print("Error connecting to database: ", err)
        sys.exit()


def check_if_row_exists(conn, text: str) -> int:  # pragma: no cover
    """Returns the re_article_id if a row already exists in the reddit_article table."""
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT * FROM reddit_article 
                    WHERE re_url = %s;""",
                    (text,))
        returned = cur.fetchone()
        if returned:
            return returned[0]
        return False


def update_reddit_article_row(conn, page: dict, existing_article_id: int):  # pragma: no cover
    """Updates the columns in reddit_article for an existing row."""
    re_domain = page[REDDIT_ARTICLE_DOMAIN]
    re_title = page[REDDIT_TITLE_KEY]
    re_article_url = page[REDDIT_ARTICLE_URL]
    re_url = page[REDDIT_SUBREDDIT_URL]
    re_sentiment_mean = page[REDDIT_SENTIMENT_MEAN]
    re_sentiment_st_dev = page[REDDIT_SENTIMENT_ST_DEV]
    re_sentiment_median = page[REDDIT_SENTIMENT_MEDIAN]
    re_vote_score = page[REDDIT_ARTICLE_SCORE]
    re_upvote_ratio = page[REDDIT_UPVOTE_RATIO]
    re_post_comments = page[REDDIT_POST_COMMENTS]
    re_processed_comments = page[REDDIT_INCLUDED_COMMENTS]
    re_created_timestamp = page[REDDIT_CREATED_UTC]
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE reddit_article SET re_domain = %s, re_title = %s, re_article_url = %s, re_url = %s, 
                    re_sentiment_mean = %s, re_sentiment_st_dev = %s, re_sentiment_median = %s, re_vote_score = %s,
                    re_upvote_ratio = %s, re_post_comments = %s, re_processed_comments = %s, re_created_timestamp = %s
                    WHERE re_article_id = %s;""",
                    (re_domain, re_title, re_article_url, re_url, re_sentiment_mean,
                     re_sentiment_st_dev, re_sentiment_median, re_vote_score, re_upvote_ratio,
                     re_post_comments, re_processed_comments, re_created_timestamp, existing_article_id))
        conn.commit()


def insert_row_into_reddit_article(conn, page: dict) -> None:  # pragma: no cover
    """Inserts a row into the reddit_article table."""
    re_domain = page[REDDIT_ARTICLE_DOMAIN]
    re_title = page[REDDIT_TITLE_KEY]
    re_article_url = page[REDDIT_ARTICLE_URL]
    re_url = page[REDDIT_SUBREDDIT_URL]
    re_sentiment_mean = page[REDDIT_SENTIMENT_MEAN]
    re_sentiment_st_dev = page[REDDIT_SENTIMENT_ST_DEV]
    re_sentiment_median = page[REDDIT_SENTIMENT_MEDIAN]
    re_vote_score = page[REDDIT_ARTICLE_SCORE]
    re_upvote_ratio = page[REDDIT_UPVOTE_RATIO]
    re_post_comments = page[REDDIT_POST_COMMENTS]
    re_processed_comments = page[REDDIT_INCLUDED_COMMENTS]
    re_created_timestamp = page[REDDIT_CREATED_UTC]
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO reddit_article (re_domain, re_title, re_article_url, re_url, 
                    re_sentiment_mean, re_sentiment_st_dev, re_sentiment_median, re_vote_score,
                    re_upvote_ratio, re_post_comments, re_processed_comments, re_created_timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                    (re_domain, re_title, re_article_url, re_url, re_sentiment_mean,
                     re_sentiment_st_dev, re_sentiment_median, re_vote_score, re_upvote_ratio,
                     re_post_comments, re_processed_comments, re_created_timestamp))
        conn.commit()


def load_each_row_into_database(conn, page_response_list: list[dict]) -> None:
    """Loads each page into the database."""
    print("Commencing loading pages into database.")
    row_count = 0
    modified_count = 0
    for page in page_response_list:
        try:
            existing_id = check_if_row_exists(conn, page[REDDIT_SUBREDDIT_URL])
            if existing_id:
                update_reddit_article_row(conn, page, existing_id)
                modified_count += 1
            else:
                insert_row_into_reddit_article(conn, page)
                row_count += 1
        except ValueError as err:
            print(err)
    print("Completed loading pages into database.")
    print(f"Successfully added {row_count} rows.")
    print(f"Successfully modified {modified_count} rows.")


if __name__ == "__main__":  # pragma: no cover
    configuration = dotenv_values()
    list_of_page_dict = run_transform()
    start = time.time()
    connection = establish_database_connection(configuration)
    load_each_row_into_database(connection, list_of_page_dict)
    connection.close()
    print(f"Time to run load: {(time.time()-start):.2f} seconds.")
