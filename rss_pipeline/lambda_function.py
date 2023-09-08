"""This script is the Lambda function for the full RSS pipeline"""
import time
import pandas as pd
from dotenv import load_dotenv
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from extract_rss import download_bbc_uk_news_xml, download_daily_mail_uk_news_xml
from transform_rss import transform_bbc_xml_file, transform_daily_mail_xml_file
from load import db_connection, insert_articles_into_rds


BBC_UK_NEWS_RSS_LINK = "http://feeds.bbci.co.uk/news/uk/rss.xml"
DAILY_MAIL_UK_NEWS_RSS_LINK = "https://www.dailymail.co.uk/home/index.rss"

BBC_UK_NEWS_XML_FILE_NAME = "bbc_uk_news.xml"
DAILY_MAIL_UK_NEWS_XML_FILE_NAME = "daily_mail_uk_news.xml"


def extract_xml_files_from_rss():
    """Downloads the XML files from the RSS feed"""
    download_bbc_uk_news_xml(BBC_UK_NEWS_RSS_LINK, BBC_UK_NEWS_XML_FILE_NAME)

    download_daily_mail_uk_news_xml(
        DAILY_MAIL_UK_NEWS_RSS_LINK, DAILY_MAIL_UK_NEWS_XML_FILE_NAME)


def transform_xml_files(sentiment_analyser: SentimentIntensityAnalyzer) -> list[pd.DataFrame]:
    """
    Transforms the XML files, obtaining information and then
    converting it to a dataframe
    """
    bbc_articles_df = transform_bbc_xml_file(
        BBC_UK_NEWS_XML_FILE_NAME, sentiment_analyser)
    daily_mail_articles_df = transform_daily_mail_xml_file(
        DAILY_MAIL_UK_NEWS_XML_FILE_NAME, sentiment_analyser)

    return [bbc_articles_df, daily_mail_articles_df]


def handler(event, context):
    start_time = time.time()

    load_dotenv()
    conn = db_connection()

    vader = SentimentIntensityAnalyzer(lexicon_file="vader_lexicon.txt")

    extract_xml_files_from_rss()
    news_df_list = transform_xml_files(vader)

    for news_df in news_df_list:
        insert_articles_into_rds(conn, news_df)

    print("The RSS pipeline took", time.time() - start_time, "to run")

    return [{"Pipeline State": "Success"}]
