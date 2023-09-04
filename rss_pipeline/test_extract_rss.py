# pylint: skip-file
from unittest.mock import patch
from extract_rss import download_bbc_uk_news_xml, download_daily_mail_uk_news_xml


@patch('os.system')
def test_download_bbc_uk_news_xml(mock_os_system):
    download_bbc_uk_news_xml()

    mock_os_system.assert_called_once_with(
        "curl http://feeds.bbci.co.uk/news/uk/rss.xml > bbc_uk_news.xml")


@patch('os.system')
def test_download_daily_mail_uk_news_xml(mock_os_system):
    download_daily_mail_uk_news_xml()

    mock_os_system.assert_called_once_with(
        "curl https://www.dailymail.co.uk/home/index.rss > daily_mail_uk_news.xml")
