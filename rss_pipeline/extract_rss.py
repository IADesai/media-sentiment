"""This script downloads the XML files from BBC and Daily Mail's RSS feed"""
import os


def download_bbc_uk_news_xml():
    """Downloads the latest UK news from the BBC website """
    os.system("curl http://feeds.bbci.co.uk/news/uk/rss.xml > bbc_uk_news.xml")


def download_daily_mail_uk_news_xml():
    """Downloads the latest news from the Daily Mail website """
    os.system(
        "curl https://www.dailymail.co.uk/home/index.rss > daily_mail_uk_news.xml")


if __name__ == "__main__":
    download_bbc_uk_news_xml()
    download_daily_mail_uk_news_xml()
