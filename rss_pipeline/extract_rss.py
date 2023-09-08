"""This script downloads the XML files from BBC and Daily Mail's RSS feed"""

import requests
from requests.exceptions import RequestException
import os

BBC_UK_NEWS_RSS_LINK = "http://feeds.bbci.co.uk/news/uk/rss.xml"
DAILY_MAIL_UK_NEWS_RSS_LINK = "https://www.dailymail.co.uk/home/index.rss"

BBC_UK_NEWS_XML_FILE_NAME = "bbc_uk_news.xml"
DAILY_MAIL_UK_NEWS_XML_FILE_NAME = "daily_mail_uk_news.xml"


def download_bbc_uk_news_xml(bbc_uk_news_rss_link: str, bbc_uk_news_xml_file_name: str) -> None:
    """Downloads the latest UK news from the BBC website """
    try:
        response = requests.get(bbc_uk_news_rss_link, timeout=10)
        if response.status_code == 200:
            with open(f"/tmp/{bbc_uk_news_xml_file_name}", "wb") as file:
                file.write(response.content)
            print("BBC UK news XML downloaded successfully.")
        else:
            print(
                f"Failed to download BBC UK news XML. Status code: {response.status_code}")
    except RequestException as request_exc:
        print(f"An error occurred: {str(request_exc)}")


def download_daily_mail_uk_news_xml(daily_mail_uk_news_rss_link: str, daily_mail_uk_news_xml_file_name: str) -> None:
    """Downloads the latest news from the Daily Mail website """
    try:
        response = requests.get(daily_mail_uk_news_rss_link, timeout=10)
        if response.status_code == 200:
            with open(f"/tmp/{daily_mail_uk_news_xml_file_name}", "wb") as file:
                file.write(response.content)
            print("Daily Mail UK news XML downloaded successfully.")
        else:
            print(
                f"Failed to download Daily Mail UK news XML. Status code: {response.status_code}")
    except RequestException as request_exc:
        print(f"An error occurred: {str(request_exc)}")


if __name__ == "__main__":
    download_bbc_uk_news_xml(BBC_UK_NEWS_RSS_LINK, BBC_UK_NEWS_XML_FILE_NAME)
    download_daily_mail_uk_news_xml(
        DAILY_MAIL_UK_NEWS_RSS_LINK, DAILY_MAIL_UK_NEWS_XML_FILE_NAME)
