"""Inserts keywords from keyword and story data into the keywords, reddit_keyword_link and story_keyword_link tables of RDS"""

from os import environ
from datetime import datetime

import pandas as pd
import psycopg2
from psycopg2 import extras
import spacy

CURRENT_TIMESTAMP = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
CSV_FILE = f'{CURRENT_TIMESTAMP}.csv'


def create_keywords_df(table: str) -> pd.DataFrame:
    """Returns most recent csv file in topics folder"""
    topics_df = pd.read_csv(f"{table}-{CSV_FILE}")
    return topics_df


def populate_keywords_table(conn: psycopg2.extensions.connection, keyword: str) -> dict | None:
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


def get_media_common_keywords(conn) -> list:
    """Retrieves commonly used media story keywords from RDS"""
    with conn.cursor() as cur:
        cur.execute("""SELECT keywords.keyword_id, keywords.keyword, COUNT(sl.keyword_id)
                    FROM keywords
                    LEFT JOIN story_keyword_link sl ON keywords.keyword_id = sl.keyword_id
                    GROUP BY keywords.keyword_id, keywords.keyword
                    HAVING COUNT(sl.keyword_id) > 5;""")
        common_keywords = cur.fetchall()
    return common_keywords


def get_reddit_common_keywords(conn) -> list:
    """Retrieves commonly used reddit story keywords from RDS"""
    with conn.cursor() as cur:
        cur.execute("""SELECT keywords.keyword_id, keywords.keyword, COUNT(rkl.keyword_id)
                    FROM keywords
                    LEFT JOIN reddit_keyword_link rkl ON keywords.keyword_id = rkl.keyword_id
                    LEFT JOIN reddit_article ra ON rkl.re_article_id = ra.re_article_id
                    GROUP BY keywords.keyword_id, keywords.keyword
                    HAVING COUNT(rkl.keyword_id) > 5;""")
        common_keywords = cur.fetchall()
    return common_keywords


def compare_common_keywords(keyword: str, common_keywords: list) -> str | None:
    """Compares new keyword with common keyword to determine if they are within the same category for topics"""
    nlp = spacy.load('en_core_web_lg')
    for common_keyword in common_keywords:
        try:
            if nlp(keyword).similarity(nlp(common_keyword['keyword'])) >= 0.65:
                return common_keyword['keyword']
        except ValueError:
            return


def get_keyword_id(conn, keyword: str) -> int | None:
    """Queries RDS to retrieve keyword_id for the associated keyword else inserts keyword into RDS"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT keyword_id FROM keywords WHERE keyword = (%s);""", [keyword])
            keyword_id = cur.fetchone()
        if not keyword_id:
            keyword_id = populate_keywords_table(conn, keyword)
        return keyword_id['keyword_id']

    except psycopg2.DatabaseError:
        print('Error retrieving keyword id from database', keyword)


def populate_media_keywords_link_table(conn, story_id: int, keyword_id: int) -> None:
    """Inserts story id and keyword id into the story_keywords_link_table to link stories to keywords"""
    try:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO story_keyword_link (story_id,keyword_id) VALUES (%s,%s);""", [
                        story_id, keyword_id])
            conn.commit()
    except psycopg2.errors.UniqueViolation:
        print('Duplicate data was not inserted:', story_id, keyword_id)
        conn.rollback()


def populate_reddit_link_table(conn, story_id: int, keyword_id: int) -> None:
    """Inserts story id and keyword id into the story_keywords_link_table to link stories to keywords"""
    try:
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO reddit_keyword_link (re_article_id,keyword_id) VALUES (%s,%s);""", [
                        story_id, keyword_id])
            conn.commit()
    except psycopg2.errors.UniqueViolation:
        print('Duplicate data was not inserted:', story_id, keyword_id)
        conn.rollback()


def load_media_keywords_df_into_rds(conn, keywords_df: pd.DataFrame) -> None:
    """Loads each row of the dataframe, containing story id and associated topics into the RDS"""
    for index, row in keywords_df.iterrows():
        story_id = row['story_id']
        keyword_one = get_keyword_id(conn, row['topic_one'])
        keyword_two = get_keyword_id(conn, row['topic_two'])
        keyword_three = get_keyword_id(conn, row['topic_three'])
        if keyword_one:
            populate_media_keywords_link_table(conn, story_id, keyword_one)
        if keyword_two:
            populate_media_keywords_link_table(conn, story_id, keyword_two)
        if keyword_three:
            populate_media_keywords_link_table(conn, story_id, keyword_three)


def load_reddit_keywords_df_into_rds(conn, keywords_df: pd.DataFrame) -> None:
    """Loads each row of the dataframe, containing story id and associated topics into the RDS"""
    for index, row in keywords_df.iterrows():
        article_id = row['re_article_id']
        keyword_one = get_keyword_id(conn, row['topic_one'])
        keyword_two = get_keyword_id(conn, row['topic_two'])
        keyword_three = get_keyword_id(conn, row['topic_three'])
        if keyword_one:
            populate_reddit_link_table(conn, article_id, keyword_one)
        if keyword_two:
            populate_reddit_link_table(conn, article_id, keyword_two)
        if keyword_three:
            populate_reddit_link_table(conn, article_id, keyword_three)
