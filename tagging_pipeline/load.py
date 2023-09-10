from os import environ
from datetime import datetime

import pandas as pd
import psycopg2
from psycopg2 import extras
import spacy

from dotenv import load_dotenv

CURRENT_TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
CSV_FILE = f'{CURRENT_TIMESTAMP}.csv'


def db_connection() -> psycopg2.extensions.connection | None:
    """Establish connection with the media-sentiment RDS"""
    try:
        return psycopg2.connect(dbname=environ["DATABASE_NAME"],
                                user=environ["DATABASE_USERNAME"],
                                host=environ["DATABASE_ENDPOINT"],
                                password=environ["DATABASE_PASSWORD"],
                                cursor_factory=psycopg2.extras.RealDictCursor)

    except Exception as exc:
        raise psycopg2.DatabaseError("Error connecting to database.") from exc


def create_keywords_df():
    """Returns most recent csv file in topics folder"""

    topics_df = pd.read_csv(CSV_FILE)
    return topics_df


def populate_keywords_table(conn: psycopg2.extensions.connection, keyword) -> int:
    """Inserts keywords into the keywords table of the RDS"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO keywords (keyword) VALUES (%s) RETURNING keyword_id;""", [keyword])
            keyword_id = cur.fetchone()
        if keyword_id:
            conn.commit()
            return keyword_id

    except psycopg2.errors.UniqueViolation:

        print('Duplicate data was not inserted:', keyword)
        conn.rollback()


# def match_keywords_from_RDS(conn, keyword):
#     """Checks if keyword can be matched with any keywords in RDS and returns most frequently used one"""
#     with conn.cursor() as cur:
#         cur.execute("""SELECT keyword.keyword FROM story_keyword_link link
#                     JOIN keywords keyword ON link.keyword_id = keyword.keyword_id
#                     WHERE keyword.keyword LIKE (%s)
#                     GROUP BY keyword.keyword
#                     ORDER BY COUNT(link.keyword_id) DESC
#                     LIMIT 1;""", [keyword + '%'])
#         match = cur.fetchone()
#     return match if match else None

def get_common_keywords(conn):
    """Retrieves commonly used keywords from RDS"""
    with conn.cursor() as cur:
        cur.execute("""SELECT keywords.keyword_id, keywords.keyword, COUNT(sl.keyword_id)
                    FROM keywords
                    LEFT JOIN story_keyword_link sl ON keywords.keyword_id = sl.keyword_id
                    GROUP BY keywords.keyword_id, keywords.keyword
                    HAVING COUNT(sl.keyword_id) > 5;""")
        common_keywords = cur.fetchall()
    return common_keywords


def compare_common_keywords(keyword, common_keywords):
    """Compares new keyword with common keyword to determine if they are within the same category for topics"""
    for common_keyword in common_keywords:
        if nlp(keyword).similarity(nlp(common_keyword['keyword'])) >= 0.7:
            return common_keyword['keyword']


def get_keyword_id(conn, keyword) -> int | None:
    """Queries RDS to retrieve keyword_id for the associated keyword else inserts keyword into RDS"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT keyword_id FROM keywords WHERE keyword = (%s);""", [keyword])
            keyword_id = cur.fetchone()
        if not keyword_id:
            common_keywords = get_common_keywords(conn)
            matched_keyword = compare_common_keywords(keyword,common_keywords)
            if matched_keyword:
                return matched_keyword
            keyword_id = populate_keywords_table(conn, keyword)
        return keyword_id['keyword_id']

    except psycopg2.DatabaseError:
        print('Error retrieving keyword id from database', keyword)


def populate_keywords_link_table(conn: psycopg2.extensions.connection, story_id, keyword_id) -> None:
    """Inserts story id and keyword id into the story_keywords_link_table to link stories to keywords"""
    try:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO story_keyword_link (story_id,keyword_id) VALUES (%s,%s);""", [
                        story_id, keyword_id])
            conn.commit()
    except psycopg2.errors.UniqueViolation:
        print('Duplicate data was not inserted:', story_id, keyword_id)
        conn.rollback()


def load_keywords_df_into_rds(conn, keywords_df) -> None:
    """Loads each row of the dataframe, containing story id and associated topics into the RDS"""
    for index, row in keywords_df.iterrows():
        story_id = row['story_id']
        keyword_one = get_keyword_id(conn, row['topic_one'])
        keyword_two = get_keyword_id(conn, row['topic_two'])
        keyword_three = get_keyword_id(conn, row['topic_three'])
        if keyword_one:
            populate_keywords_link_table(conn, story_id, keyword_one)
        if keyword_two:
            populate_keywords_link_table(conn, story_id, keyword_two)
        if keyword_three:
            populate_keywords_link_table(conn, story_id, keyword_three)


if __name__ == "__main__":
    load_dotenv()
    nlp = spacy.load('en_core_web_lg')

    connection = db_connection()
    common_keywords = get_common_keywords(connection)
    print(compare_common_keywords('Finances', common_keywords))
