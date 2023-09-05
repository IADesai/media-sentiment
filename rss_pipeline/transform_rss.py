"""This script converts the XML to dataframes and cleans them"""

from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

BBC_UK_NEWS_XML_FILE_NAME = "bbc_uk_news.xml"
DAILY_MAIL_UK_NEWS_XML_FILE_NAME = "daily_mail_uk_news.xml"

BBC_UK_NEWS_CSV_FILENAME = "bbc_uk_news.csv"
DAILY_MAIL_UK_NEWS_CSV_FILENAME = "daily_mail_uk_news.csv"


def extract_info_from_bbc_articles(xml_file: str) -> pd.DataFrame:
    """
    Extracts the title, description, article URL and publication date
    from the XML file, saves it as a dataframe
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    articles = []

    for item in root.findall('.//item'):
        article = {}

        article['title'] = item.find('title').text
        article['description'] = item.find('description').text
        article['url'] = item.find('guid').text
        article['pubdate'] = item.find('pubDate').text

        articles.append(article)

    return pd.DataFrame(articles)


def extract_info_from_daily_mail_articles(xml_file: str) -> pd.DataFrame:
    """
    Extracts the title, description, article URL and publication date
    from the XML file, saves it as a dataframe
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    articles = []

    for item in root.findall('.//item'):
        article = {}

        article['title'] = item.find('title').text
        article['description'] = item.find('description').text
        article['url'] = item.find('guid').text
        article['pubdate'] = item.find('pubDate').text
        articles.append(article)

    return pd.DataFrame(articles)


def convert_pubdate_to_timestamp(pubdate: str) -> datetime:
    """Converts the publication date to a timestamp"""
    try:
        timestamp = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        timestamp = datetime.now()

    return timestamp


def remove_headline_tags(headline: str) -> str:
    """Removes unnecessary tags from the headline"""
    headline_tags = [
        "BREAKING", "EXCLUSIVE",
        "UPDATE", "LIVE",
        "EXCLUSIVE INTERVIEW",
        "SPECIAL REPORT",
        "VIDEO", "FEATURE",
        "EXCLUSIVE VIDEO",
        "EDITORIAL", "ANALYSIS",
        "INVESTIGATION", "SPECIAL FEATURE"]

    words = headline.split()

    if words[0].upper() in headline_tags:
        words.pop(0)

    updated_headline = ' '.join(words)

    return updated_headline


def get_sentiment_score(article_text: str) -> float:
    """Returns the sentiment score using VADER"""
    vader = SentimentIntensityAnalyzer()
    sentiment_score = vader.polarity_scores(article_text)["compound"]

    return sentiment_score


if __name__ == "__main__":

    nltk.download('vader_lexicon')

    # Extract info and put in dataframe
    bbc_articles_df = extract_info_from_bbc_articles(BBC_UK_NEWS_XML_FILE_NAME)
    daily_mail_df = extract_info_from_daily_mail_articles(
        DAILY_MAIL_UK_NEWS_XML_FILE_NAME)

    list_of_news_dfs = [bbc_articles_df, daily_mail_df]

    for news_df in list_of_news_dfs:
        news_df['pubdate'] = news_df['pubdate'].apply(
            convert_pubdate_to_timestamp)
        news_df['title'] = news_df['title'].apply(
            remove_headline_tags)
        news_df['sentiment_score'] = news_df.apply(lambda row: get_sentiment_score(
            row['title'] + ' ' + row['description']), axis=1)

    # Save to CSV
    bbc_articles_df.to_csv(BBC_UK_NEWS_CSV_FILENAME)
    daily_mail_df.to_csv(DAILY_MAIL_UK_NEWS_CSV_FILENAME)
