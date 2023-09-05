"""Extracts data from RSS news articles to populate the media-sentiment relational database (RDS)"""

from os import environ

from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2 import errors, extras, extensions

TITLE = 'title'
DESCRIPTION = 'description'
URL = 'url'
PUBDATE = 'pubdate'
SENTIMENT = 'sentiment_score'


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


def create_dataframe(file_name: str) -> pd.DataFrame:
    """Creates a Pandas DataFrame with the contents of the provided csv file"""
    rss_df = pd.read_csv(file_name)
    return rss_df


def extract_source_from_url(url: str) -> str | None:
    """Extracts article source from url"""
    try:
        return url.split('https://www.')[1].split('.')[0]
    except IndexError:
        print('Source was unable to be extracted: ', url)
    return None


def get_source_id(conn: psycopg2.extensions.connection, url: str) -> str | None:
    """Queries RDS to find source_id of the provided source"""
    source = extract_source_from_url(url)
    if source:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT source_id FROM sources WHERE source_name = (%s);", [source])
                source_id_dict = cur.fetchone()
                return source_id_dict['source_id']
        except psycopg2.DatabaseError:
            print('Error retrieving source id from database', url)
    return None


def populate_sources_table(conn: psycopg2.extensions.connection, dataframe: pd.DataFrame) -> None:
    """Inserts data into the stories table of the RDS"""
    for row in dataframe.iterrows():
        article = row[1]
        url = article.get(URL)
        source_id = get_source_id(conn, url)
        if source_id:
            try:
                with conn.cursor() as cur:
                    values = (source_id, article[TITLE], article[DESCRIPTION],
                              article[URL], article[PUBDATE], article[SENTIMENT])
                    cur.execute(
                        "INSERT INTO stories "
                        "(source_id, title, description, url, pub_date, media_sentiment) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", values)
                    conn.commit()

            except psycopg2.errors.UniqueViolation:
                # placeholder but we can discuss how to address dupes (maybe replace original?)
                print('Duplicate data found:', url)
                conn.rollback()


if __name__ == "__main__":
    load_dotenv()
    conn = db_connection()
    df = create_dataframe('bbc_uk_news.csv')
    populate_sources_table(conn, df)
    conn.close()
