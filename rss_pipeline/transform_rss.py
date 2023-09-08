"""
This script converts the XML to dataframes and cleans them 
as well as applying sentiment analysis
"""
from datetime import datetime
import xml.etree.ElementTree as ET
import requests
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup


BBC_UK_NEWS_XML_FILE_NAME = "bbc_uk_news.xml"
DAILY_MAIL_UK_NEWS_XML_FILE_NAME = "daily_mail_uk_news.xml"

BBC_UK_NEWS_CSV_FILENAME = "bbc_uk_news.csv"
DAILY_MAIL_UK_NEWS_CSV_FILENAME = "daily_mail_uk_news.csv"


def extract_info_from_bbc_articles(xml_file: str) -> pd.DataFrame:
    """Extracts the title, description, article URL and publication date
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

    print("Info extracted from BBC News XML successfully")

    return pd.DataFrame(articles)


def extract_info_from_daily_mail_articles(xml_file: str) -> pd.DataFrame:
    """Extracts the title, description, article URL and publication date
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

    print("Info extracted from Daily Mail News XML successfully")
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


def get_bbc_full_article_text(url: str) -> str:
    """Uses BeautifulSoup to extract the full article from the URL"""
    html = requests.get(url)
    bsobj = BeautifulSoup(html.content, "lxml")

    # Average number of trailing tags that should be removed
    # from the BBC article (for processing)
    number_of_trailing_tags = 2

    bbc_jargon = ["This video can not be played"]

    article_contents_list = []
    for link in bsobj.find_all("p"):
        if "Paragraph" in str(link):
            article_contents_list.append(link.get_text())

    for element in bbc_jargon:
        while element in article_contents_list:
            article_contents_list.remove(element)

    if len(article_contents_list) >= number_of_trailing_tags:
        article_contents_list = article_contents_list[:-
                                                      number_of_trailing_tags]

    if len(article_contents_list) != 0:
        return " ".join(article_contents_list)

    return ""


def get_daily_mail_full_article_text(url: str) -> str:
    """Uses BeautifulSoup to extract the full article from the URL"""
    response = requests.get(url)

    html = BeautifulSoup(response.text, 'html.parser')

    # Find the tag with the article body
    article_body = html.find('div', itemprop='articleBody')

    if article_body:
        article_content = article_body.get_text()
        return article_content
    return ""


def get_sentiment_score(article_text: str, sentiment_analyser: SentimentIntensityAnalyzer) -> float:
    """Returns the sentiment score using VADER"""
    sentiment_score = sentiment_analyser.polarity_scores(article_text)[
        "compound"]

    return sentiment_score


def transform_bbc_xml_file(bbc_xml_file: str, sentiment_analyser: SentimentIntensityAnalyzer) -> pd.DataFrame:
    """Converts the BBC XML file to a dataframe and cleans it"""
    bbc_articles_df = extract_info_from_bbc_articles(f"/tmp/{bbc_xml_file}")

    bbc_articles_df['pubdate'] = bbc_articles_df['pubdate'].apply(
        convert_pubdate_to_timestamp)
    bbc_articles_df['title'] = bbc_articles_df['title'].apply(
        remove_headline_tags)

    print("Calculating the sentiment score for all of the BBC articles...")

    bbc_articles_df['sentiment_score'] = bbc_articles_df.apply(lambda row: get_sentiment_score(
        row['title'] + ' ' + row['description'] + ' ' +
        get_bbc_full_article_text(row['url']), sentiment_analyser), axis=1)

    print("BBC News XML file has been fully processed")

    return bbc_articles_df


def transform_daily_mail_xml_file(daily_mail_xml_file: str, sentiment_analyser: SentimentIntensityAnalyzer) -> pd.DataFrame:
    """Converts the Daily Mail XML file to a dataframe and cleans it"""
    daily_mail_articles_df = extract_info_from_daily_mail_articles(
        f"/tmp/{daily_mail_xml_file}")

    daily_mail_articles_df['pubdate'] = daily_mail_articles_df['pubdate'].apply(
        convert_pubdate_to_timestamp)
    daily_mail_articles_df['title'] = daily_mail_articles_df['title'].apply(
        remove_headline_tags)

    print("Calculating the sentiment score for all of the Daily Mail articles...")

    daily_mail_articles_df['sentiment_score'] = daily_mail_articles_df.apply(lambda row: get_sentiment_score(
        row['title'] + ' ' + row['description'] + ' ' +
        get_daily_mail_full_article_text(row['url']), sentiment_analyser), axis=1)

    print("Daily Mail News XML file has been fully processed")

    return daily_mail_articles_df


if __name__ == "__main__":

    nltk.download('vader_lexicon')

    vader = SentimentIntensityAnalyzer(lexicon_file="vader_lexicon.txt")

    bbc_articles_df = transform_bbc_xml_file(BBC_UK_NEWS_XML_FILE_NAME, vader)
    daily_mail_articles_df = transform_daily_mail_xml_file(
        DAILY_MAIL_UK_NEWS_XML_FILE_NAME, vader)

    daily_mail_articles_df.to_csv(DAILY_MAIL_UK_NEWS_CSV_FILENAME)
    bbc_articles_df.to_csv(BBC_UK_NEWS_CSV_FILENAME)
