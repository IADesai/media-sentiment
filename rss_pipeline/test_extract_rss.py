"""Tests the extract RRS script"""

from unittest.mock import patch, mock_open
from extract_rss import download_bbc_uk_news_xml, download_daily_mail_uk_news_xml


BBC_UK_NEWS_RSS_LINK = "http://feeds.bbci.co.uk/news/uk/rss.xml"
DAILY_MAIL_UK_NEWS_RSS_LINK = "https://www.dailymail.co.uk/home/index.rss"

BBC_UK_NEWS_XML_FILE_NAME = "bbc_uk_news.xml"
DAILY_MAIL_UK_NEWS_XML_FILE_NAME = "daily_mail_uk_news.xml"


@patch("builtins.open", new_callable=mock_open, create=True)
def test_download_bbc_uk_news_xml(mock_file_open):

    with patch("requests.get") as mock_get:
        fake_response = mock_get.return_value
        fake_response.status_code = 200
        fake_response.content = b"Fake XML Content"

        download_bbc_uk_news_xml(BBC_UK_NEWS_RSS_LINK,
                                 BBC_UK_NEWS_XML_FILE_NAME)

        mock_get.assert_called_once_with(BBC_UK_NEWS_RSS_LINK, timeout=10)
        mock_file_open.assert_called_once_with(BBC_UK_NEWS_XML_FILE_NAME, "wb")
        mock_file_open().write.assert_called_once_with(b"Fake XML Content")


@patch("builtins.open", new_callable=mock_open, create=True)
def test_download_daily_mail_uk_news_xml(mock_file_open):

    with patch("requests.get") as mock_get:
        fake_response = mock_get.return_value
        fake_response.status_code = 200
        fake_response.content = b"Fake XML Content"

        download_daily_mail_uk_news_xml(
            DAILY_MAIL_UK_NEWS_RSS_LINK, DAILY_MAIL_UK_NEWS_XML_FILE_NAME)

        mock_get.assert_called_once_with(
            DAILY_MAIL_UK_NEWS_RSS_LINK, timeout=10)
        mock_file_open.assert_called_once_with(
            DAILY_MAIL_UK_NEWS_XML_FILE_NAME, "wb")
        mock_file_open().write.assert_called_once_with(b"Fake XML Content")
