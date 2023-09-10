import os

from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2 import extras


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
    csv_files = os.listdir('topics')

    topics_df = pd.read_csv(f'topics/{sorted(csv_files)[-1]}')
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


def get_keyword_id(conn, keyword) -> int | None:
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
    environ = os.environ
    connection = db_connection()
    keywords_df = create_keywords_df()
    load_keywords_df_into_rds(connection, keywords_df)
    connection.close()
