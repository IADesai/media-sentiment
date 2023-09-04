"""This script converts the XML to dataframes and cleans them"""
from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd


def extract_info_from_bbc_articles(xml_file: str) -> pd.DataFrame:
    """Extracts the title, description, article URL and publication date
        from the XML file, saves it as a dataframe"""
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
    """Extracts the title, description, article URL and publication date
        from the XML file, saves it as a dataframe"""
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


def convert_pubdate_to_timestamp(pubdate: str):
    """Converts the publication date to a timestamp
        so it is ready for the database"""
    timestamp = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")

    return timestamp


def remove_headline_tags(headline: str):
    """Removes unnecessary tags from the headline"""
    headline_tags = [
        "BREAKING",
        "EXCLUSIVE",
        "UPDATE",
        "LIVE",
        "EXCLUSIVE INTERVIEW",
        "SPECIAL REPORT",
        "VIDEO",
        "FEATURE",
        "EXCLUSIVE VIDEO",
        "EDITORIAL",
        "ANALYSIS",
        "INVESTIGATION",
        "SPECIAL FEATURE"
    ]
    for tag in headline_tags:
        headline = headline.replace(tag, "")

    return headline


if __name__ == "__main__":

    # Extract info and put in dataframe
    bbc_articles_df = extract_info_from_bbc_articles("bbc_uk_news.xml")
    daily_mail_df = extract_info_from_daily_mail_articles(
        "daily_mail_uk_news.xml")

    # Convert the publication dates into timestamps
    bbc_articles_df['pubdate'] = bbc_articles_df['pubdate'].apply(
        convert_pubdate_to_timestamp)
    daily_mail_df['pubdate'] = daily_mail_df['pubdate'].apply(
        convert_pubdate_to_timestamp)

    # Remove headline tags
    bbc_articles_df['title'] = bbc_articles_df['title'].apply(
        remove_headline_tags)
    daily_mail_df['title'] = daily_mail_df['title'].apply(remove_headline_tags)

    # Save to CSV
    bbc_articles_df.to_csv("bbc_uk_news.csv")
    daily_mail_df.to_csv("daily_mail_uk_news.csv")
