'''Extracts data from the rss news articles and populates the media-sentiment relational database (rds)'''

from os import environ

from dotenv import load_dotenv
import pandas as pd
from psycopg2 import errors, extensions, extras
import psycopg2


def db_connection() -> psycopg2.extensions.connection | None:
    '''Establish connection with the media-sentiment rds'''
    try:
        return psycopg2.connect(dbname=environ["DATABASE_NAME"],
                                user=environ["DATABASE_USERNAME"],
                                host=environ["DATABASE_ENDPOINT"],
                                password=environ["DATABASE_PASSWORD"],
                                cursor_factory=psycopg2.extras.RealDictCursor)

    except:
        raise psycopg2.DatabaseError("Error connecting to database.")


def create_dataframe(file_name: str) -> pd.DataFrame:
    '''Creates a Pandas DataFrame with the contents of the provided csv file'''
    rss_df = pd.read_csv(file_name)
    return rss_df


def get_source_id(conn: psycopg2.extensions.connection, url) -> str:
    try:
        source = url.lstrip('https://www.').split('.co.uk')[0]
        with conn.cursor() as cur:
            cur.execute(
                "SELECT source_id FROM sources WHERE source_name = (%s);", [source])
            source_id_dict = cur.fetchone()
        return source_id_dict['source_id']
    except Exception as e:
        print('Error retrieving source')
        print(e.args)


def populate_sources_table(conn: psycopg2.extensions.connection, dataframe: pd.DataFrame) -> None:
    '''Inserts data into the stories table of the rds'''
    for index, row in dataframe.iterrows():
        source_id = get_source_id(conn, row.get('url'))
        try:
            with conn.cursor() as cur:
                values = (source_id, row['title'], row['description'],
                          row['url'], row['pubdate'], row['sentiment_score'])
                cur.execute(
                    "INSERT INTO stories (source_id, title, description, url, pub_date, media_sentiment) VALUES (%s,%s,%s,%s,%s,%s)", values)
                conn.commit()
        except psycopg2.errors.UniqueViolation as err:
            # placeholder but we can discuss how to address dupes (maybe replace original?)
            print('Duplicate data found:', err)
        except Exception as err:
            print('Error populating stories database')
            print(err.args)


if __name__ == "__main__":
    load_dotenv()
    conn = db_connection()
    df = create_dataframe('daily_mail_uk_news.csv')
    populate_sources_table(conn, df)
    conn.close()
